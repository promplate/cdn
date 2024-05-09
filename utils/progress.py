from atexit import register
from functools import cache, partial
from sys import stdout
from typing import TYPE_CHECKING

from rich import print
from rich.progress import Progress

get_progress = cache(Progress)


if INTERACTIVE := stdout.isatty():
    get_progress().start()

    register(get_progress().stop)


class Task:
    def __init__(self, description: str, total: int | None = None):
        if INTERACTIVE or TYPE_CHECKING:
            task_id = get_progress().add_task(description, True, total)
            self.update = partial(get_progress().update, task_id, refresh=True)
        else:
            print(description)
            self.update = lambda **_: 0
