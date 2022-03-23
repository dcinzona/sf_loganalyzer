from sfloganalyzer.Operations.Operation import Operation
from sfloganalyzer.graph.VizUtils.utils.RenderUtils import EdgeElement, NodeElement


class Renderer(object):
    operations: list[Operation] = []
    nodes: list[NodeElement] = []
    edges: list[EdgeElement] = []
