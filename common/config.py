# vim set fileencoding=utf-8
"""配置管理模块"""
from configparser import RawConfigParser
from functools import lru_cache

from pydantic import BaseSettings, validator

from common.qt_logging import frame_log
from common.utils import MultiModeBase



class ConfigManager(MultiModeBase):
    _HANDLERS = []

    def get(self, section, *keys, default=None, required=False, **kwargs):
        raise NotImplementedError

    def iter_keys(self, *keys):
        """获取配置文件空间中*keys下所有子key"""
        raise NotImplementedError

    @classmethod
    def register_config_handler(cls, handler, mode_name=None):
        """其它模块可注册初始化函数，在Config初始化之后调用，传入cls对象

        参考logger.config.fileConfig
        """
        mode_name = mode_name or cls.NAME_DEFAULT
        if handler not in cls._HANDLERS:
            cls._HANDLERS.append(handler)
            if cls(mode_name):
                # 已配置
                handler(cls(mode_name))

    def initialize(self, *args, **kwargs):
        for handler in self._HANDLERS:
            handler(self)


class INIConfigManager(ConfigManager):
    """ini文件初始化管理

    仅支持两级key: (section, option)
    无option提供时，给出option dict
    """

    def initialize(self, conf_file, *args, **kwargs):
        conf = RawConfigParser()
        conf.read(conf_file)
        self.conf = conf  # pylint: disable=attribute-defined-outside-init
        super().initialize(*args, **kwargs)

    def get(self, section, *keys, required=False, encode=lambda x: x, **kwargs):
        conf = None
        if len(keys) == 0:
            if self.conf.has_section(section):
                conf = dict(self.conf.items(section))
        elif len(keys) == 1:
            if self.conf.has_option(section, keys[0]):
                conf = self.conf.get(section, keys[0])
        if conf is None:
            if required:
                raise RuntimeError(
                    f"Config:({section}|{keys}) missing(required)")
            conf = kwargs.get('default', None)
            return conf
        return encode(conf)

    def iter_keys(self, *keys):
        if not keys:
            return self.conf.sections()
        if len(keys) == 1:
            return self.conf.options(keys[0])
        return []


class CommonConfig(BaseSettings):
    conf: str = "/Users/an/code/quantex-code/conf/dev.conf"
    run_env: str = None

    @validator("conf", pre=False)
    def validate_conf(cls, conf):
        if not ConfigManager() or isinstance(conf, str):
            ConfigManager.register(INIConfigManager, conf_file=conf)
            conf = ConfigManager()
        return conf

    @validator("run_env", pre=True)
    def validate_run_env(cls, run_env, values):
        if not run_env:
            conf_ins = values["conf"]
            run_env = conf_ins.get('app_env', 'run_env', required=True)
        return run_env


def get_config(section, *keys, **kwargs):
    return ConfigManager().get(section, *keys, **kwargs)


def get_settings(settings):
    """抽象工厂配置实例"""
    _instance = None

    @lru_cache
    def create_config():
        instance = settings()
        frame_log.info(
            f"Read <{settings.__name__}> configuration from environment {instance.run_env}"
        )
        _instance = instance
        return instance

    if _instance is None:
        return create_config()
    return _instance


