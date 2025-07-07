import os
import sys
from loguru import logger
from biography_agent.infra.settings import settings


def setup_logger(enqueue: bool = False):
    """设置日志配置"""
    # 移除所有现有的处理器
    logger.remove()

    # 获取配置
    debug = settings.get("logging", "debug", fallback=False)
    log_level = settings.get("logging", "level", fallback="INFO")

    # 根据环境设置格式
    env = os.getenv("ENV", "dev")
    if env == "prod" and not debug:
        # 生产环境：简洁格式
        format_str = "{time:YYYY-MM-DD HH:mm:ss}|{level}|{file}:{line}|{message}"
        colorize = False
    else:
        # 开发环境或调试模式：详细格式，带颜色
        format_str = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green>|"
            "<level>{level.name}</level>|"
            "<cyan>{file}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>|"
            "<level>{message}</level>"
        )
        colorize = True

    # 多进程环境下的处理
    if enqueue:
        # 使用队列模式（推荐）
        logger.add(
            sys.stdout,
            format=format_str,
            colorize=colorize,
            level=log_level,
            enqueue=True,  # 多进程安全
            backtrace=True,
            diagnose=True,
        )
    else:
        # 非队列模式：添加进程ID到格式中，帮助区分日志来源
        process_info = f"[PID:{os.getpid()}]"
        if env == "prod" and not debug:
            format_str = f"{process_info}|{{time:YYYY-MM-DD HH:mm:ss}}|{{level}}|{{file}}:{{line}}|{{message}}"
        else:
            format_str = (
                f"{process_info}|<green>{{time:YYYY-MM-DD HH:mm:ss}}</green>|"
                "<level>{level.name}</level>|"
                "<cyan>{file}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>|"
                "<level>{message}</level>"
            )
        
        logger.add(
            sys.stdout,
            format=format_str,
            colorize=colorize,
            level=log_level,
            enqueue=False,  # 非队列模式
            backtrace=True,
            diagnose=True,
        )


# 自动初始化（开发环境）
if os.getenv("ENV", "dev") != "prod":
    setup_logger()

# 导出 logger 实例
__all__ = ["logger", "setup_logger"]
