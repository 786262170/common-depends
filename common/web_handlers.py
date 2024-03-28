"""路由处理"""
from timeit import default_timer as timer
from typing import Callable

from common.error import QtException
from common.qt_logging import frame_log
from common.request_context import Request as RequestContext
from common.utils import get_random_cid
from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import JSONResponse


class RespModel(BaseModel):
    code: int = Field(default=200, title="响应状态码")
    msg: str = Field(default="Success", title="响应异常描述")
    errCode: int = Field(default=None, title="响应异常描述")
    data: dict = Field(default=None, title="返回数据")


async def set_body(request: Request):
    receive_ = await request._receive()

    async def receive():
        return receive_

    request._receive = receive


class BaseRouteHandlers(APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def _route_handler(request: Request) -> Response:
            try:
                before = timer()
                if not RequestContext.get():
                    RequestContext.set(get_random_cid())
                content_type = request.headers.get("content-type") or ""
                if "multipart/form-data; boundary=" in content_type:
                    request_text = "{'file_upload': 1}"
                else:
                    await set_body(request)
                    request_text = await request.body()
                    request_text = str(request_text.decode("utf-8"))
                frame_log.info(
                    "recv log request method:{},uri:{}\nheaders:{}\nquery_params:{}\nbody:{}\n",
                    request.method,
                    request.url,
                    dict(request.headers.items()),
                    request.query_params,
                    request_text,
                )
                response = await original_route_handler(request)
                duration = timer() - before
                response.headers["X-Response-Time"] = str(duration)
                response.headers["X-Request-Id"] = RequestContext.get()
            except Exception as exc:
                if isinstance(exc, QtException):
                    resp = RespModel(
                        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        errCode=exc.error.errno,
                        msg=str(exc),
                    )
                elif isinstance(exc, HTTPException):
                    resp = RespModel(code=exc.status_code, msg=exc.detail)
                elif isinstance(exc, RequestValidationError):
                    msg = "参数校验错误："
                    msg += ";".join([
                        f"'{raw_err._loc[-1]}': {raw_err.exc}"
                        for raw_err in exc.raw_errors
                    ])
                    msg = ";".join([err["msg"] for err in exc.errors()])
                    resp = RespModel(code=status.HTTP_400_BAD_REQUEST, msg=msg)
                else:
                    resp = RespModel(
                        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        msg="Server Internal Error, Please Retry Later",
                    )
                return JSONResponse(content=resp.dict())

        return _route_handler
