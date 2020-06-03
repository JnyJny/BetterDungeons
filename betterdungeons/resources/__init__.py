"""
"""

import importlib.resources
from pathlib import Path
from functools import partial

_RESMOD = "dungeon.resources"

_contents = partial(importlib.resources.contents, _RESMOD)
_is_resource = partial(importlib.resources.is_resource, _RESMOD)
_path = partial(importlib.resources.path, _RESMOD)


def contents() -> str:

    for filename in _contents():
        if _is_resource(filename):
            yield filename


def path_for(name: str) -> Path:
    """Looks for a file in the resources module that matches `name`
    exactly or that starts with `name`. 

    :param name: str
    :return: pathlib.Path
    """

    for filename in contents():
        if filename == name or filename.startswith(name):
            with _path(filename) as path:
                return path.resolve()

    raise FileNotFoundFound(name)
