from Operations.Operation import Operation
from Operations.OperationFactory import OperationsList
import Operations.Invocations as OPS


class nodeArgs(dict):
    def __init__(self, **kwargs):
        super(nodeArgs, self).__init__(**kwargs)
        self.__dict__ = kwargs
        self.name = kwargs.get('name', None)
        self.label = kwargs.get('label', None)
        self.pop('name', None)
        self.pop('label', None)

    def __getattr__(self, name):
        return self.__dict__.get(name, None)

    @property
    def __olddict__(self):
        d = self.kwargs
        d.pop('name', None)
        d.pop('label', None)
        return d


class Node():
    opList: OperationsList
    options: dict

    def __init__(self, opList: OperationsList, options: dict):
        Node.opList = opList
        Node.options = options

    def BuildNode(self, op: Operation, **kwargs):
        # create and style the nodes
        nodepenwidth = '3.0' if len(op.LIMIT_USAGE_FOR_NS) > 0 else '1.0'

        opName = self._getOpName(op)

        nodeId = self._getOpNodeId(op)
        label = f'<{opName}<BR ALIGN="LEFT"/><font POINT-SIZE="8"><b><sub>{op.eventType}</sub></b></font>>'
        tooltip = self._buildNodeTooltipForOp(op)
        tooltip += self._buildLimitsString(op)
        args = nodeArgs(name=nodeId,
                        label=label,
                        shape='box',
                        penwidth=nodepenwidth,
                        id=f'lognode{nodeId}',
                        style='filled, rounded',
                        color=op.color,
                        fillcolor=self.lighten(op.color, .7),
                        tooltip=f'OPERATION:{tooltip}',)

        return args

    def _getOpName(self, op: Operation) -> str:
        if(not Node.options.redact):
            return op.safeName
        return op.safeName if isinstance(op, OPS.FatalErrorOp) else f'UID: {op.nodeId}'

    def BuildEdge(self, op: Operation, **kwargs):
        args = self.BuildNode(op, **kwargs)
        label = f'{op.idx + 1}'
        color = op.color if op.idx == 0 else op.PREV_OPERATION.color
        tooltip = self._buildEdgeTooltip(op)
        fontcolor = '#cc2222' if op.PREV_OPERATION is not None and \
            op.PREV_OPERATION.isClusterOp else '#000000'

        prevNodeId = self._getOpNodeId(
            op.PREV_OPERATION) if op.PREV_OPERATION is not None else 'start'
        headNodeId = self._getOpNodeId(op)
        tailurlId = f'lognode{prevNodeId}'
        headurlId = f'lognode{headNodeId}'
        edge = nodeArgs(color=color,
                        penwidth=args.penwidth,
                        tooltip=tooltip,
                        labeltooltip=tooltip,
                        tailtooltip=tooltip,
                        headtooltip=tooltip,
                        edgetooltip=tooltip,
                        fontcolor=fontcolor,
                        tailURL=f'#{headurlId}',
                        headURL=f'#{tailurlId}',
                        constraint='true')
        edge.tail = prevNodeId
        edge.head = headNodeId
        edge.label = label
        return edge

    def _getOpNodeId(self, op: Operation) -> str:
        return op.nodeId if Node.options.useloops else f'{op.idx}{op.nodeId}'

    def _buildEdgeTooltip(self, op: Operation) -> str:
        if(op.PREV_OPERATION is None):
            return None
        tt = 'PREV OP:'
        tt += self._buildNodeTooltipForOp(op.PREV_OPERATION)
        tt += '\nNEXT OP:'
        tt += self._buildNodeTooltipForOp(op)
        tt += self._buildLimitsString(op.PREV_OPERATION)
        return tt

    def _buildNodeTooltipForOp(self, op: Operation) -> str:
        tt = '\n  LogLine: [{}]'.format(op.lineNumber)
        tt += '\n  Type: {}'.format(op.eventType)
        tt += '\n  Op: {}'.format(self._getOpName(op))
        # tt += self._buildLimitsString(op)
        return tt

    def _buildLimitsString(self, op: Operation) -> str:
        if(op is None or not op.isClusterOp or Node.options.strict):
            return ''

        return '\n\nLimits Usage Data:\nNamespace: {}\n  {}'\
            .format(op.namespace, '\n  '.join(op.LIMIT_USAGE_FOR_NS))

    def lighten(self, hex, amount):
        """ Lighten an RGB color by an amount (between 0 and 1),

        e.g. lighten('#4290e5', .5) = #C1FFFF
        """
        hex = hex.replace('#', '')
        red = min(255, int(hex[0:2], 16) + 255 * amount)
        green = min(255, int(hex[2:4], 16) + 255 * amount)
        blue = min(255, int(hex[4:6], 16) + 255 * amount)
        return "#%X%X%X" % (int(red), int(green), int(blue))
