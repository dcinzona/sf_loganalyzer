"""CLI options for sfloganalyzer
Because the entry point for this is always the CLI, 
we don't need to worry about different options 
for different contexts or operations.

Returns: a shared options class for the context of the application
"""

import inspect
import sfloganalyzer


logfile: str = None
debug: bool = False
useloops: bool = False
engine: str = "dot"
format: str = "svg"
no_show: bool = False
strict: bool = False
exclude: list[str] = []
rankdir: str = "TB"
stop_on_exception: bool = False
redact: bool = False


def __call__(**kwargs):
    return setOptions(**kwargs)


def set(**kwargs):
    return setOptions(**kwargs)


def setOptions(**kwargs):
    sfloganalyzer.setOptions(**kwargs)


def __getattr__(name):
    if debug:
        print(f"SFLOGANALYZER\n property:'{name}' not found in options")
        print(f" {inspect.stack()[1][0]}")
    return None
