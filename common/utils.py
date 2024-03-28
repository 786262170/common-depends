# vim set fileencoding=utf-8
"""utils module"""
import copy
import datetime
import functools
import importlib
import inspect
import json
import random
import time
import typing
from collections import OrderedDict
from typing import List

import pydantic

try:
    import qtlib
except ImportError:
    qtlib = None


class MultiModeBase(object):
    """
    A.register(name, support_type, init_arguments)
    A(name), A()
    """

    NAME_DEFAULT = "default"

    def __new__(cls, name=NAME_DEFAULT):
        instance_map = getattr(cls, "_INSTANCE_MAP", {})
        return instance_map.get(name)

    @classmethod
    def register(cls, mode_impl, mode_name=NAME_DEFAULT, *args, **kwargs):
        instance_map = getattr(cls, "_INSTANCE_MAP", None)
        if not instance_map:
            instance_map = {}
            setattr(cls, "_INSTANCE_MAP", instance_map)
        if mode_name in instance_map:
            return instance_map[mode_name]
            # raise RuntimeError("%s register before" % mode_name)
        if not issubclass(mode_impl, cls):
            raise RuntimeError("%s Need subclass of %s" % (mode_impl, cls))
        instance = super(MultiModeBase, cls).__new__(mode_impl)
        instance.initialize(*args, **kwargs)
        instance_map[mode_name] = instance

    def initialize(self, *args, **kwargs):
        """初始化操作，替代__init__"""


# --- 通用 ---


def base_mutable_hash(*args, **kwargs):
    """定制化hash策略，支持对mutable(可变)基础类型进行hash"""

    def __hash(value):
        if isinstance(value, pydantic.BaseModel):
            value = value.dict()
        if isinstance(value, (list, set, tuple)):
            return hash(tuple([__hash(item) for item in value]))
        elif isinstance(value, dict):
            return hash(
                tuple([(key, __hash(value)) for key, value in value.items()]))
        else:
            return hash(value)

    return hash(tuple([__hash(args), __hash(kwargs)]))


class ExpandJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        from decimal import Decimal

        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)


def dict_trip(data: dict, trip=None):
    for key, val in list(data.items()):
        if val == trip:
            del data[key]
    return data


def get_random_cid():
    """随机选择8位数字"""
    return "".join([random.choice("0123456789") for _ in range(8)])


def copy_value(
    dst_record,
    src_record,
    exclude_field: List[str] = None,
    increment: bool = False,
    exclude_none: bool = True,
):
    """将src_record中的属性值按条件拷贝到dst_record
    :param dst_record: 目标实例
    :param src_record: 源实例
    :param exclude_field: 需要排除的属性
    :param increment: 是否将src_record中多于dst_record的属性进行拷贝
    :param exclude_none: none值是否排除
    :return: None
    """
    if exclude_field is None:
        exclude_field = []
    if src_record is None or dst_record is None:
        return
    for key in dst_record.dict():
        val = getattr(src_record, key, None)
        if key in exclude_field:
            continue
        if val is None and exclude_none:
            continue
        if isinstance(val, float):
            import numpy as np

            if np.isnan(val) or np.isinf(val):
                continue
        if increment:
            setattr(dst_record, key, val)
        else:
            if hasattr(src_record, key):
                setattr(dst_record, key, copy.deepcopy(val))


def import_cls(module_cls_path: str,
               second: int = 3,
               package=None) -> typing.Callable:
    """动态导入类
    :param module_cls_path: 绝对导入路径，例turing_models.instruments.base
    :param second: 导入异常重试时间, 默认3s
    :param package: 相对路径导包时辅助参数，module_cls_path需以.开头
    :return:类引用
    """
    module = None
    if module_cls_path.startswith("."):
        if not package:
            raise RuntimeError("相对路径传入时，package不能为空")
    module_name, clsname = module_cls_path.rsplit(".", 1)
    start_time = int(time.time())
    while int(time.time()) - start_time <= second:
        try:
            module = importlib.import_module(module_name, package)
            importlib.reload(module)
            break
        except (ModuleNotFoundError, ImportError):
            time.sleep(0.5)
            continue
    else:
        if module is None:
            raise ImportError(
                f"Module cls path {module_cls_path} not found, please checking..."
            )
    if not hasattr(module, clsname):
        raise AttributeError(
            f"Attributes: [{clsname}] that do not exist in module:[{module_name}]"
        )
    cls = getattr(module, clsname)
    return cls


