# vim set fileencoding=utf-8
"""dask helper module"""
import functools

from common.async_helper import patch_async_run
from common.config import get_config
from distributed import Client

DEFAULT_DASK_ADDRESS = "localhost:9010"


def submit_process(fns):
    address = get_config("dask",
                         "address",
                         required=True,
                         default=DEFAULT_DASK_ADDRESS)
    client = Client(address=address)
    futures = []
    for fn in fns:
        futures.append(client.submit(fn))
    result = client.gather(futures)
    return result


def patch_run_process(fns, worker=4, patch=8, is_coroutine=True):
    results = []
    if not fns:
        return results
    group_len = max((len(fns) // worker + 1), worker)
    fns_group = [
        functools.partial(
            patch_async_run,
            fns[idx:idx + group_len],
            patch=patch,
            is_coroutine=is_coroutine,
        ) for idx in range(0, len(fns), group_len)
    ]
    ret = submit_process(fns_group)
    if ret:
        results = sum(ret, [])
    return results


async def async_submit_process(fns, is_coroutine=True):
    address = get_config("dask",
                         "address",
                         required=True,
                         default=DEFAULT_DASK_ADDRESS)
    client = await Client(address=address, asynchronous=is_coroutine)
    futures = []
    for fn in fns:
        futures.append(client.submit(fn))
    ret = await client.gather(futures, asynchronous=is_coroutine)
    return ret


async def patch_async_run_process(fns, worker=4, patch=8, is_coroutine=True):
    results = []
    if not fns:
        return results
    group_len = max((len(fns) // worker + 1), worker)
    fns_group = [
        functools.partial(
            patch_async_run,
            fns[idx:idx + group_len],
            patch=patch,
            is_coroutine=is_coroutine,
        ) for idx in range(0, len(fns), group_len)
    ]
    ret = await async_submit_process(fns_group)
    if ret:
        results = sum(ret, [])
    return results
