# vim set fileencoding=utf-8
""" error/exception base module """

from collections import namedtuple

Error = namedtuple("Error", ["errno", "msg", "user_msg"])


class ErrorMeta(type):
    """异常元类"""

    def __new__(mcs, clsname, bases, attrs):
        for key, value in attrs.items():
            if key.startswith("E_") and isinstance(value, tuple):
                if len(value) < 3:
                    attrs[key] = Error(*value, user_msg="系统错误")
                else:
                    attrs[key] = Error(*value)
        setattr(Error, '__str__', lambda x: "<%d: %s>" % (x.errno, x.msg))
        return super(ErrorMeta, mcs).__new__(mcs, clsname, bases, attrs)


class QtError(object, metaclass=ErrorMeta):  # pylint: disable=too-few-public-methods
    """Qt Error number and descript"""

    # Base Error
    E_SUCCESS = (0, 'success')
    E_BASEERROR = (1000, 'base error')
    E_AUTH_FAILED = (1002, 'auth failed')
    E_ACCESS_LIMIT = (1003, 'access rate limit')
    E_SLOW_REQUEST = (1004, 'request too slow')
    E_INPROCESS = (1005, "in process")
    E_RETRY = (1006, "retry...")
    E_FINISH_REQUEST = (1007, "finish request")

    E_BAD_REQUEST = (1100, 'bad request')
    E_RESP_LOGICAL = (1201, 'app logical error')
    E_EXIST = (1202, "already exist")
    E_NOT_EXIST = (1203, "not exist")

    # Logical Error
    E_INCONSISTENT = (1301, 'inconsistent')
    E_LOGICAL = (1302, 'logical error')
    E_SUPPORT = (1303, 'not support')
    E_NO_RECORD = (1310, 'record not exist')

    # other system error
    E_OTHER_BASE = (1500, 'other system error')
    E_CONNECT = (1501, 'connect other failed')

    # Model Data Count Error
    E_INSUFFICIENT_SAMPLES = (1600, "insufficient samples")

    # System Error
    E_QTQA = (-1000002, "test error")


class QtException(Exception):
    """自定义异常类"""

    def __init__(self, error=QtError.E_BASEERROR, msg=None, **kwargs):
        # pylint: disable=no-member
        self.error = error
        self.kwargs = kwargs
        self.args = self.kwargs.pop('args', [])
        self.msg = msg or (error.msg.format(
            *self.args) if self.args else error.msg)
        self.user_msg = kwargs.get('user_msg', error.user_msg)
        super().__init__(self.msg)

    def __reduce_ex__(self, proto=None):
        return type(self), (self.error, self.msg), self.__dict__

    def __str__(self):
        message = f"{self.msg}({self.error.errno})"  # pylint: disable=no-member
        if self.kwargs:
            message += f"{self.kwargs}"
        return message

    def __repr__(self):
        """Messages for user"""
        return self.user_msg


class QtOtherException(QtException):
    """来源于其他系统的异常基类"""

    def __init__(self, error=QtError.E_OTHER_BASE, msg=None, **kwargs):
        self.errno = kwargs.get("errno", 0)
        self.err_plat = kwargs.get("plat", "unknow")
        msg = msg or f"{error}({self.errno})"
        super().__init__(error, msg, **kwargs)
