
from opcode import opname
from Operations.Invocations.FatalError import FatalErrorOp
from Operations.Invocations.FlowOperation import FlowOperation
from Operations.OpUtils import dynamicDict
from Operations.Operation import Operation
import graphviz


class renderer():

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
        self.useloops = kwargs.get('useloops', False)
        self.stackProcessMap = {}
        self.g.strict = self.options.strict
        self.g.engine = self.options.engine
        self.g.graph_attr['rankdir'] = self.options.rankdir
        self.g.graph_attr['fontname'] = "helveticaneue-light,Helvetica,Arial,sans-serif"
        self.g.attr(
            'node', fontname='helveticaneue-light,Helvetica,Arial,sans-serif')
        self.g.attr(
            'edge', fontname='helveticaneue-light,Helvetica,Arial,sans-serif')

    def processStack(self, sortedOperations: list):
        self.operations = sortedOperations

        if(len(self.operations) == 0):
            raise Exception("No operations found in the log file")

        self._checkIdx()

        with self.g.subgraph(name='cluster_Stack', graph_attr={'labeljust': 'l',
                                                               'outputorder': 'nodesfirst',
                                                               'margin': '24.0',
                                                               'rankdir': self.options.rankdir}) as g:

            g.node('start', label='START', shape='invhouse', style='filled',
                   fillcolor=self.lighten('#00FF00', .4), rank='min', fontsize='16')

            self._buildGraph(g)

            g.node('end', label='END', shape='house', style='filled',
                   fillcolor=self.lighten('#00FF00', .4), rank='max', fontsize='16')

        # self._buildLegendSubgraph()

    def _buildLegendSubgraph(self):
        eventTypes = []
        for op in self.operations:
            if(op.eventType not in eventTypes):
                eventTypes.append(op.eventType)

        with self.g.subgraph(name='cluster_Legend',
                             node_attr={'shape': 'box',
                                        'style': self.nodestyle,
                                        'labeljust': 'l',
                                        'fontsize': '12'},
                             graph_attr={'label': 'LEGEND', 'labeljust': 'l', 'tooltip': 'LEGEND'}) \
                as legend:
            for eventType in eventTypes:
                legend.node(eventType, label=eventType,
                            color=self._eventTypeColor(eventType), fillcolor=self._opFillColor(eventType))

    def _buildGraph(self, g: graphviz.Digraph) -> None:
        self.prevNode = None
        prevNode = self.prevNode

        for idx, op in enumerate(self.operations):
            try:
                if(op.operationAction == 'CODE_UNIT_STARTED'):
                    print(op.name)
                if(op.parent is None and idx > 0):
                    raise(Exception(f'Operation {op.name} has no parent'))

                if(prevNode is not None and prevNode.idx == op.idx):
                    continue

                opName = op.name.split(':')[0] if not op.name.startswith(
                    'apex:') and not isinstance(op, FlowOperation) else op.name
                nodeId = self._getOpNodeId(op)
                parentNodeId = self._getOpNodeId(
                    prevNode) if prevNode is not None else 'start'
                parentOpName = prevNode.name if prevNode is not None else 'start'
                nodeTT = f'Line [{op.lineNumber}]\n   {op.eventType}'

                if(self.options.redact):

                    if(isinstance(op, FatalErrorOp)):
                        nodeTT += f'\n   {op.name}' if op.name.startswith(
                            'System.LimitException:') else f'\n   {opName}'

                    else:
                        opName = f'{op.eventType}\nuid{op.nodeId}'
                        nodeTT += f'\n   {op.nodeId}'
                        parentOpName = parentNodeId

                else:
                    nodeTT += f'\n   Operation: {op.name}'

                urlId = f'lognode{nodeId}'
                opName = opName.replace('<', '&lt;').replace('>', '&gt;')
                # create and style the nodes
                g.node(nodeId, label=f'<{opName}<BR ALIGN="LEFT"/><font POINT-SIZE="8"><b><sub>{op.eventType}</sub></b></font>>',
                       shape='box',
                       color=self._eventTypeColor(op.eventType),
                       fillcolor=self._opFillColor(op.eventType),
                       style=self.nodestyle,
                       tooltip=nodeTT,
                       id=urlId
                       )

                # create and style the edges (arrows to each node)
                lmtstr: str = None
                if(prevNode is not None and prevNode.get('limitsUsageData', None) is not None and not self.options.strict):
                    lmtstr = '\n  Limits Usage Data:\n'
                    lmtstr += '\n  '.join(prevNode.limitsUsageData)

                edgetooltip = f'''Previous Node:
    Line: [{prevNode.lineNumber}]
    Type: {prevNode.eventType}
    Name: {parentOpName}''' if prevNode is not None else ''

                edgetooltip += lmtstr if lmtstr is not None else ''

                edgetooltip += f'''
    -> 
    Next Node:
    {nodeTT}'''
                edgeLabel = f'{idx}' if lmtstr is None else f'{idx} (s)'
                edgeLabelColor = '#000000' if lmtstr is None else '#cc2222'

                if(idx == 0):
                    g.edge('start', nodeId, label=f'{edgeLabel}', tooltip='Start',
                           labeltooltip='Start of the log file', fontcolor=edgeLabelColor)

                elif(idx == len(self.operations) - 1):
                    g.edge(f'{parentNodeId}', nodeId, label=f'{edgeLabel}', color=self._opColor(
                        prevNode.eventType), tooltip=edgetooltip, labeltooltip=edgetooltip, fontcolor=edgeLabelColor, URL=f'#{urlId}')
                    g.edge(f'{nodeId}', 'end', label=f'{len(self.operations)}', color=self._opColor(
                        op.eventType), tooltip=edgetooltip, labeltooltip=edgetooltip)

                else:
                    g.edge(parentNodeId, nodeId,
                           label=f'{edgeLabel}',
                           color=self._opColor(prevNode.eventType),
                           tooltip=edgetooltip,
                           labeltooltip=edgetooltip,
                           fontcolor=edgeLabelColor,
                           URL=f'#{urlId}',
                           constraint='true')

                prevNode = op

            except Exception as e:
                print(f"Error processing operation {op}")
                raise e

    def _getOpNodeId(self, op: Operation) -> str:
        nodeId = op.nodeId
        if(self.useloops == False):
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
                    op._nodeId = f'({len(uniques)-1})'
                    continue
                op._nodeId = f'({idx})'

    def _printStack(self, prefix: str = '', inputStack: list[Operation] = None, suffix: str = ''):
        arr = self.operations if inputStack is None else inputStack
        if(len(arr) == 0):
            raise Exception("No operations found in the log file")
        for op in arr:
            outstr = f' > {op.idx} {prefix} [{op.lineNumber}] {op.eventType} | {op.name} | {op.finished} {suffix}'
            print(outstr)

    def _setparentstack(self, op):
        if(op.get('parent', None) is not None):
            if(op.parent.get('children', None) is None):
                op.parent['children'] = []
                op.parent['children'].append(op)
            else:
                op.parent['children'].append(op)
        else:
            if(op.idx > 0):
                raise Exception(
                    f"Operation should have a parent \n {op.__dict__}")
