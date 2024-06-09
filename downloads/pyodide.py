from asyncio import Semaphore, gather
from os import getenv

from packaging.version import Version

from utils.bz2 import decompress_bz2
from utils.fs import root
from utils.http import download, get_releases
from utils.progress import Task
from utils.tar import extract_tar

sem = Semaphore(int(getenv("CONCURRENCY", "1")))


async def download_one(tag_name: str, name: str):
    async with sem:
        await download("pyodide", "pyodide", tag_name, name)

    await decompress_bz2(root / name)

    await extract_tar(root / name.removesuffix(".bz2"), root / "pyodide" / f"v{tag_name.removeprefix("r")}", "pyodide")


async def download_all():
    task = Task("listing [b]pyodide[/b] releases")

    releases = [
        (tag_name, name)
        for release in await get_releases("pyodide", "pyodide")
        if Version(tag_name := release["tag_name"]) >= Version("0.25.0")
        for asset in release["assets"]
        if (name := asset["name"]) == f"pyodide-{tag_name}.tar.bz2"
    ]

    task.update(total=1, completed=1)

    await gather(*(download_one(*args) for args in releases))
