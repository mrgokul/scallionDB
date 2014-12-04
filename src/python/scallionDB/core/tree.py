import json
from scallionDB.parser.selection import Selector, Operator

_and = Operator('_and')
_or = Operator('_or')

class Tree(dict):

    def __init__(self, name):
        self.name = name
		
    def GET(self,expr,attrs=[])
        ids = _getIDs(expr)
        nodes = []
        for id in ids:
            node = _getNode(id)
            if node:
                if attrs:
                    node = {k,v for k,v in node.items() if k in attrs}
                nodes.append(node)
        return nodes
			
    def _getNode(self,id):
        def reduceToNode(node,num):
            if not node:
                return None
            if not node.has_key('_children'):
                return None
            if len(node['_children'])  < num+1 :
                return None
            return node['_children'][num]			
		
        return reduce(reduceToNode, self.pathMap[id], self)
           
		
    def _getIDs(self,expr):
        prefix = Selector(expr).toPrefix()[::-1]
        if len(prefix) == 1:
            return _getID(expr)
        operandStack = []
        i = 0
        while i < len(prefix):
            pop = prefix.pop()
            if isinstance(pop, Operator):
                operand_1 = _getID(operandStack.pop())
                operand_2 = _getID(operandStack.pop())	
	            operandStack.append(_combine(operand_1,operand_2,pop))	
            else:
                operandStack.append(pop)			
            i += 1
        return operandStack[0]
		
    def _combine(op1,op2,operator):
        if operator == _and:
            return op1 & op2
        else:
            returrn op1 | op2
			
    def _getID(self, expr):
        key = expr[0]
        value = expr[1]
        operator = '_eq'
        if isinstance(value,dict):
            operator, value = value.items()
        if key == '_id':
            return set([value['_eq']])
        keys in self.RI[key].keys():
        if operator == '_eq':
            return set(filter((lambda x: x == value), keys))
        if operator == '_neq':
            return set(filter((lambda x: x != value), keys))
        if operator == '_lt':
            return set(filter((lambda x: x < value), keys))
        if operator == '_gt':
            return set(filter((lambda x: x > value), keys))
        if operator == '_lte':
            return set(filter((lambda x: x <= value), keys))
        if operator == '_gte':
            return set(filter((lambda x: x >= value), keys))			
        


		

    