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
        self.nodes = []
        self.edges = []

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
        self.nodeUtils = RenderUtils.NodeUtils(self.operations)
        self._buildElements(self.g)
        # Add the nodes and edges to the graph
        with self.g.subgraph(name="cluster_Log", graph_attr=self.subgraphAttrs) as g:
            self._addDebugToGraph(g, graph_attr=self.subgraphAttrs)
            self._clearlabels(g)

            with g.subgraph(name="cluster_STACK", graph_attr=self.subgraphAttrs) as dg:
                # self._addDebugToGraph(g, graph_attr=self.subgraphAttrs)
                self._clearlabels(dg)
                self._loadNodesAndEdgesIntoGraph(dg)

    def _buildElements(self, g: graphviz.Digraph) -> None:

        self.nodes.append(
            RenderUtils.NodeElement(
                name="start",
                label="START",
                shape="invhouse",
                style="filled",
                fillcolor=self.nodeUtils.lighten("#00FF00", 0.4),
                fontsize="16",
            )
        )

        if len(self.operations) == 0:
            raise Exception("No operations found in the log file")

        self._addDebugToGraph(self.g, graph_attr=self.subgraphAttrs)

        # Add the nodes and edges to the object lists
        for op in self.operations:
            try:
                node = self.nodeUtils.BuildNode(op=op)
                self.nodes.append(node)
                edge = self.nodeUtils.BuildEdge(op=op)
                self.edges.append(edge)
            except Exception as e:
                print(e)
                print(f"Error processing operation {op}")
                raise e

        self.nodes.append(
            RenderUtils.NodeElement(
                name="end",
                label="END",
                shape="invhouse",
                style="filled",
                fillcolor=self.nodeUtils.lighten("#00FF00", 0.4),
                fontsize="16",
            )
        )

        edge = self.nodeUtils.BuildEdge(self.operations[-1])
        edge.tail = str(edge.head)
        edge.head = "end"
        edge.label = self.operations[-1].idx_label
        self.edges.append(edge)

    def _loadNodesAndEdgesIntoGraph(self, g: graphviz.Digraph) -> None:
        if options.format == "json":
            return
        for node in self.nodes:
            g.node(node.name, node.label, **node)
        for edge in self.edges:
            g.edge(edge.tail, edge.head, **edge)

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
