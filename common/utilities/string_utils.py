# coding=utf8
"""字符处理"""
import re
from typing import Union


def utf8fmt(data, codes=None):
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    elif isinstance(data, list):
        data = [utf8fmt(item) for item in data]
    elif isinstance(data, dict):
        data = {utf8fmt(key): utf8fmt(value) for key, value in data.items()}

    if codes and isinstance(data, str):
        value = None
        for code in codes:
            try:
                value = data.decode(code).encode("utf-8")
            except UnicodeError:
                continue
            break
        if not value:
            raise TypeError("can not find coder for %r in %s" % (data, codes))
        data = value

    return data


def get_tbname_from_sql(sql_string):
    """sql中获取表名"""
    # 获取表名
    table_name = None
    # 去掉换行
    sql = sql_string.replace("\n", " ")
    # 多个空格替换成一个空格
    sql = re.sub(" +", " ", sql)
    # 获取表名
    obj = re.match(".* FROM ([^\s]*)\s?", sql, re.I)
    if obj:
        table_name = obj.group(1)
    return table_name


def pascal_case_to_snake_case(camel_case: str):
    """大驼峰（帕斯卡）转蛇形"""
    snake_case = re.sub(r"(?P<key>[A-Z]+)", r"_\g<key>", camel_case)
    return snake_case.lower().strip("_").replace(" ", "")


def snake_case_to_pascal_case(snake_case: str):
    """蛇形转大驼峰（帕斯卡）"""
    words = snake_case.split("_")
    return "".join(word.title() for word in words)


def to_sql_in_str(d: Union[str, list]):
    """list or str convert to sql string"""
    d = [d] if isinstance(d, str) else d
    return "({})".format((",".join([f"'{k}'" for k in d])))
