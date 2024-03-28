# vim set fileencoding=utf-8
"""logging module"""
import logging
import logging.config
import sys

from loguru import logger

from common.request_context import Request as RequestContext
from common.utils import get_random_cid


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth,
                   exception=record.exc_info).log(level, record.getMessage())


def record_filter(record):
    """logger add request id"""
    extra = record["extra"]
    if not hasattr(extra, "request"):
        if not RequestContext.get():
            RequestContext.set(get_random_cid())
        extra["request"] = RequestContext.get()
    record["extra"] = extra
    return record


LOG_CONFIG = {
    "sink":
    sys.stderr,  # 默认处理程序会将消息写入sys.stderr
    "level":
    "INFO",  # 更改日志级别
    "format":
    "<level>{level}</level> | <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {process}|"
    " {thread}| {extra[request]} | <cyan>{module}</cyan> | <cyan>{function}</cyan> | "
    "<cyan>{name}</cyan> | <cyan>{line}</cyan> | <level>{message}</level>",
    "enqueue":
    False,
    "filter":
    record_filter,
    "diagnose":
    False  # 记录Exception时，Loguru将显示现有变量的值
}


class QtLogger:
    __instance = {}
    __call_flag = True

    def __new__(cls, *args, **kwargs):
        if cls not in cls.__instance:
            cls.__instance[cls] = super().__new__(cls, *args, **kwargs)
            return cls.__instance[cls]
        return cls.__instance[cls]

    def get_logger(self):
        if self.__call_flag:
            logger.remove()  # 避免重复打印
            logger.add(**LOG_CONFIG)
            self.__call_flag = False
        return logger


frame_log = QtLogger().get_logger()
# from common.config import
# logging.basicConfig()
# logging.config.fileConfig()
# frame_log = logging.getLogger("frame_log")
# app_log = logging.getLogger("app_log")
# logger.configure(
#     handlers=[
#         dict(sink=sys.stderr, format="[{time}] {message}"),
#         dict(sink="file.log", enqueue=True, serialize=True),
#     ],
#     levels=[dict(name="NEW", no=13, icon="¤", color="")],
#     extra={"common_to_all": "default"},
#     patcher=lambda record: record["extra"].update(some_value=42),
#     activation=[("my_module.secret", False), ("another_library.module", True)],
# )
