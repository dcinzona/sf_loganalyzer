import os
import sys


__import__("pkg_resources").declare_namespace("sfla")

__location__ = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(__location__, "version.txt")) as f:
    __version__ = f.read().strip()

if sys.version_info < (3, 8):  # pragma: no cover
    raise Exception("SF LogAnalyzer requires Python 3.8+.")


def setOptions(**kwargs):
    """Set options for sfla"""
    from . import options

    for k, v in kwargs.items():
        setattr(options, k, v)
    return options
