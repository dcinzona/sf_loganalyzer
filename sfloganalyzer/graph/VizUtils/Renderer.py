from abc import ABC
from sfloganalyzer.Operations.Operation import Operation


class Renderer(ABC):

    operations: list[Operation] = []
