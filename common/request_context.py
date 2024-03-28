# coding=utf-8
"""module"""

from contextvars import ContextVar
from typing import Optional

Request: ContextVar[Optional[str]] = ContextVar('request', default=None)
