from contextlib import asynccontextmanager
from functools import wraps
from pathlib import Path
from typing import Literal, cast

from aiofiles import open

root = Path("data")


@wraps(open)
@asynccontextmanager
async def safe_open(file, mode):
    path = Path(file)

    tmp_path = root / "tmp" / path.relative_to(root)
    try:
        tmp_path.parent.mkdir(exist_ok=True)
        async with open(tmp_path, cast(Literal["rb", "wb"], mode)) as f:
            yield f

        tmp_path.replace(path)

    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
