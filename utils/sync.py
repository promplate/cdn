from asyncio import get_running_loop
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from functools import cache, partial, wraps
from inspect import isgeneratorfunction
from os import cpu_count
from typing import Any, AsyncGenerator, Awaitable, Callable, Generator, Iterator, ParamSpec, TypeVar, overload

P = ParamSpec("P")
T = TypeVar("T")


concurrency = cpu_count() or 1

get_thread_pool = cache(lambda: ThreadPoolExecutor(concurrency))


@overload
def run_in_threadpool(func: Callable[P, Generator[T, Any, Any]]) -> Callable[P, AsyncGenerator[T, None]]: ...


@overload
def run_in_threadpool(func: Callable[P, T]) -> Callable[P, Awaitable[T]]: ...


def run_in_threadpool(func):  # type: ignore
    if isgeneratorfunction(func):

        @wraps(func)
        async def _(*args, **kwargs):
            it: Iterator = func(*args, **kwargs)
            with suppress(StopIteration):
                obj = object()
                while True:
                    res = await get_running_loop().run_in_executor(get_thread_pool(), next, it, obj)
                    if res is obj:
                        break
                    else:
                        yield res

    else:

        @wraps(func)
        async def _(*args, **kwargs):
            return await get_running_loop().run_in_executor(get_thread_pool(), partial(func, *args, **kwargs))

    return _
