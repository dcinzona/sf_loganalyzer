from pprint import pp
from Operations.OpUtils import dynamicDict
from Operations.Operation import Operation
import graphviz

class renderer():

    def __init__(self, filename:str='') -> None:
        self.g = graphviz.Digraph('LogViz', comment=f'Log file visualization for {filename}',format='svg')
        self.useloops = True

    def processStack(self, sortedOperations:list):
        g = self.g
        
        self.operations = sortedOperations
        if(len(self.operations) == 0):
            raise Exception("No operations found in the log file")
        self._checkIdx()
        # self.stackProcessMap = {}
        g.node('start', label='start', shape='Mdiamond')
        g.node('end', label='end', shape='Msquare')
        for op in self.operations:   
            idx = op.idx
            # if(uid in self.stackProcessMap):
            #     self.stackProcessMap[uid].append(op)
            # else:
            #     self.stackProcessMap[uid] = [op]
            if(op.eventType == 'APEX'):
                #add to apex cluster
                color='0.6 0.700 0.700'
                pass
            if(op.eventType == 'TRIGGER'):
                #add to trigger cluster
                color='purple'
                pass
            if(op.eventType == 'FLOW'):
                #add to flow cluster
                color='red'
                pass
            if(op.eventType == 'PROCESS BUILDER'):
                #add to flow cluster
                color='orange'
                pass
            
            opType = op.eventType
            opName = op.name.split(':')[0]
            opLabel = opName
            nodeId = op.nodeId
            parentNodeId = op.parent.nodeId if op.parent is not None else 'start'
            
            if(self.useloops == False):
                nodeId = f'{op.idx}{nodeId}'
                parentNodeId = f'{op.idx}{parentNodeId}'

            #create and style the nodes
            g.node(nodeId, label=opLabel, shape='box', color=color)

            #create and style the edges (arrows to each node)
            if(idx == 0):
                g.edge('start', nodeId, label=f's_{op.idx}', color=color)
                continue
            
            elif(idx == len(self.operations) - 1):
                g.edge(nodeId, 'end', label=f's_{op.idx}', color=color)
            else:
                g.edge(parentNodeId, nodeId, label=f's_{op.idx}', color=color)
            
            continue
            if(op.get('parent', None) is not None):
                if(op.parent.get('children', None) is None):
                    op.parent['children'] = []
                    op.parent['children'].append(op)
                else:
                    op.parent['children'].append(op)
                #print(f'{op.parent.idx}: [{op.parent.lineNumber}] {op.parent.nodeId}\n  {op.idx}[{op.lineNumber}] {op.nodeId}')
            else:
                #print(f'PARENT NOT IN NODE: {op.idx}[{op.lineNumber}] {op.nodeId}')
                if(op.idx > 0):
                    raise Exception(f"Operation should have a parent \n {op.__dict__}")
        
        g.view()
        # for op in self.operations:
        #     if(op.children is not None):
        #         for child in op.children:
        #             g.edge(op.nodeId, child.nodeId)




        # for uid in self.stackProcessMap:
        #     print(f'{uid}')          
        #     self._printStack('=>',self.stackProcessMap[uid],'')


    
    def _checkIdx(self) -> None:
        if(len(self.operations) == 0):
            raise Exception("No operations found in the log file")
        if('idx' not in self.operations[0]):
            for idx, op in enumerate(self.operations):
                op['idx'] = idx

    
    def _printStack(self, prefix:str='', inputStack:list[Operation]=None, suffix:str=''):
        arr = self.operations if inputStack is None else inputStack
        if(len(arr) == 0):
            raise Exception("No operations found in the log file")
        for op in arr:
            outstr = f' > {op.idx} {prefix} [{op.lineNumber}] {op.eventType} | {op.name} | {op.finished} {suffix}'
            print(outstr)