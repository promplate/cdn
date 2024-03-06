from downloads import pyodide
from utils.progress import progress


async def main():
    await pyodide.download_all()


if __name__ == "__main__":
    from asyncio import run

    with progress:
        run(main())
