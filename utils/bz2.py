from bz2 import BZ2File
from pathlib import Path
from threading import Lock

from .fs import safe_open
from .progress import Task
from .sync import run_in_threadpool

lock = Lock()

block_size = 1024 * 1024 * 4


@run_in_threadpool
def decompress_bz2(path: Path):
    if path.with_suffix("").exists():
        return

    task = Task(f"decompressing [b]{path.name}", path.stat().st_size)

    with BZ2File(path, "rb") as bz2_file, safe_open(path.with_suffix(""), "wb") as tar:
        while True:
            with lock:
                block = bz2_file.read(block_size)

            if not block:
                break

            tar.write(block)

            task.update(advance=block_size)
