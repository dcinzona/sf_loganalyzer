
from Operations.Operation import Operation


class ClusterStack:
    clusters: list['Cluster']
    parent: 'Cluster'
    children = property(lambda self: self.clusters)

    def __init__(self, parent: 'Cluster' = None):
        self.clusters = []
        self.parent = parent
        if(parent is not None):
            self.parent.children.append(self)

    def getParent(self, input: 'Cluster') -> 'ClusterStack':
        clustersInRange = [parent for parent in self.clusters
                           if parent.start < input.start
                           and parent.end > input.end]
        if(len(clustersInRange) > 0):
            yield ClusterStack(clustersInRange[0])
        return None


class Cluster(object):
    start: int
    end: int
    data: dict
    operations: list[Operation]

    def __init__(self, start: int = 0, end: int = 0, data: dict = {}):
        self.start = start
        self.end = end
        # Or if you don't have lots of nested objects, data.copy()
        self.data = data.copy()
        self.operations = []

    def addOperation(self, operation: 'Operation') -> None:
        if(operation.lineNumber >= self.start and operation.lineNumber < self.end):
            self.data[operation.namespace].append(operation)

    def __str__(self) -> str:
        obj = {}
        obj['start'] = self.start
        obj['end'] = self.end
        obj['data'] = self.data
        return str(obj)
