# vim set fileencoding=utf-8
"""常量定义"""

import enum


class SvrEnv(enum.Enum):
    PRD = "prd"  # 正式环境
    DEV = "dev"  # 测试环境
    SIT = "sit"  # 测试fix环境
    DEMO = "demo"  # 客户演示环境
