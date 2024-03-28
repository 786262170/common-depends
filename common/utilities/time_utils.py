# coding=utf8
"""时间处理"""
import datetime
import functools
import time
from typing import Optional, Union

import dateutil.parser
import qtlib
from chinese_calendar import is_holiday


def timing(f):

    @functools.wraps(f)
    def wrap(*args, **kw):
        from common.qt_logging import frame_log

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        frame_log.info("执行函数:{}, 参数:[], 耗时:{}秒, {}毫秒", f.__name__, (te - ts),
                       (te - ts) * 1000)
        return result

    return wrap


def to_datetime(obj, fmt="%Y-%m-%d %H:%M:%S"):
    """
    convert datetime, timestamp, date str(%Y-%m-%d %H:%M:%S) -> datetime obj
    """
    if isinstance(obj, datetime.datetime):
        return obj
    if isinstance(obj, int):
        return datetime.datetime.fromtimestamp(obj)
    if isinstance(obj, str):
        if obj.isdigit():
            return datetime.datetime.fromtimestamp(int(obj))  # 不考虑纯数字的timestr了
        return datetime.datetime.strptime(obj, fmt)
    raise TypeError(
        f"unsupport type:{type(obj)}|(datetime, timestamp, str format)")


def time_to_str(time_obj, fmt="%Y-%m-%d %H:%M:%S"):
    time_obj = to_datetime(time_obj)
    return datetime.datetime.strftime(time_obj, fmt)


def to_date(obj, fmt="%Y-%m-%d"):
    if isinstance(obj, datetime.date):
        return obj
    if isinstance(obj, str):
        if obj.isdigit():
            obj = int(obj)
        else:
            return datetime.datetime.strptime(obj, fmt).date()
    if isinstance(obj, int):
        return datetime.date.fromtimestamp(obj)
    raise TypeError(
        f"unsupport type:{type(obj)}|(date, timestamp, str format)")


def get_today_remaining_seconds():
    """获取当日剩余时间"""
    now = datetime.datetime.now()
    midnight = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
    return int((midnight - now).total_seconds()) + 1


def get_time_segment(now=datetime.datetime.now(), step=1 * 24 * 3600):
    """获取时间片段"""
    return time_to_str(now -
                       datetime.timedelta(seconds=step)), time_to_str(now)


def get_time_group(start_time, end_time, step=24 * 60 * 60, is_reversed=False):
    """分割时间段区间

    对起始和结束时间进行多次分隔, 用于减少单次db查询量过大

    :param start_time: 起始时间 %Y-%m-%d %H:%M:%S
    :param end_time: 结束时间 %Y-%m-%d %H:%M:%S
    :param step: 分隔时间段 24 * 60 * 60
    :param is_reversed: 反转 分隔时间迭代对象从结束到开始
    :return:多个时间间隔元祖组成的生成器 ((start,end)...)
    """
    start_time = to_datetime(start_time)
    end_time = to_datetime(end_time)
    if is_reversed:
        start_time, end_time = end_time, start_time
        step = 0 - step
    for t_delta in range(0, int((end_time - start_time).total_seconds()),
                         step):
        start_t = start_time + datetime.timedelta(seconds=t_delta)
        end_t = start_t + datetime.timedelta(seconds=step)
        start_t, end_t = ((max(end_t, end_time), start_t) if is_reversed else
                          (start_t, min(end_t, end_time)))
        yield str(start_t), str(end_t)


def month_beg(d: Optional[Union[datetime.datetime, datetime.date]]):
    return datetime.date(d.year, d.month, 1)


def month_end(d: Optional[Union[datetime.datetime, datetime.date]]):
    if d.month == 12:
        end = datetime.date(d.year, d.month, 31)
    else:
        end = datetime.date(d.year, d.month + 1,
                            1) + datetime.timedelta(days=-1)
    return end


def prev_month_start(v):
    now = dateutil.parser.parse(str(v))
    first = datetime.date(day=1, month=now.month, year=now.year)
    if first.month == 1:
        start = datetime.date(first.year - 1, 12, 1)
    else:
        start = datetime.date(first.year, first.month - 1, 1)
    return start


def prev_month_end(v):
    now = dateutil.parser.parse(str(v))
    first = datetime.date(day=1, month=now.month, year=now.year)
    lastMonth = first - datetime.timedelta(days=1)
    res_v = str(lastMonth.year) + str(lastMonth.month) + str(lastMonth.day)
    return res_v


def get_next_day(v, fmt="%Y-%m-%d"):
    d = dateutil.parser.parse(v) + datetime.timedelta(days=1)
    d = d.strftime(fmt)
    return d


def str_to_date(v, fmt="%Y%m%d"):
    if not v:
        return v
    if isinstance(v, datetime.date):
        return v
    return datetime.datetime.strptime(v, fmt).date()


def date_to_str(v, fmt="%Y%m%d"):
    if not v:
        return v
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.strftime(fmt)
    else:
        raise ValueError(f"时间格式有误，v:{v}")


def check_date(v: datetime.date | str):
    if isinstance(v, datetime.date):
        return v
    elif isinstance(v, str):
        fmt = "%Y%m%d"
        if "-" in v:
            fmt = "%Y-%m-%d"
        elif "/" in v:
            fmt = "%Y/%m/%d"
        try:
            date_v = datetime.datetime.strptime(v, fmt).date()
            return date_v
        except:
            raise RuntimeError(f"date:{v},参数有误")


def postponed_during_holidays(now_date: Union[datetime.date, str],
                              fmt="%Y-%m-%d") -> datetime.date:
    """中国节假日顺延"""
    now_date = to_date(now_date, fmt)
    while is_holiday(now_date):
        now_date += datetime.timedelta(days=1)
    return now_date


@functools.lru_cache(1000)
def to_cpp_date(yyyymmdd: str):
    """str to cpp date"""
    d = datetime.datetime.strptime(yyyymmdd, "%Y%m%d")
    temp = datetime.datetime(1899, 12, 30)  # Note, not 31st Dec but 30th!
    delta = d - temp
    return qtlib.Date(delta.days)


def cpp_date_to_str(cpp_date):
    """cpp date to str"""
    return qtlib.cpp_date_to_str(cpp_date)


def is_date_col(col_val):
    if isinstance(col_val, str):
        if col_val.isdigit():
            try:
                if check_date(col_val):
                    return True
            except:
                pass
    return False
