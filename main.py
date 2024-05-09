from downloads import pyodide


async def main():
    await pyodide.download_all()


if __name__ == "__main__":
    from asyncio import run

    run(main())
