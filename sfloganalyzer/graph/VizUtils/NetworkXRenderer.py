import Operations
import networkx as nx


class Renderer:
    def __init__(self, *args, **kwargs):
        self.options = Operations.dynamicDict(kwargs)
        self.nodestyle = "filled, rounded"
        fileformat = self.options.format
        self.filename = self.options.logfile
        self.g = nx.DiGraph()
        self.useloops = self.options.useloops

    def processStack(self, opsList: Operations.OperationsList):
        self.operations = opsList
