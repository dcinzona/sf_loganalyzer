import os
from Operations.Invocations.FlowOperation import FlowOperation
from Operations.LogLine import LogLine, Cluster
from Operations.OpUtils import dynamicDict
from Operations.OperationFactory import OperationFactory


class reader:

    lineCount: int = 0
    loglines: list[str] = []
    clusters: list[LogLine] = []

    @property
    def logReversed(self):
        return list(reversed(self.loglines))

    def __init__(self, **kwargs):
        self.options = dynamicDict(kwargs)
        self.logfile = self.options.logfile
        self.loglines = []
        self.lineCount = 0
        self.operations = []
        self.logpath = os.path.abspath(self.logfile)
        self.filename = os.path.basename(self.logpath)
        self.inputfileDir = os.path.dirname(os.path.abspath(self.logpath))
        self.factory = OperationFactory(**self.options)
        self.operations = self.factory.OPERATIONS
        self.limitUsageLines = []
        self.clusters = []

    def read(self):
        codeunitList: list[LogLine] = []
        with open(self.logpath) as infile:
            self.lineCount = 0  # for tracking actual log lines in the file vs operations
            self.lastValidLine = None  # for tracking limits lines
            # for processing lines that were technically invalid (i.e. limits lines with no timestamp)
            self.processedInvalid = False
            # for getting the log line for the last code unit entered (defined by finished)
            self.getNextCodeUnitFinished = False
            # need to keep track of codeunits for clustering
            for line in infile:
                self.lineCount += 1  # we read a line
                # will generate a logline object instance if this is a valid line (timestamp and |)
                isValid, ll = LogLine.isValidLine(line.strip(), self.lineCount)
                if(isValid):
                    # cluster tracking
                    if(ll.lineSplit[1] == 'CODE_UNIT_STARTED'):
                        codeunitList.append(ll)
                    elif(ll.lineSplit[1] == 'CODE_UNIT_FINISHED'):
                        lastCodeUnitLine = codeunitList.pop()

                    if(self.processedInvalid is True):
                        # finished processing lines that did not have a timestamp and now processing the next valid line
                        # (so we need to reset the flag and process the last valid line if it's a limits line)
                        self.processedInvalid = False
                        if(self.lastValidLine.isLimitsLine()):
                            self.limitUsageLines.append(
                                self.lastValidLine.copy())
                            self.getNextCodeUnitFinished = True
                            pass

                    self.lastValidLine = ll.copy()
                    self.loglines.append(line)
                    self.factory.createOrderedOperation(ll)

                    if(self.getNextCodeUnitFinished and ll.lineSplit[1] == 'CODE_UNIT_FINISHED' and len(self.limitUsageLines) > 0):
                        self.getNextCodeUnitFinished = False
                        cluster = Cluster(
                            start=int(lastCodeUnitLine.lineNumber), end=int(ll.lineNumber))  # this is the line range of the cluster
                        cluster.name = ll.lineSplit[-1]

                        # add the limits lines to the cluster instance
                        for ln in self.limitUsageLines:
                            ns = ln.lineSplit[-2]
                            cluster.data[ns] = [
                                x.strip() for x in ln.additionalLines if x.strip() != '']

                        self.clusters.append(cluster)
                        self.limitUsageLines.clear()

                    self.processedInvalid = False

                else:
                    # line didn't have a timestamp or pipe character
                    if(self.lastValidLine is not None and self.lastValidLine.isLimitsLine()):
                        self.lastValidLine.addLine(line)
                        self.processedInvalid = True

            if(len(self.clusters) > 14):
                for idx, c in enumerate(self.clusters):
                    print(c.data)
                    print(idx)
                    # print(c) if c.data['(default)'][0].strip(
                    # ) == 'Number of SOQL queries: 2 out of 100' else print(c)
            # exit() if len(self.clusters) > 20 else None

            # self.clusters = sorted(self.clusters, key=lambda x: x.start)
            for idx, cluster in enumerate(self.clusters):
                cluster.id = f'cluster{idx}'
                cluster.operations = [
                    op for op in self.operations if op.lineNumber >= cluster.start and op.lineNumber < cluster.end]

                # pp(f'({cluster.id})[{cluster.start} - {cluster.end}] {cluster.name} | Child Ops: {len(cluster.operations)}')
                for op in cluster.operations:
                    if(op.lineNumber == cluster.start):
                        op_ns = op.namespace
                        op.LIMIT_USAGE_FOR_NS = cluster.data.get(op_ns, [])
                        print(op_ns)
                        print(op.LIMIT_USAGE_FOR_NS[0])
                    op.cluster = cluster
                    op.clusterId = op.cluster.id
                    print(f'\t[{op.lineNumber}] {op.name} | {op.clusterId}')

            self.clusters = list(filter(lambda n: len(
                n.operations) > 0, self.clusters))

        if(self.options.get('debug', False)):
            openOps = 0
            opCountsByType = {}
            for idx, op in enumerate(self.operations):
                if(op.finished == False):
                    openOps += 1
                    print(
                        f'{idx} [{op.lineNumber}] "{op.name}" <{op.eventId}> is not finished')
                clsName = op.__class__.__name__
                if(isinstance(op, FlowOperation)):
                    clsName = op.eventType
                opCountsByType.setdefault(clsName, 0)
                opCountsByType[clsName] += 1

            if(openOps > 0):
                print(f'{openOps} operations are not finished')

            print('\nCounts by type of operation:')
            for k, v in opCountsByType.items():
                print(f'{k}: {v}')
                # exit(1)

    def getLastOperationByAttribute(self, attr, value):
        for op in reversed(self.operations):
            if(getattr(op, attr) == value):
                return op
        return None

    def _sortStack(self):
        # sorted(Operation.OPSTACK, key=lambda x: x["lineNumber"])
        self.operations = self.factory.OPERATIONS
        return self.operations
