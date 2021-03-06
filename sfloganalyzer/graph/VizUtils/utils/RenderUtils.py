from typing import Any
from sfloganalyzer.Operations.Operation import Operation
from sfloganalyzer.Operations.OperationFactory import OperationsList
import sfloganalyzer.Operations.Invocations as OPS
import sfloganalyzer.options as options


class NodeElement(dict):
    name: str
    label: str

    def __init__(self, **kwargs):
        super(NodeElement, self).__init__(**kwargs)
        self.__dict__ = kwargs
        if options.format != "json":
            self.name = kwargs.get("name", None)
            self.label = kwargs.get("label", None)
            self.pop("name", None)
            self.pop("label", None)

    def __getattr__(self, name):
        return self.__dict__.get(name, None)

    @property
    def __olddict__(self):
        d = self.kwargs
        d.pop("name", None)
        d.pop("label", None)
        return d


class EdgeElement(dict):
    tail: str = None
    head: str = None
    label: str = None

    def __init__(self, **kwargs):
        super(EdgeElement, self).__init__(**kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name, None)

    def __setattr__(self, __name: str, __value: Any) -> None:
        super(EdgeElement, self).__setattr__(__name, __value)
        self[__name] = __value


class NodeUtils:
    opList: OperationsList
    options: dict

    def __init__(self, opList: OperationsList):
        NodeUtils.opList = opList

    def BuildNode(self, op: Operation, **kwargs) -> NodeElement:
        # create and style the nodes
        nodepenwidth = "3.0" if len(op.LIMIT_USAGE_FOR_NS) > 0 else "1.0"

        opName = self._getOpName(op)

        nodeId = self._getOpNodeId(op)
        label = f"{opName}\n{op.eventType}"

        args = NodeElement(
            name=nodeId,
            label=label,
            shape="box",
            penwidth=nodepenwidth,
            id=f"lognode{nodeId}",
            style="filled, rounded",
            color=op.color,
            fillcolor=self.lighten(op.color, 0.7),
        )

        if options.format == "json":
            args["op"] = op.toDict()

        if options.format == "dot":
            return args

        tooltip = self._buildNodeTooltipForOp(op)
        tooltip = (
            f"{tooltip}{self._buildLimitsString(op)}" if tooltip is not None else None
        )
        args["tooltip"] = tooltip
        args.label = f'<{opName}<BR ALIGN="LEFT"/><font POINT-SIZE="8"><b><sub>{op.eventType}</sub></b></font>>'

        return args

    def _getOpName(self, op: Operation) -> str:
        if not options.redact:
            return op.safeName
        return op.safeName if isinstance(op, OPS.FatalErrorOp) else f"UID: {op.nodeId}"

    def BuildEdge(self, op: Operation, **kwargs) -> EdgeElement:
        args = self.BuildNode(op, **kwargs)
        label = f"{op.idx + 1}"
        color = op.color if op.idx == 0 else op.PREV_OPERATION.color

        fontcolor = (
            "#cc2222"
            if op.PREV_OPERATION is not None and op.PREV_OPERATION.isClusterOp
            else "#000000"
        )

        prevNodeId = (
            self._getOpNodeId(op.PREV_OPERATION)
            if op.PREV_OPERATION is not None
            else "start"
        )
        headNodeId = self._getOpNodeId(op)
        tailurlId = f"lognode{prevNodeId}"
        headurlId = f"lognode{headNodeId}"
        edge = EdgeElement(
            color=color,
            penwidth=args.penwidth,
            fontcolor=fontcolor,
            constraint="true",
        )
        edge.tail = prevNodeId
        edge.head = headNodeId
        edge.label = label
        edge.tooltip = self._buildEdgeTooltip(op)
        edge.headurlId = headurlId
        edge.tailurlId = tailurlId
        if options.format == "svg":
            tooltip = edge.tooltip
            edge["tooltip"] = tooltip
            edge["labeltooltip"] = tooltip
            edge["tailtooltip"] = tooltip
            edge["headtooltip"] = tooltip
            edge["edgetooltip"] = tooltip
            edge["tailURL"] = f"#{headurlId}"
            edge["headURL"] = f"#{tailurlId}"

        return edge

    def _getOpNodeId(self, op: Operation) -> str:
        return op.nodeId if options.useloops else f"{op.idx}{op.nodeId}"

    def _buildEdgeTooltip(self, op: Operation) -> str:
        if options.format == "dot":
            return None
        if op.PREV_OPERATION is None:
            return None
        tt = "PREV OP:"
        tt += self._buildNodeTooltipForOp(op.PREV_OPERATION)
        tt += "\nNEXT OP:"
        tt += self._buildNodeTooltipForOp(op)
        tt += self._buildLimitsString(op.PREV_OPERATION)
        return tt

    def _buildNodeTooltipForOp(self, op: Operation) -> str:
        if options.format == "dot":
            return None
        tt = "\n  LogLine: [{}]".format(op.lineNumber)
        tt += "\n  Type: {}".format(op.eventType)
        tt += "\n  Op: {}".format(self._getOpName(op))
        # tt += self._buildLimitsString(op)
        return tt

    def _buildLimitsString(self, op: Operation) -> str:
        if options.format == "dot":
            return None
        if op is None or not op.isClusterOp or options.strict:
            return ""

        return "\n\nLimits Usage Data:\nNamespace: {}\n  {}".format(
            op.namespace, "\n  ".join(op.LIMIT_USAGE_FOR_NS)
        )

    def lighten(self, hex, amount):
        """Lighten an RGB color by an amount (between 0 and 1),

        e.g. lighten('#4290e5', .5) = #C1FFFF
        """
        hex = hex.replace("#", "")
        red = min(255, int(hex[0:2], 16) + 255 * amount)
        green = min(255, int(hex[2:4], 16) + 255 * amount)
        blue = min(255, int(hex[4:6], 16) + 255 * amount)
        return "#%X%X%X" % (int(red), int(green), int(blue))
