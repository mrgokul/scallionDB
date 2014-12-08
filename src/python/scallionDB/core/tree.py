import json

from scallionDB.parser.selection import Selector, Operator
from treeutil import evaluate, flattenTree, traverse, generateID
from treeutil import filterByRelation, filterByReference 
from copy import deepcopy

import traceback

class Tree(dict):

    def __init__(self, name):
        self.name = name
        self.RI = {}
        self.pathMap = {'_ROOT':[]}
        self.id = '_ROOT'    
        self['_id'] = '_ROOT'		
        self['_children'] = []
		
    def GET(self,expr,ref,attrs=[]):
        ids = self._getAllID(expr)
        getNodes = []
        for id in ids:
            nodes = self._getNodes(id)
            if nodes:
                refNodes = filterByReference(nodes,ref)
                if attrs:
                    if isinstance(attrs,list):
                        if '_id' not in attrs:
                            attrs.append('_id')
                        all = False
                    elif attrs == '*':
                        all = True
                    attrNodes = []
                    for refNode in refNodes:
                        if all:
                            attr = [a for a in refNode.keys() if a != '_children']
                        else:
                            attr = attrs
                        attrNodes.extend([{k:refNode.get(k,None) for k in attr}])
                    refNodes = attrNodes
                getNodes.extend(refNodes)
        return getNodes
			
    def PUT(self,expr,ref,tree={},attrs={}):
        nodes = self.GET(expr,ref)
        if len(nodes) > 1 and tree.has_key('_id'):
            raise KeyError("More than one node to PUT wit same ID")
        treeIDs = []
        for node in nodes:
            if tree:
                try:
                    treeID = self._putTree(node, tree)
                except:
                    raise Exception("Only %s out of %s nodes PUT, %s"
                					%(str(len(treeIDs)), str(len(nodes)), 
									str(treeIDs)))
                treeIDs.append(treeID)
            else:
                if node['_id'] == '_ROOT':
                    continue
                try:
                    self._putAttrs(node, attrs)
                except Exception, e:
                    raise Exception("Only %s out of %s nodes ATTRS applied:, %s"
                					%(str(len(treeIDs)), str(len(nodes)), 
									str(treeIDs)))
                treeIDs.append(node['_id'])
        return treeIDs
		
    def DELETE(self,expr,ref,attrs=[]): 
        nodes = self.GET(expr,ref) 
        treeIDs = []
        for node in nodes:
            if node['_id'] == '_ROOT':
                continue
            if attrs:
                try:
                    self._delAttrs(node,attrs)
                except:
                    raise Exception("Only %s out of %s nodes DELETED, %s"
                					%(str(len(treeIDs)), str(len(nodes)), 
									str(treeIDs)))
                    treeIDs.append(node['_id'])
            else:
                try:
                    self._delTree(node)
                except:
                    traceback.print_exc()
                    raise Exception("Only %s out of %s nodes DELETED, %s"
                					%(str(len(treeIDs)), str(len(nodes)), 
									str(treeIDs)))
                    treeIDs.append(node['_id'])			
        return treeIDs          
			
    def _getNodes(self,id):
        if not self.pathMap.has_key(id):
            return []
        nodes = [self]       
        def reduceToNode(node,num):
            if not node:
                return None
            if not node.has_key('_children'):
                return None
            if len(node['_children'])  < num+1 :
                return None
            nodes.append(node['_children'][num])
            return node['_children'][num]			
        reduce(reduceToNode, self.pathMap[id], self)
        return nodes
           
    def _getAllID(self,expr):
        prefix = Selector(expr).toPrefix()
        if not prefix:
            return set([self.id])
        if len(prefix) == 1:
            return self._getIDset(prefix[0])
        operandStack = []
        while prefix:
            pop = prefix.pop()
            if isinstance(pop, Operator):
                operand_1 = operandStack.pop()
                if isinstance(operand_1, tuple):
                    operand_1 = self._getIDset(operand_1)	
                operand_2 = operandStack.pop()
                if isinstance(operand_2, tuple):
                    operand_2 = self._getIDset(operand_2)						
                computed = evaluate(operand_1,operand_2,pop)
                operandStack.append(computed)	
            else:
                operandStack.append(pop)			
        return operandStack[0]
			
    def _getIDset(self, expr):
        attrKey = expr[0]
        attrValue = expr[1]
        operator = '_eq'
        if isinstance(attrValue,dict):
            operator, attrValue = attrValue.items()[0]
        if attrKey == '_id':
            return set([attrValue])
        matchKeys = filterByRelation(self.RI.get(attrKey,dict()).keys(),
		                             attrValue,operator)
        ids = set()
        for matchKey in matchKeys:
            ids.update(self.RI[attrKey][matchKey])
        return ids
               
    def _putTree(self,here,tree):
        tree = deepcopy(tree)
        parentChildMap = {}  
        attrsMap = {}		
        traverser = traverse(tree)
        while True:

            try:
                node = traverser.next()
            except StopIteration:
                break
            parentID = self._setID(node)
            for k,v in node.iteritems():
                if k!='_id' and k!='_children' and not isinstance(v,dict)\
                    and not isinstance(v,list):
                    if attrsMap.has_key(k):
                        if attrsMap[k].has_key(v):
                            attrsMap[k][v].add(parentID)
                        else:
                            attrsMap[k][v] = set([parentID])
                    else:   			
                        attrsMap[k] = {v:set([parentID])}  				
            children = node['_children']
            if not isinstance(children,list):
                raise TypeError("_children attribute should be of Array Type")
            for num, child in enumerate(children):   
                id = self._setID(child)
                parentChildMap[id] = (parentID,num) 	
  				
				
        parentChildMap[tree['_id']] = (here['_id'],len(here['_children']))			
        here['_children'].append(tree)
        herePath = self.pathMap[here['_id']]
        #treePath = herePath + [len(here['_children'])]
        #self.pathMap[tree['_id']] = treePath
        try:
            for k,v in  parentChildMap.iteritems():
                pathStack = [v[1]]
                while v[0] in parentChildMap:
                    v = parentChildMap[v[0]]
                    pathStack.append(v[1])
                fullPath = herePath + pathStack[::-1]
                self.pathMap[k] = fullPath
            for attr,valMap in attrsMap.iteritems():
                for val, map in valMap.iteritems():			
                    if self.RI.has_key(attr):
                        if self.RI[attr].has_key(val):
                            self.RI[attr][val].update(map)
                        else:
                            self.RI[attr][val] = map
                    else:
                        self.RI[attr] = {val:map} 		
            return tree['_id']
        except Exception, e: 
            self.DELETE(tree)
            raise Exception(e)

    def _putAttrs(self, here, attrs):
        oldAttrs = {k:here[k] for k in attrs.keys() if here.has_key(k)}
        try:		        
            for k,v in attrs.iteritems():
                if oldAttrs.has_key(k):
                    oldVal = oldAttrs[k]
                    if not isinstance(oldVal,dict) and not isinstance(oldVal,list):
                        self.RI[k][oldVal].remove(here['_id'])
                here[k] = v
                if k!='_id' and k!='_children' and not isinstance(v,dict)\
                    and not isinstance(v,list):
                    if self.RI.has_key(k):
                        if self.RI[k].has_key(v):
                            self.RI[k][v].add(here['_id'])
                        else:
                            self.RI[k][v] = set([here['_id']])
                    else:   			
                        self.RI[k] = {v:set([here['_id']])}
        except Exception, e:
            self._delAttrs(here,attrs.keys(),oldAttrs)
            raise Exception(e)
			
    def _delTree(self, node):
        parent = self.GET(json.dumps({'_id':node['_id']}),'PARENT')[0]
        index = parent['_children'].index(node)
        nextSiblings = parent['_children'][(index+1):]
        flatTree = flattenTree(node)
        for tree in flatTree:
            self._delAttrs(tree)
            del self.pathMap[tree['_id']]
        del parent['_children'][index]
        if nextSiblings:
            self.reducePath(nextSiblings)
        
						
    def _delAttrs(self,here,attrs='*',replace={}):
        if attrs == '*':
            attrs = [a for a in here.keys() if a != '_id' and a!='_children']
        for k in attrs:
            if here.has_key(k):
                v = here[k]
                del here[k]
                if k!='_id' and k!='_children' and not isinstance(v,dict)\
                    and not isinstance(v,list):
                    if self.RI.has_key(k):
                        if self.RI[k].has_key(v):
                            self.RI[k][v].remove(here['_id'])
            if replace.has_key(k):
                oldVal = replace[k]
                here[k] = oldVal
                if not isinstance(oldVal,dict) and not isinstance(oldVal,list):
                    self.RI[k][oldVal].add(here['_id'])
					
    def _reducePath(self,siblings):
        index =  len(siblings[0]) - 1
        for sibling in siblings:
            trees = flattenTree(flattenTree(node))
            for tree in trees:
                self.pathMap[index] -= 1			
	   
    def _setID(self,node):
        if not isinstance(node, dict):
            raise TypeError("Node should be Object Type")
        if node.has_key('_id'):
            id = node['_id']
            if self.pathMap.has_key(id):
                raise KeyError('ID %s already present' %id)
        else:
            id = generateID()
            while self.pathMap.has_key(id):
                id = generateID()
            node['_id'] = id
        return id
		

    