from functools import partial

from rich.progress import Progress

progress = Progress()


class Task:
    def __init__(self, description: str, total: int | None = None):
        self.id = progress.add_task(description, True, total)
        self.update = partial(progress.update, self.id, refresh=True)
