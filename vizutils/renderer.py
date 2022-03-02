from pprint import pformat
from Operations.Cluster import Cluster
from Operations.OpUtils import dynamicDict
from Operations.Operation import Operation
from Operations.OperationFactory import OperationsList
from vizutils.utils.RenderUtils import Node, nodeArgs
import graphviz


class renderer:

    operations: list[Operation] = []

    @property
    def graphLabelText(self) -> str:
        return f"Log file visualization for {self.filename}"

    @property
    def graphAttrs(self):
        return {
            "label": f'<<FONT POINT-SIZE="28">{self.graphLabelText}</FONT>>',
            "tooltip": "",
            "labeljust": "l",
            "outputorder": "nodesfirst",
            # 'margin': '24.0',
            "rank": "same",
            # 'style': "invis",
            "ordering": "out",
            "rankdir": self.options.rankdir,
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
        # attrs['style'] = 'invis'
        attrs["rank"] = "same"
        attrs["nojustify"] = "true"
        return attrs

    def __init__(self, *args, **kwargs) -> None:
        self.options = dynamicDict(kwargs)
        self.nodestyle = "filled, rounded"
        fileformat = self.options.format
        self.filename = self.options.logfile
        self.g = graphviz.Digraph(
            "SFLogGraph",
            filename=f"{self.filename}.gv",
            comment=self.graphLabelText,
            graph_attr=self.graphAttrs,
            format=fileformat,
        )
        self.useloops = self.options.useloops  # kwargs.get('useloops', False)
        self.g.strict = self.options.strict
        self.g.engine = self.options.engine
        self.g.attr("node", fontname="helveticaneue-light,Helvetica,Arial,sans-serif")
        self.g.attr("edge", fontname="helveticaneue-light,Helvetica,Arial,sans-serif")

    def _addDebugToGraph(self, graph: graphviz.Digraph, **kwargs):
        if graph is not None and self.options.debug:
            # with graph.subgraph(name=f'cluster_DEBUG_{graph.name}', graph_attr=self.subgraphAttrs) as g:
            #     g.node(f'debug_{graph.name}', label=pformat(graph.graph_attr, indent=4),
            #            shape='plaintext', style='filled', fontsize='16')\
            #         if str(graph.graph_attr) != '{}' else None
            # graph.edge(f'debug_{graph.name}', f'{graph.name}', taillabel=pformat(
            #     graph.graph_attr, indent=4), labeljust='l', fontsize='16')
            txt = (
                f"\n{graph.name} attrs: {pformat(graph.graph_attr, indent=4, depth=2)}"
            )
            print(txt)
            # self.g.node(f'debug_{graph.name}', label=txt,
            #             shape='box', style='filled,rounded')

    def _clearlabels(self, g: graphviz.Digraph):
        g.attr(label="")
        g.attr(tooltip="")

    def processClusters(self, clusterOps: list[Cluster]):
        self.clusters = clusterOps
        if self.clusters is None or len(self.clusters) == 0:
            raise Exception("No clustered operations found in the log file")

        for cluster in self.clusters:
            print(f"Processing cluster {cluster.name}")
            self._processCluster(cluster)
        pass

    def _processCluster(self, cluster: Cluster):
        with self._subgraph(
            self.g, f"cluster_{cluster.name}", graph_attr=self.subgraphAttrs
        ) as g:
            for idx, op in enumerate(cluster.operations):
                self._validateOperations(op, idx)
                self._loadNodesAndEdgesIntoGraph(g, op, idx, None)

    def processStack(self, opsList: OperationsList):
        self.operations = opsList
        self.nodeUtils = Node(self.operations, self.options)

        if len(self.operations) == 0:
            raise Exception("No operations found in the log file")

        self._checkIdx()

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
        clusterIdx = 0
        subclusters = [g]
        for idx, op in enumerate(self.operations):
            self._validateOperations(op, idx)
            try:
                self._loadNodesAndEdgesIntoGraph(subclusters[-1], op, idx, clusterIdx)
            except Exception as e:
                print(f"Error processing operation {op}")
                raise e

    def _loadNodesAndEdgesIntoGraph(
        self, g: graphviz.Digraph, op: Operation, idx: int, clusterIdx: int = 0
    ) -> None:
        nodeargs = self.nodeUtils.BuildNode(op=op)
        g.node(nodeargs.name, nodeargs.label, **nodeargs)
        edgeargs = self.nodeUtils.BuildEdge(op=op)
        isLastOp = op == self.operations[-1]
        if isLastOp:
            self._addEdge(g, edgeargs)
            g.edge(edgeargs.head, "end", str(len(self.operations) + 1), **edgeargs)
        elif idx == 0:
            g.edge("start", edgeargs.head, str(idx + 1), **edgeargs)
        else:
            self._addEdge(g, edgeargs)

    def _addEdge(self, g: graphviz.Digraph, args: nodeArgs) -> None:
        g.edge(args.tail, args.head, args.label, **args)

    def _validateOperations(self, op: Operation, idx: int) -> None:
        if op.PREV_OPERATION is None and idx > 0:
            op.PREV_OPERATION = self.operations[idx - 1]
            # raise(Exception(f'Operation [{idx}] {op.name} has no previous operation'))
        if op.NEXT_OPERATION is None and idx < len(self.operations) - 1:
            op.NEXT_OPERATION = self.operations[idx + 1]
            # raise(Exception(f'Operation [{idx}] {op.name} has no next operation'))

        if op.PREV_OPERATION is not None and op.PREV_OPERATION.eventId == op.eventId:
            raise (
                Exception(
                    f"Operation [{idx}] {op.name} is a duplicate of [{op.PREV_OPERATION.name}]"
                )
            )

        if op.NEXT_OPERATION is not None and op.eventId == op.NEXT_OPERATION.eventId:
            raise (
                Exception(
                    f"Operation [{idx}] {op.name} is a duplicate of [{op.NEXT_OPERATION.name}]"
                )
            )

    def _checkIdx(self) -> None:
        if len(self.operations) == 0:
            raise Exception("No operations found in the log file")

        if "idx" not in self.operations[0]:
            for idx, op in enumerate(self.operations):
                op["idx"] = idx

        if self.options.redact or True:
            uniques = []

            for op in self.operations:
                idx = uniques.index(op.nodeId) if op.nodeId in uniques else -1

                if idx == -1:
                    uniques.append(f"{op.nodeId}")
                    op._nodeId = f"{op.__class__.__name__}({len(uniques)-1})"
                    continue

                op._nodeId = f"{op.__class__.__name__}({idx})"

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
