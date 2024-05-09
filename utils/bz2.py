from bz2 import BZ2File
from pathlib import Path
from threading import Lock

from .fs import safe_open
from .progress import Task
from .sync import run_in_threadpool

lock = Lock()

block_size = 1024 * 1024 * 100  # 100MB


@run_in_threadpool
def _decompress_bz2(path: Path):
    if path.with_suffix("").exists():
        return

    task = Task(f"decompressing [b]{path.name}")

    with BZ2File(path, "rb") as file:
        while True:
            with lock:
                block = file.read(block_size)

            if not block:
                break

            yield block

    task.update(total=1, completed=1)


async def decompress_bz2(path: Path):
    async with safe_open(path.with_suffix(""), "wb") as tar:
        async for block in _decompress_bz2(path):
            await tar.write(block)
