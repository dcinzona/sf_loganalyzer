from pprint import pp

from Operations.Invocations.FatalError import FatalErrorOp
from Operations.Invocations.FlowOperation import FlowOperation
from Operations.OpUtils import dynamicDict
from Operations.Operation import Operation
import graphviz

class renderer():

    def __init__(self, *args, **kwargs) -> None:
        self.options = dynamicDict(kwargs)
        fileformat = self.options.format
        self.filename = self.options.logfile
        self.g = graphviz.Digraph(f'{self.filename}', comment=f'Log file visualization for {self.filename}',format=fileformat)
        self.useloops = kwargs.get('useloops', False)
        self.stackProcessMap = {}

    def processStack(self, sortedOperations:list):
        self.operations = sortedOperations
        self.g.strict = self.options.strict
        self.g.engine = self.options.engine
        self.g.graph_attr['rankdir'] = self.options.rankdir
        self.g.attr('node',fontname='helveticaneue-light')
        self.g.attr('edge',fontname='helveticaneue-light')
        if(len(self.operations) == 0):
            raise Exception("No operations found in the log file")
        self._checkIdx()
        self._buildGraph(self.operations)

    def _buildGraph(self, stack):
        g = self.g
        g.node('start', label='START', shape='Mdiamond', style='filled', fillcolor=self.lighten('#00FF00', .4), rank='min', fontsize='16')
        g.node('end', label='END', shape='Msquare', style='filled', fillcolor=self.lighten('#00FF00', .4), rank='max', fontsize='16')
        prevNode = None
        for idx, op in enumerate(self.operations):
            try:
                #idx = op.idx
                if(op.parent is None and idx > 0):
                    raise(Exception(f'Operation {op.name} has no parent'))
                uid = op.nodeId
                if(uid in self.stackProcessMap):
                    self.stackProcessMap[uid].append(op)
                else:
                    self.stackProcessMap[uid] = [op]

                if(prevNode is not None and prevNode.idx == op.idx):
                    continue
                

                opName = op.name.split(':')[0] if not op.name.startswith('apex:') and not isinstance(op, FlowOperation) else op.name
                nodeId = op.nodeId
                parentNodeId = op.parent.nodeId if op.get('parent',None) is not None else 'start'
                #parentNodeId = prevNode.nodeId if op.parent is not None and op.idx == op.parent.idx else parentNodeId
                parentOpName = op.parent.name if op.parent is not None else 'start'
                
                if(self.useloops == False):
                    #make each node operation unique to prevent looping
                    nodeId = f'{op.idx}{nodeId}'
                    parentNodeId = f'{op.parent.idx}{parentNodeId}' if op.parent is not None else 'start'

                nodeTT=f'Line [{op.lineNumber}]\n   {op.eventType}'
                if(self.options.redact):
                    if(isinstance(op, FatalErrorOp)):              
                        nodeTT += f'\n   {op.name}' if op.name.startswith('System.LimitException:') else f'\n   {opName}'
                    else:
                        opName = f'{op.eventType}\nuid{op.nodeId}'
                        nodeTT += f'\n   {op.nodeId}'
                        parentOpName = parentNodeId
                else:
                    nodeTT += f'\n   Operation: {op.name}'
                #create and style the nodes
                g.node(nodeId, label=f'{opName}', 
                shape='box', 
                color=self._opColor(op), 
                fillcolor=self._opFillColor(op), 
                style='filled',
                tooltip=nodeTT,
                )

                #create and style the edges (arrows to each node)

                edgetooltip = f'''Previous Node:
    Line: [{op.parent.lineNumber}]
    Type: {op.parent.eventType}
    Name: {parentOpName}''' if op.parent is not None else ''
                edgetooltip += f'''
    -> 
    Next Node:
    {nodeTT}'''
                if(idx == 0):
                    g.edge('start', nodeId, label=f'{idx}', tooltip='Start', labeltooltip='Start of the log file')
                elif(idx == len(self.operations) - 1):
                    g.edge(parentNodeId, nodeId, label=f'{idx}', color=self._opColor(op.parent), tooltip=edgetooltip, labeltooltip=edgetooltip)
                    g.edge(nodeId, 'end', label=f'{len(self.operations)}', color=self._opColor(op), tooltip=edgetooltip, labeltooltip=edgetooltip)
                else:
                    g.edge(parentNodeId, nodeId, label=f'{idx}', color=self._opColor(op.parent), tooltip=edgetooltip, labeltooltip=edgetooltip)
                
                prevNode = op
                
                continue
                if(op.get('parent', None) is not None):
                    if(op.parent.get('children', None) is None):
                        op.parent['children'] = []
                        op.parent['children'].append(op)
                    else:
                        op.parent['children'].append(op)                
                else:
                    if(op.idx > 0):
                        raise Exception(f"Operation should have a parent \n {op.__dict__}")
            except Exception as e:
                print(f"Error processing operation {op}")
                raise e

    def _opColor(self, op) -> str:
        color = '#888888'    
        if(op.eventType == 'APEX'):
            #add to apex cluster
            color='#0000FF' #blue
            pass
        if(op.eventType == 'TRIGGER'):
            #add to trigger cluster
            color='#800080'
            pass
        if(op.eventType == 'FLOW'):
            #add to flow cluster
            color='#033E3E'
            pass
        if(any(x in op.eventType for x in ['ERROR','EXCEPTION'])):
            #add to flow cluster
            color='#E42217'
            color='#FF0000'
            pass
        if(op.eventType == 'PROCESS BUILDER'):
            #add to flow cluster
            color='#008080'
            pass
        return color.lower()

    def _opFillColor(self, op) -> str:
        return self.lighten(self._opColor(op), .8) 

    def lighten(self, hex, amount):
        """ Lighten an RGB color by an amount (between 0 and 1),

        e.g. lighten('#4290e5', .5) = #C1FFFF
        """
        hex = hex.replace('#','')
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


    
    def _printStack(self, prefix:str='', inputStack:list[Operation]=None, suffix:str=''):
        arr = self.operations if inputStack is None else inputStack
        if(len(arr) == 0):
            raise Exception("No operations found in the log file")
        for op in arr:
            outstr = f' > {op.idx} {prefix} [{op.lineNumber}] {op.eventType} | {op.name} | {op.finished} {suffix}'
            print(outstr)