from scallionDB.parser.constants import *
from scallionDB.parser.selection import Operator
from random import randint

_and = Operator('_and')
_or = Operator('_or')

def generateID():
    return "%09x" % randint(0,10**11)

def evaluate(op1,op2,operator):
    if operator == _and:
        return op1 & op2
    if operator == _or:
        return op1 | op2
				

def filterByRelation(keys,value,operator):
    if operator not in relational:
        raise ValueError("Comaparison should be made with one of %s" %str(relational))
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

def filterByReference(nodes,ref):
    if ref not in reference:
        raise ValueError("Reference should be one of %s" %str(reference))
    if ref =='ANCESTOR':
        return nodes[:-1]
    elif ref == 'PARENT':
        if len(nodes) > 1:
            return [nodes[-2]]
        else:
            return []
    elif ref == 'SELF':
        return [nodes[-1]]
    elif ref == 'CHILDREN':
        return nodes[-1]['_children']
    else:
        retNodes = []
        for node in nodes[-1]['_children']:
            retNodes.extend(flattenTree(node))
        return retNodes
		
def flattenTree(tree):
    nodes = []
    traverser = traverse(tree)
    while True:
        try:	
            nodes.append(traverser.next())
        except StopIteration:
            break
    return nodes
    
def traverse(tree):
    if not tree.has_key('_children'):
        tree['_children'] = []
    yield tree
    nodeQ = []
    nodeQ.extend(tree['_children'])
    i = 0
    while i < len(nodeQ):
        node = nodeQ[i]
        if not node.has_key('_children'):
            node['_children'] = []
        yield node
        nodeQ.extend(node['_children'])
        i += 1
    

           
		

    