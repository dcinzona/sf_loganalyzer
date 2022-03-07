import sfloganalyzer.Operations as Operations
import networkx as nx
from sfloganalyzer.graph.VizUtils.Renderer import Renderer


class NetworkXRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        self.options = Operations.dynamicDict(kwargs)
        self.nodestyle = "filled, rounded"
        # fileformat = self.options.format
        self.filename = self.options.logfile
        self.g = nx.MultiDiGraph(name=self.filename)
        self.useloops = self.options.useloops

    def processStack(self, opsList: Operations.OperationsList):
        self.operations = opsList
