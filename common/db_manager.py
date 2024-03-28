# coding=utf-8
# vim set fileencoding=utf-8
"""DB管理模块"""

import datetime
import inspect
import json
import time
import typing
from collections import namedtuple
from contextlib import contextmanager
from typing import Union
from urllib.parse import quote_plus

import pandas
import pandas as pd
import sqlalchemy.orm
from sqlalchemy import create_engine, inspect as sql_inspect
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, load_only, Query
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import insert

from qt_quant.common import config
from qt_quant.common.qt_logging import frame_log

PGDialect._get_server_version_info = lambda *args: (9, 2)  # 解决引入pg插件后版本强制检测的问题

DBCfg = namedtuple(
    "DBCfg", ["engine", "db_name", "user", "passwd", "host", "port", "charset", "engine_para"]
)

PgDBCfg = namedtuple(
    "PgDBCfg", ["engine", "db_name", "user", "passwd", "host", "port", "engine_para"]
)
Base = declarative_base()


class DBManager(object):
    _INSTANCES = {}
    MYSQL_PREFIX = "mysql_"
    POSTGRESQL_PREFIX = "pg_"

    def __init__(self, name, db_cfg):
        create_eng_str = (
            "{engine}://{user}:{passwd}@{host}:{port}/{db}".format(
                engine=db_cfg.engine,
                user=db_cfg.user,
                passwd=quote_plus(db_cfg.passwd),  # 兼容sqlalchemy用法，防止密码中带@
                host=db_cfg.host,
                port=db_cfg.port,
                db=db_cfg.db_name,
            )
        )
        if name.startswith(self.MYSQL_PREFIX):
            create_eng_str += "?charset={}".format(db_cfg.charset)
        engine_paras = {
            "pool_size": 512,
            "max_overflow": 512,
            "pool_recycle": 3600,
            "echo": False,  # 是否开启sql日志
            "case_sensitive": False  # 忽略列大小写
        }
        engine_paras.update(db_cfg.engine_para)
        self.engine = create_engine(create_eng_str, **engine_paras)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.name = name

    @staticmethod
    def get_instance(name):
        if name not in DBManager._INSTANCES:
            raise RuntimeError(
                f"name:{name} need register first({DBManager._INSTANCES})"
            )
        return DBManager._INSTANCES.get(name)

    @staticmethod
    def register(name, db_cfg):
        assert isinstance(db_cfg, (DBCfg, PgDBCfg))
        if name in DBManager._INSTANCES:
            frame_log.info("name:{} had registed before", name)
        DBManager._INSTANCES[name] = DBManager(name, db_cfg)

    def get_session(self):
        return self.session()

    @contextmanager
    def session_open(self):
        """Provide session context manager"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            error = str(e.__cause__)
            session.rollback()
            raise RuntimeError(error) from e
        finally:
            session.close()


def session_decorate(func):
    def _wrapper(*args, **kwargs):
        call_args = inspect.getcallargs(func, *args, **kwargs)
        session = call_args.get("session")
        if isinstance(session, sqlalchemy.orm.session.Session):
            return func(*args, **kwargs)
        if isinstance(session, str):
            db_instance = DBManager.get_instance(session)
        else:
            raise RuntimeError(f"unsupport session:{session}|{type(session)}")
        with db_instance.session_open() as session:
            call_args["session"] = session
            arg_spec = inspect.signature(func).parameters
            vargs = []
            kws = {}
            for name, param in arg_spec.items():
                if param.kind != inspect.Parameter.VAR_KEYWORD:
                    vargs.append(call_args[name])
                elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                    kws.setdefault(name, call_args.get(name, param))
            return func(*vargs, **kws)

    return _wrapper


def query_record(cls, session, filters=None, load_attrs=None):
    """query filter wrapper"""
    query = session.query(cls)
    if filters:
        query = query.filter(*filters)
    if load_attrs:
        query = query.options(load_only(*load_attrs))
    return query.all()


class DeclarMixin(object):
    """Mixin with declarative base class"""

    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
        "mysql_collate": "utf8_unicode_ci",
    }

    def as_dict(self, jsonable=False):
        insp = sql_inspect(self)
        data = {}
        for item in insp.attrs:
            value = item.value
            if jsonable:
                if isinstance(value, datetime.datetime):
                    if round(value.microsecond * 10 ** -6):
                        value += datetime.timedelta(0, 1)
                    value = int(time.mktime(value.timetuple()))
            data[str(item.key)] = value
        return data

    @session_decorate
    def add(self, session=None):
        frame_log.debug("session:{} add record:{}", session, self)
        session.add(self)

    @session_decorate
    def put(self, session=None, replace_dict=None):
        frame_log.debug("session:{} put record:{}", session, self)
        replace_dict = replace_dict or {}
        for key in replace_dict:
            if hasattr(self, key):
                if getattr(self, key) != replace_dict[key]:
                    setattr(self, key, replace_dict[key])

    @session_decorate
    def merge(self, session=None):
        frame_log.debug("session:{} merge record:{}", session, self)
        session.merge(self)

    @classmethod
    @session_decorate
    def batch_insert(cls, values, prefixes=None, session=None):
        insert_stmt = insert(cls.__table__, values=values, prefixes=prefixes)
        return session.execute(insert_stmt)

    @classmethod
    @session_decorate
    def query(cls, filters, expunge=True, load_attrs=None, session="default"):
        """query object filter by kwargs"""
        results = query_record(cls, session, filters, load_attrs)
        if expunge:
            for result in results:
                session.expunge(result)
        return results

    @classmethod
    @session_decorate
    def query_one(cls, filters, expunge=True, load_attrs=None, session="default"):
        result = cls.query(filters, expunge, load_attrs, session=session)
        if result:
            if len(result) != 1:
                raise RuntimeError(f"multiple object found:{len(result)}")
            result = result[0]
        else:
            result = None
        return result

    @classmethod
    @session_decorate
    def create_table(cls, check_first=True, session=None):
        table = cls.__table__
        table.create(session.bind, check_first)


# --- df sql helper ---

@session_decorate
def pd_to_sql(df: pandas.DataFrame, tb_name: str = None,
              tb: Union[Base, DeclarMixin] = None,
              session: Union[str, Session] = "default",
              upper_or_lower: Union['str'] = "upper",
              **kwargs):
    """dataframe插入数据库"""
    name = tb.__tablename__ if tb else tb_name
    if upper_or_lower == "upper":
        df.columns = map(str.upper, df.columns)
        name = name.upper()
    else:
        df.columns = map(str.lower, df.columns)
        name = name.lower()
    frame_log.info("insert to sql for tb_name:{}", name)
    df.to_sql(name, session.bind, if_exists="replace",
              index=False, method="multi", **kwargs)
    frame_log.info("inserting succeed, num:{}", len(df))


@session_decorate
def pd_read_sql(sql: str | Query, session: Union[str, Session] = "default",
                decoder: typing.Callable = None, **kwargs) -> pd.DataFrame:
    """基于pandas的sql查询
    支持事务回滚和orm查询操作

    :param sql: 支持str原生sql语句和sqlalchemy.Query对象实体（需兼容Orm语法，参考：https://docs.sqlalchemy.org/）
    :param session:连接对象，默认session='default',根据conf配置选项调整
    :param decoder:输出格式化函数，对查询结果进一步处理
    :param kwargs:pandas.read_sql扩展参数
                 >>> pandas.read_sql()
    :return:
    """
    # 支持sqlalchemy.Query对象语句
    if isinstance(sql, Query):
        sql = sql.statement
        dialect = session.bind.dialect
        sql = sql.compile(
            dialect=dialect, compile_kwargs={
                "literal_binds": True})  # 支持对于搜索条件值的格式化处理
        # 解决关于psycopg2驱动对于大写列、表名""查找失败的问题
        if dialect.driver == "psycopg2":
            sql = str(sql).replace('"', '')
    frame_log.info("Reading sql to df: '{}'", sql)
    data = pandas.read_sql(sql=sql, con=session.bind, **kwargs)
    if decoder:
        data = decoder(data)
    return data


def db_config_handle(conf):
    """注册DB配置初始化"""
    mysql_fix = "mysql_"
    pg_fix = "pg_"

    for section in conf.iter_keys():

        if section.startswith(mysql_fix):
            # MySQL
            db_name = conf.get(section, "db_name")
            engine = conf.get(section, "engine", default="mysql+pymysql")
            user = conf.get(section, "user")
            passwd = conf.get(section, "passwd")
            host = conf.get(section, "host")
            port = conf.get(section, "port", default=3306, encode=int)
            charset = conf.get(section, "charset", default="utf8")
            extra = set(conf.iter_keys(section)) - set(DBCfg._fields)
            engine_para = dict([(name, conf.get(section, name)) for name in extra])
            db_cfg = DBCfg(engine, db_name, user, passwd, host, port, charset, engine_para)
            DBManager.register(section[len(mysql_fix):], db_cfg)
        elif section.startswith(pg_fix):
            # PostgreSQL
            engine = conf.get(section, "engine", default="postgresql+psycopg2")
            db_name = conf.get(section, "db_name")
            user = conf.get(section, "user")
            passwd = conf.get(section, "passwd")
            host = conf.get(section, "host")
            port = conf.get(section, "port", default=5432, encode=int)
            extra = set(conf.iter_keys(section)) - set(DBCfg._fields)
            engine_para = dict([(name, conf.get(section, name)) for name in extra])
            if "connect_args" in engine_para:
                engine_para["connect_args"] = json.loads(engine_para["connect_args"])
            db_cfg = PgDBCfg(engine, db_name, user, passwd, host, port, engine_para)
            DBManager.register(section[len(pg_fix):], db_cfg)


config.CommonConfig()
config.ConfigManager.register_config_handler(db_config_handle)
