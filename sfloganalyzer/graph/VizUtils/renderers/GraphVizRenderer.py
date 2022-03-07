from sfloganalyzer.graph.VizUtils.Renderer import Renderer
from pprint import pformat
from sfloganalyzer.Operations.Operation import Operation
from sfloganalyzer.Operations.OperationFactory import OperationsList
import sfloganalyzer.graph.VizUtils.utils.RenderUtils as RenderUtils
import graphviz
import sfloganalyzer.options as options


class GraphVizRenderer(Renderer):
    @property
    def graphLabelText(self) -> str:
        return f"Log file visualization for {self.filename}"

    @property
    def graphAttrs(self):
        labelTxt = self.graphLabelText
        if options.format == "svg":
            labelTxt = f'<<FONT POINT-SIZE="28">{self.graphLabelText}</FONT>>'
        return {
            "label": labelTxt,
            "tooltip": "",
            "labeljust": "l",
            "outputorder": "nodesfirst",
            "rank": "same",
            "ordering": "out",
            "rankdir": options.rankdir,
            "fontname": "Salesforce,helveticaneue-light,Helvetica,Arial,sans-serif",
            "labelloc": "t",
            "center": "false",
            "pad": "0.5",
            "compound": "true",
        }

    @property
    def subgraphAttrs(self) -> dict:
        attrs = dict(self.graphAttrs)
        attrs.pop("label", None)
        attrs.pop("labelloc", None)
        attrs.pop("labeljust", None)
        attrs.pop("tooltip", None)
        attrs["center"] = "true"
        attrs["style"] = "invis"
        attrs["rank"] = "same"
        attrs["nojustify"] = "true"
        return attrs

    def __init__(self, *args, **kwargs) -> None:
        self.nodestyle = "filled, rounded"
        fileformat = options.format
        self.filename = options.logfile
        self.g = graphviz.Digraph(
            "SFLogGraph",
            filename=f"{self.filename}.gv",
            comment=self.graphLabelText,
            graph_attr=self.graphAttrs,
            format=fileformat,
        )
        self.useloops = options.useloops  # kwargs.get('useloops', False)
        self.g.strict = options.strict
        self.g.engine = options.engine
        self.g.attr("node", fontname="helveticaneue-light,Helvetica,Arial,sans-serif")
        self.g.attr("edge", fontname="helveticaneue-light,Helvetica,Arial,sans-serif")

    def _addDebugToGraph(self, graph: graphviz.Digraph, **kwargs):
        if graph is not None and options.debug:
            txt = (
                f"\n{graph.name} attrs: {pformat(graph.graph_attr, indent=4, depth=2)}"
            )
            print(txt)

    def _clearlabels(self, g: graphviz.Digraph):
        g.attr(label="")
        g.attr(tooltip="")

    def processStack(self, opsList: OperationsList):
        self.operations = opsList
        self.nodeUtils = RenderUtils.Node(self.operations)

        if len(self.operations) == 0:
            raise Exception("No operations found in the log file")

        self._addDebugToGraph(self.g, graph_attr=self.subgraphAttrs)

        with self.g.subgraph(name="cluster_Log", graph_attr=self.subgraphAttrs) as g:
            self._addDebugToGraph(g, graph_attr=self.subgraphAttrs)
            self._clearlabels(g)
            g.node(
                "start",
                label="START",
                shape="invhouse",
                style="filled",
                fillcolor=self.nodeUtils.lighten("#00FF00", 0.4),
                fontsize="16",
            )

            with g.subgraph(name="cluster_STACK", graph_attr=self.subgraphAttrs) as dg:
                # self._addDebugToGraph(g, graph_attr=self.subgraphAttrs)
                self._clearlabels(dg)
                self._buildGraph(dg)

            g.node(
                "end",
                label="END",
                shape="invhouse",
                style="filled",
                fillcolor=self.nodeUtils.lighten("#00FF00", 0.4),
                fontsize="16",
            )

    def _buildGraph(self, g: graphviz.Digraph) -> None:
        subclusters = [g]
        for op in self.operations:
            try:
                self._loadNodesAndEdgesIntoGraph(subclusters[-1], op)
            except Exception as e:
                print(f"Error processing operation {op}")
                raise e

    def _loadNodesAndEdgesIntoGraph(self, g: graphviz.Digraph, op: Operation) -> None:
        nodeargs = self.nodeUtils.BuildNode(op=op)
        g.node(nodeargs.name, nodeargs.label, **nodeargs)
        edgeargs = self.nodeUtils.BuildEdge(op=op)
        isLastOp = op == self.operations[-1]
        if isLastOp:
            self._addEdge(g, edgeargs)
            g.edge(edgeargs.head, "end", None, **edgeargs)
        elif op.idx == 0:
            g.edge("start", edgeargs.head, op.idx_label, **edgeargs)
        else:
            self._addEdge(g, edgeargs)

    def _addEdge(self, g: graphviz.Digraph, args: RenderUtils.nodeArgs) -> None:
        g.edge(args.tail, args.head, args.label, **args)

    def _printStack(
        self, prefix: str = "", inputStack: list[Operation] = None, suffix: str = ""
    ):
        arr = self.operations if inputStack is None else inputStack
        if len(arr) == 0:
            raise Exception("No operations found in the log file")
        for op in arr:
            outstr = f" > {op.idx} {prefix} [{op.lineNumber}] {op.eventType} | {op.name} | {op.finished} {suffix}"
            print(outstr)

    def _setparentstack(self, op):
        if op.get("parent", None) is not None:
            op.parent.setdefault("children", [])
            op.parent["children"].append(op)
        else:
            if op.idx > 0:
                raise Exception(f"Operation should have a parent \n {op.__dict__}")
