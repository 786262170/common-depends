"""async_helper module"""
import asyncio
from asyncio.futures import wrap_future
from concurrent.futures import ThreadPoolExecutor

from asgiref.sync import async_to_sync

MAX_WORKERS = 32
EXECUTOR = None


def run_async(func, *args, **kwargs):
    """run_async同步版本"""
    return async_to_sync(func)(*args, **kwargs)


def run_sync(func, *args, **kwargs):
    """sync start other thread"""
    global EXECUTOR  # pylint: disable=global-statement
    if EXECUTOR is None:
        # 协程不考虑多线程访问
        EXECUTOR = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    return wrap_future(EXECUTOR.submit(func, *args, **kwargs))


async def patch_async_run(fns, patch=8, is_coroutine=False, timeout=None):
    """异步并发执行
    :param fns: 函数引用列表, List[Callable]
    :param patch: 分组长度, 过大或过小可能并未达到最优的性能，根据实际需要调整合适的patch值
    :param is_coroutine: 是否异步(True if fns is async else False), boolean
    :param timeout: 超时时间, int 默认为None
    :return List[result]
    :raise asyncio.TimeoutError
    """
    results = []
    if not fns:
        return results
    for idx in range((len(fns) + patch - 1) // patch):
        tasks = fns[patch * idx:patch * (idx + 1)]
        for num, value in enumerate(tasks):
            if not is_coroutine:
                tasks[num] = asyncio.to_thread(value)
            else:
                tasks[num] = value()
            # 是否加入延迟耗时
            if timeout and isinstance(timeout, int):
                tasks[num] = asyncio.wait_for(tasks[num], timeout)

        patch_result = await asyncio.gather(*tasks)  # 结果值的顺序与 aws 中可等待对象的顺序一致
        results.extend(patch_result)
    return results