class ReflectHelper:
    """反射执行帮助类"""

    @staticmethod
    def get_reflect_module(module_path: str, package=None):
        """获取反射模块
        :param module_path:模块名称
        :param package:模块包
        :return: 模块的引用
        """
        if module_path.startswith("."):
            if not package:
                raise RuntimeError(f"模块路径以相对路径方式传入时，包路径需指定:package:{package}")
        module = importlib.import_module(module_path, package=package)
        importlib.reload(module)
        return module

    @classmethod
    def get_reflect_cls(cls, module_path, clsaname):
        """获取反射类
        :param module_path:模块包文件路径
        :param clsaname:需要导入的类名称
        :return: 导入类引用
        """
        module = cls.get_reflect_module(module_path)
        if not isinstance(module, object):
            raise ModuleNotFoundError(f"动态导入失败，检测路径：{module_path}")
        if not hasattr(module, clsaname):
            raise AttributeError(f"不存在的类:{clsaname}")
        return getattr(module, clsaname)

    @classmethod
    def get_reflect_func(cls,
                         module_path,
                         clsaname,
                         fun_name,
                         init_args: typing.Iterable = None,
                         init_kwargs: dict = None):
        """获取反射函数引用
        :param module_path: 模块包文件路径
        :param clsaname: 需要导入的类名称
        :param fun_name: 需要导入的函数名称
        :param init_args: 初始化位置参数
        :param init_kwargs: 初始化关键字参数
        :return: 函数引用
        """
        cls_meta = cls.get_reflect_cls(module_path, clsaname)
        if init_args is not None:
            cls_meta = functools.partial(cls_meta, *init_args)
        if init_kwargs is not None:
            cls_meta = functools.partial(cls_meta, *init_kwargs)
        cls_instance = cls_meta()
        if not hasattr(cls_instance, fun_name):
            raise AttributeError(f"不存在的函数:{fun_name}")
        return getattr(cls_instance, fun_name)

    @staticmethod
    def create_instance(module_class_path, *args, **kwargs):
        """动态创建类的实例。
        ("module_meta,class_meta: ", type(module_meta),module_meta, type(class_meta),class_meta)
        [Parameter]
        module_class_path - 类的全名（包括模块名）
        *args - 类构造器所需要的参数(list)
        *kwargs - 类构造器所需要的参数(dict)
        [Return]
        动态创建的类的实例
        [Example]
        module_class_path = 'knightmade.logging.Logger'
        logger = Activator.create_instance(module_class_path, 'logname')
        """
        (module_name, class_name) = module_class_path.rsplit('.', 1) \
            if '.' in module_class_path \
            else (module_class_path, '')
        module_meta = __import__(module_name, globals(), locals(),
                                 [class_name])
        ReflectHelper.module_reload(module_meta)
        if class_name:
            class_meta = getattr(module_meta, class_name)
        else:
            class_meta = module_meta
        if isinstance(class_meta, type):
            class_meta = class_meta(*args, **kwargs)
        else:
            ReflectHelper.module_reload(class_meta)

        return class_meta

    @staticmethod
    def module_reload(module_name):
        try:
            importlib.reload(module_name)
        except:
            pass


class BaseEnum(object):
    _values = None
    _attrs = None

    @classmethod
    def values(cls):
        if cls._values is not None:
            return cls._values
        values = []
        attrs = []
        for item in dir(cls):
            if cls.is_enum_attr(item):
                values.append(getattr(cls, item))
                attrs.append(item)
        cls._values = values
        cls._attrs = attrs
        return values

    @classmethod
    def attrs(cls):
        if cls._attrs is None:
            cls.values()
        return cls._attrs

    @classmethod
    def is_enum_attr(cls, attr):
        """不是以'_'开头的，非callble属性"""
        if attr.startswith("_"):
            return False
        obj = getattr(cls, attr)
        return not callable(obj)


def asyncio_cache_funcs(func=None, max_size=128, expired=300):
    """基于装饰器设计模型实现本地缓存（分布式不考虑）支持异步

    :param func: 需要缓存的函数
    :param max_size: 缓存大小
    :param expired: 过期时间
    """
    if func is None:
        return functools.partial(asyncio_cache_funcs,
                                 max_size=max_size,
                                 expired=expired)
    assert isinstance(max_size, int) and max_size > 0
    cache = OrderedDict()

    @functools.wraps(func)
    async def wrap_fn(*args, **kwargs):
        from common.qt_logging import frame_log

        # 支持self实例方法，实例对象hash值不唯一、动态剔除
        if isinstance(args[0], object):
            key = base_mutable_hash(*args[1:], **kwargs)
        else:
            key = base_mutable_hash(*args, **kwargs)
        frame_log.info("cache search key:{}", key)
        if key in cache:
            frame_log.debug("cache key find:{}", cache[key])
            if int(time.time()) - cache[key]['stamp'] < expired:
                return cache[key]['data']
        frame_log.info("load cache key")
        if inspect.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        if len(cache) == max_size:
            # pop item
            cache.pop(list(cache.keys())[0])
        frame_log.info("load cache key result:{}", result)
        cache[key] = dict(data=result, stamp=int(time.time()))
        return result

    def clear():
        cache.clear()

    def data():
        return cache

    wrap_fn.clear = clear
    wrap_fn.data = data
    return wrap_fn


def cache_funcs(func=None, max_size=128, expired=300):
    """基于装饰器设计模型实现本地缓存（分布式不考虑）

    :param func: 需要缓存的函数
    :param max_size: 缓存大小
    :param expired: 过期时间
    """
    if func is None:
        return functools.partial(cache_funcs,
                                 max_size=max_size,
                                 expired=expired)
    assert isinstance(max_size, int) and max_size > 0
    cache = OrderedDict()

    @functools.wraps(func)
    def wrap_fn(*args, **kwargs):
        from common.qt_logging import frame_log

        # 支持self实例方法，实例对象hash值不唯一、动态剔除
        if isinstance(args[0], object):
            key = base_mutable_hash(*args[1:], **kwargs)
        else:
            key = base_mutable_hash(*args, **kwargs)
        frame_log.info("cache search key:{}", key)
        if key in cache:
            frame_log.debug("cache key find:{}", cache[key])
            if int(time.time()) - cache[key]['stamp'] < expired:
                return cache[key]['data']
        frame_log.info("load cache key")
        result = func(*args, **kwargs)
        if len(cache) == max_size:
            # pop item
            cache.pop(list(cache.keys())[0])
        frame_log.info("load cache key result:{}", result)
        cache[key] = dict(data=result, stamp=int(time.time()))
        return result

    def clear():
        cache.clear()

    def data():
        return cache

    wrap_fn.clear = clear
    wrap_fn.data = data
    return wrap_fn


def inverted_dict(data: dict):
    """倒转字典key value映射
    value为不可变类型
    """
    return dict(zip(data.values(), data.keys()))


