# vim set fileencoding=utf-8
"""client module"""
import math
import os
from timeit import default_timer
from typing import IO
from urllib import parse
from urllib.request import Request

import httpx
import numpy as np
from httpx import HTTPStatusError

from common import utils
from common.error import QtError, QtException
from common.qt_logging import frame_log
from common.request_context import Request as RequestContext
from common.utilities import string_utils

try:
    import qtlib
except ImportError:
    frame_log.warning("qtlib is not available")
    qtlib = None

DEFAULT_REQUEST_TIMEOUT = 5
HTTP_PROXY = None


def add_turing_username_secret(req):
    """添加turing—db环境变量"""
    username = os.environ.get("TURING_USERNAME")
    secret = os.environ.get("TURING_SECRET")
    if not username or not secret:
        raise QtException(QtError.E_OTHER_BASE,
                          "环境变量中缺少TURING_USERNAME或TURING_SECRET")
    req.headers.update({"username": username, "secret": secret})


def build_cgi_request(url, req_method, data, headers, prepare, **para):
    para = utils.dict_trip(para)
    headers = headers or {}
    if "X-Request-Id" not in headers:
        if RequestContext.get():
            headers["X-Request-Id"] = str(RequestContext.get())
        else:
            headers["X-Request-Id"] = utils.get_random_cid()
        if isinstance(data, IO):
            # 支持stream post (urllib2 do_request_ len(data)
            headers["Content-Length"] = str(os.path.getsize(data.name))
    if para:
        url += "?" + parse.urlencode(para)
    req = Request(url, data, headers=headers, method=req_method)
    if req_method in ["PUT", "GET", "POST", "PATCH", "DELETE"]:
        req.get_method = lambda: req_method
    if prepare:
        prepare(req)
    frame_log.info("cgi request:{}|method:{}|headers:{}|body:{}",
                   req.get_full_url(), req.get_method(), req.headers,
                   str(req.data))
    return req


def cgi_request(url,
                req_method=None,
                data=None,
                prepare=None,
                decoder=None,
                headers=None,
                timeout=None,
                resp_header=None,
                **para):
    """公共cgi请求-同步"""
    req = build_cgi_request(url, req_method, data, headers, prepare, **para)
    if timeout is None:
        timeout = DEFAULT_REQUEST_TIMEOUT
    proxy_url = os.environ.get("http_proxy")
    try:
        with httpx.Client(proxies=proxy_url) as client:
            resp = client.request(req.get_method(),
                                  req.get_full_url(),
                                  data=data,
                                  headers=req.headers,
                                  timeout=timeout)
            resp.raise_for_status()
    except HTTPStatusError as err:
        raise QtException(QtError.E_OTHER_BASE, f"{url}:{err}")
    except Exception as err:
        raise QtException(QtError.E_CONNECT, f"{url}:{err}")
    content = resp.read()
    frame_log.info("resp:{}", utils.utf8fmt(content))
    if decoder:
        try:
            content = decoder(content)
        except QtException:
            raise
        except Exception as err:
            raise QtException(QtError.E_OTHER_BASE,
                              f"{url}: decoder resp error.({err})")
    if resp_header is not None:
        frame_log.info("headers:{}", resp.headers)
        resp_header.update(resp.headers)
    return utils.utf8fmt(content)


# pylint: disable=too-many-arguments, too-many-locals
async def async_cgi_request(url,
                            req_method=None,
                            data=None,
                            prepare=None,
                            decoder=None,
                            headers=None,
                            timeout=None,
                            resp_header=None,
                            **para):
    """公共cgi请求-异步"""
    req = build_cgi_request(url, req_method, data, headers, prepare, **para)
    if timeout is None:
        timeout = DEFAULT_REQUEST_TIMEOUT
    proxy_url = os.environ.get("http_proxy")

    async with httpx.AsyncClient(proxies=proxy_url) as client:
        resp = await client.request(
            req.get_method(),
            req.get_full_url(),
            data=data,
            headers=req.headers,
            timeout=timeout,
        )
        content = resp.read()
        frame_log.info("resp:{}", string_utils.utf8fmt(content))
        if decoder:
            try:
                data = decoder(content)
            except QtException:
                raise
            except Exception as err:
                raise QtException(QtError.E_OTHER_BASE,
                                  f"{url}: decoder resp error.({err})")
        else:
            data = content
            if resp_header is not None:
                frame_log.info("headers:{}", resp.headers)
                resp_header.update(resp.headers)
        return string_utils.utf8fmt(data)


def cpp_request(func, *args, **kwargs):
    """c++模块统一调用函数
    :param func:c++接口函数名称， callable
    :raise QtException
    """
    # 去除值为None的参数
    timeout = kwargs.pop("timeout", 30)
    decoder = kwargs.pop("decoder", lambda x: x)
    name = func.__name__
    start_time = default_timer()
    try:
        while default_timer() - start_time <= timeout:
            frame_log.info("'qtlib:{}' request args:{}, kwargs:{}", name, args,
                           kwargs)
            content = func(*args, **kwargs)
            break
        else:
            raise TimeoutError(f"{name} requset timed out:{timeout}")
    except QtException:
        raise
    except Exception as err:
        raise QtException(QtError.E_CONNECT,
                          f"'qtlib.{name}' request error.({err})")
    # 无限值和nan值处理
    if isinstance(content, int) and math.isinf(content):
        return None
    if isinstance(content, float) and np.isnan(content):
        return None
    # cpp计算结果序列化
    if decoder:
        try:
            frame_log.info("decoder:{} qtlib output result", decoder.__name__)
            content = decoder(content)
        except QtException:
            raise
        except Exception as err:
            raise QtException(QtError.E_OTHER_BASE,
                              f"{name}: decoder resp error.({err})")
    frame_log.info(f"'{name} request successful, resp:{content}")
    return content
