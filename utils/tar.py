from pathlib import Path
from tarfile import TarFile

from .progress import Task
from .sync import run_in_threadpool


@run_in_threadpool
def extract_tar(path: Path, target_folder: Path, directory: str | None = None):
    target_folder.mkdir(parents=True, exist_ok=True)

    task = Task(f"   extracting [b]{path.name}")

    with TarFile.open(path, mode="r") as tar:
        if directory is None:
            members = tar.getmembers()
        else:
            members = [i for i in tar.getmembers() if i.name.startswith(directory)]

        task.update(total=len(members))

        for member in members:
            if directory:
                member.path = member.path.removeprefix(directory).lstrip("/")
            tar.extract(member, target_folder)

            task.update(advance=1)

    path.unlink()
