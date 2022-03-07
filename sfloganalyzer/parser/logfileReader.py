import os
import sfloganalyzer.Operations as Operations
import sfloganalyzer.options as options


class reader:

    lineCount: int = 0
    loglines: list[str] = []
    clusters: list[Operations.LogLine] = []
    operations: Operations.OperationsList = []

    @property
    def logReversed(self):
        return list(reversed(self.loglines))

    def __init__(self, **kwargs):
        self.logfile = options.logfile
        self.loglines = []
        self.lineCount = 0
        self.operations = []
        self.logpath = os.path.abspath(self.logfile)
        self.filename = os.path.basename(self.logpath)
        self.inputfileDir = os.path.dirname(os.path.abspath(self.logpath))
        self.factory = Operations.OperationFactory()
        self.operations = self.factory.OPERATIONS
        self.limitUsageLines = []
        self.clusters = []

    def read(self):
        codeunitList: list[Operations.LogLine] = []
        with open(self.logpath) as infile:
            # for tracking actual log lines in the file vs operations
            self.lineCount = 0
            self.lastValidLine = None  # for tracking limits lines
            # for processing lines that were technically invalid
            # (i.e. limits lines with no timestamp)
            self.processedInvalid = False
            # for getting the log line for the last code unit entered
            # (defined by finished)
            self.getNextCodeUnitFinished = False
            # need to keep track of codeunits for clustering
            for line in infile:
                self.lineCount += 1  # we read a line
                # will generate a logline object instance if this is a
                # valid line (timestamp and |)
                isValid, ll = Operations.LogLine.isValidLine(
                    line.strip(), self.lineCount
                )
                if isValid:
                    # cluster tracking
                    if ll.lineSplit[1] == "CODE_UNIT_STARTED":
                        codeunitList.append(ll)
                    elif ll.lineSplit[1] == "CODE_UNIT_FINISHED":
                        lastCodeUnitLine = codeunitList.pop()

                    if self.processedInvalid is True:
                        # finished processing lines that did not have
                        # a timestamp and now processing the next valid line
                        # (so we need to reset the flag and process the last
                        #  valid line if it's a limits line)
                        self.processedInvalid = False
                        if self.lastValidLine.isLimitsLine():
                            self.limitUsageLines.append(self.lastValidLine.copy())
                            self.getNextCodeUnitFinished = True
                            pass

                    self.lastValidLine = ll  # .copy()
                    self.loglines.append(line)
                    self.factory.generateOperation(ll)

                    if (
                        self.getNextCodeUnitFinished is True
                        and ll.lineSplit[1] == "CODE_UNIT_FINISHED"
                        and len(self.limitUsageLines) > 0
                    ):

                        self.getNextCodeUnitFinished = False
                        # this is the line range of the cluster
                        cluster = Operations.Cluster(
                            start=int(lastCodeUnitLine.lineNumber),
                            end=int(ll.lineNumber),
                        )
                        cluster.name = ll.lineSplit[-1]

                        # add the limits lines to the cluster instance
                        for ln in self.limitUsageLines:
                            ns = ln.lineSplit[-2]
                            cluster.data[ns] = [
                                x.strip() for x in ln.additionalLines if x.strip() != ""
                            ]

                        self.clusters.append(cluster)
                        self.limitUsageLines.clear()

                    self.processedInvalid = False

                else:
                    # line didn't have a timestamp or pipe character
                    if (
                        self.lastValidLine is not None
                        and self.lastValidLine.isLimitsLine()
                    ):
                        # this is a limits line that has no timestamp
                        self.lastValidLine.addLine(line)
                        self.processedInvalid = True

            # self.clusters = sorted(self.clusters, key=lambda x: x.start)
            # self.rootClusterStack = ClusterStack()
            # self.rootClusterStack.clusters = self.clusters
            # self.operations = []
            for idx, cluster in enumerate(self.clusters):
                cluster.id = f"cluster{idx}"
                cluster.operations = [
                    op.clone()
                    for op in self.operations
                    # op for op in self.operations
                    if op.lineNumber >= cluster.start and op.lineNumber < cluster.end
                ]

                for op in cluster.operations:
                    if op.lineNumber == cluster.start:
                        op_ns = op.namespace
                        op.LIMIT_USAGE_FOR_NS = cluster.data.get(op_ns, [])

                        print(op_ns) if options.debug else None
                        print(op.LIMIT_USAGE_FOR_NS[0]) if options.debug else None
                    if op.get("cluster", None) is None:
                        op.cluster = cluster
                        op.clusterId = op.cluster.id
                        op._nodeId = f"{op.cluster.id}_{op.nodeId}"

                    print(
                        f"\t[{op.lineNumber}] {op.name} | {op.clusterId}"
                    ) if options.debug else None

            for op in self.operations:
                if op.get("clusterId", None) is None:
                    for cluster in self.clusters:
                        if (
                            op.lineNumber >= cluster.start
                            and op.lineNumber < cluster.end
                        ):
                            op.cluster = cluster
                            op.clusterId = op.cluster.id
                            op._nodeId = f"{op.cluster.id}_{op.nodeId}"
                            print(
                                f"\t[{op.lineNumber}] {op.name} | {op.clusterId} | {op.nodeId}"
                            )
                else:
                    print(op.nodeId) if options.debug else None

            self.clusters = list(filter(lambda n: len(n.operations) > 0, self.clusters))

        if options.debug:
            openOps = 0
            opCountsByType = {}
            for idx, op in enumerate(self.operations):
                if op.finished is False:
                    openOps += 1
                    print(
                        f'{idx} [{op.lineNumber}] "{op.name}" \
                        <{op.eventId}> is not finished'
                    )
                clsName = op.__class__.__name__
                if isinstance(op, Operations.FlowOperation):
                    clsName = op.eventType
                opCountsByType.setdefault(clsName, 0)
                opCountsByType[clsName] += 1

            if openOps > 0:
                print(f"{openOps} operations are not finished")

            print("\nCounts by type of operation:")
            for k, v in opCountsByType.items():
                print(f"{k}: {v}")
                # exit(1)

    def getLastOperationByAttribute(self, attr, value):
        for op in reversed(self.operations):
            if getattr(op, attr) == value:
                return op
        return None

    def _sortStack(self):
        # sorted(Operation.OPSTACK, key=lambda x: x["lineNumber"])
        self.operations = self.factory.OPERATIONS
        return self.operations
