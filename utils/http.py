from os import getenv
from typing import AsyncIterable, Awaitable, Literal, TypedDict, cast

from niquests import AsyncSession

from .fs import root, safe_open
from .progress import Task

headers = {"accept": "application/vnd.github+json, */*"}

if token := getenv("GITHUB_TOKEN"):
    headers["authorization"] = f"Bearer {token}"


class ReleaseItem(TypedDict):
    tag_name: str
    assets: list[dict[Literal["name"], str]]


async def get_releases(owner: str, repo: str) -> list[ReleaseItem]:
    async with AsyncSession() as session:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        res = await session.get(url, headers=headers)
        res.raise_for_status()
        return res.json()


async def download(owner: str, repo: str, tag: str, asset: str):
    path = root / asset
    if path.exists():
        return

    path.parent.mkdir(exist_ok=True)

    url = f"https://github.com/{owner}/{repo}/releases/download/{tag}/{asset}"

    task = Task(f"  downloading [b]{asset}")

    async with AsyncSession() as session:
        res = await session.get(url, headers=headers, stream=True)

    res.raise_for_status()

    task.update(total=int(res.headers["content-length"]))

    with safe_open(path, "wb") as f:
        async for i in await cast(Awaitable[AsyncIterable[bytes]], res.iter_content()):
            f.write(i)
            task.update(advance=len(i))
