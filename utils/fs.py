from contextlib import contextmanager
from functools import wraps
from pathlib import Path

root = Path("data")


@wraps(open)
@contextmanager
def safe_open(file, mode: str):
    path = Path(file)

    tmp_path = root / "tmp" / path.relative_to(root)
    try:
        tmp_path.parent.mkdir(exist_ok=True)
        with tmp_path.open(mode) as f:
            yield f

        tmp_path.replace(path)

    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
