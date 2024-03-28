# coding=utf8
"""
@Author: Changye Yang
@Date: 2023/9/11 15:50
调度管理模块
"""

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from common.config import ConfigManager


class SchedulerManager:
    """调度任务处理"""

    __SCH_HANDLERS = {}  # 调度处理器

    @classmethod
    def register(cls, name="default", g_config=None):
        """注册调度器"""
        if name in cls.__SCH_HANDLERS:
            raise RuntimeError("the scheduler is already registered")
        scheduler = BackgroundScheduler()
        if g_config is None:
            g_config = {
                "apscheduler.executors": {"default": ThreadPoolExecutor(20)},
                "apscheduler.job_defaults": {"coalesce": True, "max_instance": 1},
            }
        scheduler.configure(g_config)
        cls.__SCH_HANDLERS[name] = scheduler

    @staticmethod
    def get_instance(name="default"):
        """获取调度器实例"""
        if name not in SchedulerManager.__SCH_HANDLERS:
            raise RuntimeError("Need to register the instance")
        return SchedulerManager.__SCH_HANDLERS[name]

    @staticmethod
    def update(name="default", scheduler=None):
        """更新调度器实例"""
        if SchedulerManager.get_instance(name):
            return SchedulerManager.__SCH_HANDLERS[name].update(name, scheduler)


def sch_config_handler(conf):
    """通过配置中心注册调度任务"""
    for section in conf.iter_keys():
        sch_prefix = "apscheduler."
        job_prefix = "job."
        if section.startswith(sch_prefix):
            executors = conf.get(
                section, "executors", default={"default": ThreadPoolExecutor(20)}
            )
            job_defaults = conf.get(
                section, "job_defaults", default={"coalesce": True, "max_instance": 1}
            )
            # trigger = conf.get(section, "trigger", default="cron")
            # trigger_args = conf.get(section, "trigger_args", default={})
            # for k, v  in conf.get(section).items():
            #     if k.startswith(job_prefix):
            #         # 配置定时任务job
            #         ...

            g_config = {
                "apscheduler.executors": executors,
                "apscheduler.job_defaults": job_defaults,
            }
            SchedulerManager.register(
                name=section[len(sch_prefix) :], g_config=g_config
            )


ConfigManager.register_config_handler(sch_config_handler)
