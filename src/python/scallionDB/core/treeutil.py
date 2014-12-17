from scallionDB.parser.constants import *
from scallionDB.parser.selection import Operator
from random import randint
import json, re

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
    if operator == '_regex':
        str_keys = [a for a in keys if isinstance(a,basestring)]
        return set(filter((lambda x: re.search(value,x)), str_keys))	
		
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
		
def reduceToNode(node,num):
    if not node:
        return None
    if not node.has_key('_children'):
        return None
    if len(node['_children'])  < num+1 :
        return None
    return node['_children'][num]  

		
def treebreaker(tree):	
	

    childStack = []
    if not tree.has_key('_children'):
        yield json.dumps(tree)
        raise StopIteration
    while True:
        node = reduce(reduceToNode, childStack, tree)
        if not node:
            raise StopIteration
        outNode = json.dumps({k:v for k,v in node.items() 
		                      if k!='_children'})

        if node.has_key('_children'):
            if node['_children']:
                parent = node
                outNode = outNode[:-1] +', "_children":['
                if childStack:
                    if childStack[-1] != 0:
                        outNode = ", "+ outNode
                childStack.append(0)
                yield outNode
            else:
                if childStack[-1] != 0:
                    outNode = ", "+ outNode
                yield outNode
                childStack[-1] += 1
                while childStack[-1] == len(parent['_children']):
                    childStack.pop()
                    if not childStack:
                        yield "]}"
                        raise StopIteration
                    parent = reduce(reduceToNode, childStack[:-1], tree)
                    yield "]}"
                    childStack[-1] += 1
        else:
            yield outNode
		
           
		

    