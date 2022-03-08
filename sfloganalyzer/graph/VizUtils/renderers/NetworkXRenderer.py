import sfloganalyzer.options as options
import sfloganalyzer.Operations as Operations
import networkx as nx
from sfloganalyzer.Operations.OpUtils import AttributeInitType
from sfloganalyzer.graph.VizUtils.Renderer import Renderer


class NetworkXRenderer(Renderer, metaclass=AttributeInitType):
    def __init__(self, *args, **kwargs):
        super(NetworkXRenderer, self).__init__()
        print(f"\n{self.__class__.__name__} args: {args}")
        print(f"{self.__class__.__name__} kwargs: {kwargs}")
        self.nodestyle = "filled, rounded"
        # fileformat = self.options.format
        self.filename = options.logfile
        self.useloops = options.useloops
        self.g = nx.MultiDiGraph(name=self.filename)

    def processStack(self, opsList: Operations.OperationsList):
        self.operations = opsList
