
from pprint import pformat
from tokenize import group
from Operations.Invocations.FatalError import FatalErrorOp
from Operations.Cluster import Cluster
from Operations.OpUtils import dynamicDict
from Operations.Operation import Operation
import graphviz


class renderer():

    operations: list[Operation] = []

    def __init__(self, *args, **kwargs) -> None:
        self.options = dynamicDict(kwargs)
        self.nodestyle = 'filled, rounded'
        fileformat = self.options.format
        self.filename = self.options.logfile
        self.g = graphviz.Digraph(
            f'{self.filename}',
            graph_attr={
                'label': f'Log file visualization for {self.filename}', 'outputorder': 'nodesfirst'},
            format=fileformat)
        self.useloops = self.options.useloops  # kwargs.get('useloops', False)
        self.stackProcessMap = {}
        self.g.strict = self.options.strict
        self.g.engine = self.options.engine
        self.g.graph_attr['rankdir'] = self.options.rankdir
        self.g.graph_attr['fontname'] = "helveticaneue-light,Helvetica,Arial,sans-serif"
        self.g.attr(
            'node', fontname='helveticaneue-light,Helvetica,Arial,sans-serif')
        self.g.attr(
            'edge', fontname='helveticaneue-light,Helvetica,Arial,sans-serif')

    def processClusters(self, clusterOps: list[Cluster]):
        self.clusters = clusterOps
        if(self.clusters is None or len(self.clusters) == 0):
            raise Exception("No clustered operations found in the log file")

        for cluster in self.clusters:
            print(f"Processing cluster {cluster.name}")
            self._processCluster(cluster)
        pass

    def _processCluster(self, cluster: Cluster):
        with self.g.subgraph(name=f'cluster_{cluster.name}',
                             graph_attr={
                                 'label': f'{cluster.name}',
                                 'tooltip': f'{cluster.name}',
                                 'style': "invis",
                                 'ordering': "out",
                                 'margin': '24.0',
                                 'rankdir': self.options.rankdir,
                                 'labeljust': 'c'}) as g:

            for idx, op in enumerate(cluster.operations):
                self._validateOperations(op, idx)
                self._loadNodesAndEdgesIntoGraph(g, op, idx, None)

    def processStack(self, sortedOperations: list):
        self.operations = sortedOperations

        if(len(self.operations) == 0):
            raise Exception("No operations found in the log file")

        self._checkIdx()

        with self.g.subgraph(name='cluster_Log', graph_attr={'labeljust': 'c',
                                                             'outputorder': 'nodesfirst',
                                                             # 'outputorder': 'edgesfirst',
                                                             'margin': '24.0',
                                                             'rank': 'min',
                                                             'style': "invis",
                                                             'ordering': "out"}) as g:
            if(self.options.debug):
                print(g.graph_attr.__str__())
                with self.g.subgraph(name='cluster_debug', graph_attr={
                        'labeljust': 'c', 'rank': 'min', 'style': "invis"}) as g2:
                    g2.node('debug', label=pformat(g.graph_attr, indent=4),
                            shape='box', style='filled', fontsize='16')

            g.node('start', label='START', shape='invhouse', style='filled',
                   fillcolor=self.lighten('#00FF00', .4), fontsize='16')

            with g.subgraph(name='cluster_STACK', graph_attr={
                    'labeljust': 'c', 'rank': 'same', 'style': "invis", 'ordering': 'out'}) as dg:

                self._buildGraph(dg)

            g.node('end', label='END', shape='invhouse', style='filled',
                   fillcolor=self.lighten('#00FF00', .4), fontsize='16')

    def _buildGraph(self, g: graphviz.Digraph) -> None:
        clusterIdx = 0
        subclusters = [g]
        for idx, op in enumerate(self.operations):
            self._validateOperations(op, idx)
            try:
                if(op.isClusterOp):
                    clusterIdx += 1
                    graph = graphviz.Digraph(
                        f'cluster_{clusterIdx}')
                    graph.graph_attr['label'] = f'{op.safeName}'
                    graph.graph_attr[
                        'tooltip'] = f'{op.safeName}\n{self._getLimitDataString(op)}'
                    graph.graph_attr['style'] = 'invis'
                    graph.graph_attr['rank'] = 'same'
                    # subclusters.append(graph)

                self._loadNodesAndEdgesIntoGraph(
                    subclusters[-1], op, idx, clusterIdx)

            except Exception as e:
                print(
                    f"Error processing operation {op}")
                raise e
        for graph in subclusters:
            # g.subgraph(graph)
            pass

    clusterGroup = 'root'

    def _loadNodesAndEdgesIntoGraph(self, g: graphviz.Digraph, op: Operation, idx: int, clusterIdx: int = 0) -> None:

        if(op.isClusterOp and self.options.debug):
            print(f'[{op.lineNumber}] {op.LIMIT_USAGE_FOR_NS[0]}')
            print(op.clusterId)
            self.clusterGroup = op.clusterId
            exit()
            pass

        opName = op.safeName
        # f'{self._getOpNodeId(op)}{clusterIdx}' if op.isClusterOp == False else f'{self._getOpNodeId(op)}{clusterIdx-1}'
        nodeId = self._getOpNodeId(op)
        parentNodeId = self._getOpNodeId(
            op.PREV_OPERATION) if op.PREV_OPERATION is not None else 'start'
        parentOpName = op.PREV_OPERATION.safeName if op.PREV_OPERATION is not None else 'start'
        nodeTT = self._getNodeTooltip(op)

        if(self.options.redact):
            if(isinstance(op, FatalErrorOp)):
                nodeTT += f'\n   {op.safeName}'

            else:
                opName = f'UID: {op.nodeId}'
                nodeTT += f'\n   {op.nodeId}'
                parentOpName = parentNodeId

        else:
            nodeTT += f'\n   Operation: {op.safeName}'

        nodeTT += self._getLimitDataString(op)

        # create and style the edges (arrows to each node)
        lmtstr: str = None
        if(op.PREV_OPERATION is not None and op.PREV_OPERATION.isClusterOp and not self.options.strict):
            lmtstr = f'\nLimits Usage Data:\nNamespace: {op.PREV_OPERATION.namespace}\n  '
            lmtstr += '\n  '.join(op.PREV_OPERATION.LIMIT_USAGE_FOR_NS)

        edgetooltip = f'''Previous Node:
                            LogLine: [{op.PREV_OPERATION.lineNumber}]
                            Type: {op.PREV_OPERATION.eventType}
                            Name: {parentOpName}''' if op.PREV_OPERATION is not None else ''

        edgetooltip += f'''\nNext Node:
                            {nodeTT}\n'''

        edgetooltip += lmtstr if lmtstr is not None else ''
        edgetooltip = edgetooltip.replace(
            '                                ', '')

        isLastOp = op == self.operations[-1]
        edgeLabelColor = '#000000' if lmtstr is None else '#cc2222'
        edgePenWidth = '1.0' if lmtstr is None else '3.0'
        tail = parentNodeId if idx > 0 else 'start'
        head = nodeId
        nodeColor = self._opColor(
            op.PREV_OPERATION.eventType) if idx > 0 and not isLastOp else self._opColor(op.eventType)

        tailurlId = f'lognode{parentNodeId}'
        headurlId = f'lognode{nodeId}'
        self._addEdge(g,
                      tail,
                      head,
                      f'{idx + 1}',
                      #   taillabel=taillabel,
                      #   headlabel=headlabel,
                      color=nodeColor,
                      tooltip=edgetooltip,
                      labeltooltip=edgetooltip,
                      tailtooltip=edgetooltip,
                      headtooltip=edgetooltip,
                      edgetooltip=edgetooltip,
                      fontcolor=edgeLabelColor,
                      # tail links to head, head links to tail
                      tailURL=f'#{headurlId}',
                      headURL=f'#{tailurlId}',
                      penwidth=edgePenWidth,
                      constraint='true')

        if(isLastOp):
            g.edge(nodeId, 'end', label=f'{len(self.operations) + 1}', color=self._opColor(
                op.eventType), tooltip=edgetooltip, labeltooltip=edgetooltip, penwidth=edgePenWidth, constraint='true')

        # create and style the nodes
        nodepenwidth = '3.0' if len(op.LIMIT_USAGE_FOR_NS) > 0 else '1.0'

        g.node(nodeId, label=f'<{opName}<BR ALIGN="LEFT"/><font POINT-SIZE="8"><b><sub>{op.eventType}</sub></b></font>>',
               shape='box',
               color=self._eventTypeColor(op.eventType),
               fillcolor=self._opFillColor(op.eventType),
               style=self.nodestyle,
               tooltip=self._getNodeTooltip(op),
               id=headurlId,
               penwidth=nodepenwidth,
               group=self.clusterGroup
               )

    def _getNodeTooltip(self, op: Operation) -> str:
        tt = f'Line [{op.lineNumber}]\n   {op.eventType}'

        if(self.options.redact):
            tt += f'\n   {op.safeName}' if isinstance(
                op, FatalErrorOp) else f'\n   Operation Unique ID: ({op.idx})'
        else:
            tt += f'\n   Operation: {op.safeName}'

        return tt

    def _getLimitDataString(self, op: Operation) -> str:
        if(len(op.LIMIT_USAGE_FOR_NS) == 0):
            return ''

        lmtstr = '\nLimits Usage Data:\n  '
        lmtstr += '\n  '.join(op.LIMIT_USAGE_FOR_NS)

        return lmtstr

    def _addEdge(self, g: graphviz.Digraph, tail: str, head: str, label: str, _attributes=None, **kwargs):
        g.edge(tail, head, label, **kwargs)

    def _validateOperations(self, op: Operation, idx: int) -> None:
        if(op.PREV_OPERATION is None and idx > 0):
            op.PREV_OPERATION = self.operations[idx - 1]
            # raise(Exception(f'Operation [{idx}] {op.name} has no previous operation'))
        if(op.NEXT_OPERATION is None and idx < len(self.operations) - 1):
            op.NEXT_OPERATION = self.operations[idx + 1]
            # raise(Exception(f'Operation [{idx}] {op.name} has no next operation'))

        if(op.PREV_OPERATION is not None and op.PREV_OPERATION.eventId == op.eventId):
            raise(Exception(
                f'Operation [{idx}] {op.name} is a duplicate of [{op.PREV_OPERATION.name}]'))

        if(op.NEXT_OPERATION is not None and op.eventId == op.NEXT_OPERATION.eventId):
            raise(
                Exception(f'Operation [{idx}] {op.name} is a duplicate of [{op.NEXT_OPERATION.name}]'))

    def _getOpNodeId(self, op: Operation) -> str:
        nodeId = op.nodeId
        if(self.useloops is False):
            # make each node operation unique to prevent looping
            nodeId = f'{op.idx}{op.nodeId}'
        return nodeId

    def _opColor(self, evtType: str) -> str:
        return self._eventTypeColor(evtType)

    def _eventTypeColor(self, eventType) -> str:
        color = '#888888'
        if(eventType == 'APEX'):
            # add to apex cluster
            color = '#0101FF'
            pass
        elif(eventType == 'TRIGGER'):
            # add to trigger cluster
            color = '#800180'
            pass
        elif(eventType == 'FLOW'):
            # add to flow cluster
            color = '#033E3E'
            pass
        elif(any(x in eventType for x in ['ERROR', 'EXCEPTION'])):
            color = '#FF0101'
            pass
        elif(eventType == 'PROCESS BUILDER'):
            # add to flow cluster
            color = '#418855'
            pass
        return color.lower()

    def _opFillColor(self, eventType: str) -> str:
        return self.lighten(self._eventTypeColor(eventType), .7)

    def lighten(self, hex, amount):
        """ Lighten an RGB color by an amount (between 0 and 1),

        e.g. lighten('#4290e5', .5) = #C1FFFF
        """
        hex = hex.replace('#', '')
        red = min(255, int(hex[0:2], 16) + 255 * amount)
        green = min(255, int(hex[2:4], 16) + 255 * amount)
        blue = min(255, int(hex[4:6], 16) + 255 * amount)
        return "#%X%X%X" % (int(red), int(green), int(blue))

    def _checkIdx(self) -> None:
        if(len(self.operations) == 0):
            raise Exception("No operations found in the log file")

        if('idx' not in self.operations[0]):
            for idx, op in enumerate(self.operations):
                op['idx'] = idx

        if(self.options.redact or True):
            uniques = []

            for op in self.operations:
                idx = uniques.index(op.nodeId) if op.nodeId in uniques else -1

                if(idx == -1):
                    uniques.append(f'{op.nodeId}')
                    op._nodeId = f'{op.__class__.__name__}({len(uniques)-1})'
                    continue

                op._nodeId = f'{op.__class__.__name__}({idx})'

    def _printStack(self, prefix: str = '', inputStack: list[Operation] = None, suffix: str = ''):
        arr = self.operations if inputStack is None else inputStack
        if(len(arr) == 0):
            raise Exception("No operations found in the log file")
        for op in arr:
            outstr = f' > {op.idx} {prefix} [{op.lineNumber}] {op.eventType} | {op.name} | {op.finished} {suffix}'
            print(outstr)

    def _setparentstack(self, op):
        if(op.get('parent', None) is not None):
            op.parent.setdefault('children', [])
            op.parent['children'].append(op)
        else:
            if(op.idx > 0):
                raise Exception(
                    f"Operation should have a parent \n {op.__dict__}")
