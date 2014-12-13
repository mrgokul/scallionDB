import json

from scallionDB.parser.selection import Selector, Operator
from treeutil import evaluate, flattenTree, traverse, generateID
from treeutil import  filterByRelation, treebreaker
from copy import deepcopy

import traceback
import gc

class Tree(dict):

    def __init__(self, name):
        self.name = name
        self.RI = {}
        self.PM = {}
        self.parentChildMap = {}		
        self['_id'] = '_ROOT'		
        self['_children'] = []
		
    def GET(self,expr,ref,attrs=[]):
        ids = self._getAllID(expr)
        getNodes = []
        for id in ids:
            nodes = self._getNodes(id,ref)
            if attrs:
                if isinstance(attrs,list):
                    if '_id' not in attrs:
                        attrs.append('_id')
                    all = False
                elif attrs == '*':
                    all = True
                attrNodes = []
                for node in nodes:
                    if all:
                        attr = [a for a in node.keys() if a != '_children']
                    else:
                        attr = attrs
                    attrNodes.extend([{k:node.get(k,None) for k in attr}])
                nodes = attrNodes
            getNodes.extend(nodes)
        return getNodes
			
    def PUT(self,expr,ref,tree={},attrs={}):
        nodes = self.GET(expr,ref)
        if len(nodes) > 1 and tree.has_key('_id'):
            raise KeyError("More than one node to PUT wit same ID")
        treeIDs = []
        num = len(nodes)
        for node in nodes:
            if tree:
                try:
                    treeID = self._putTree(node, tree, num)
                except:
                    traceback.print_exc()
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
            num -= 1
        return treeIDs
		
    def LOAD(self,path):
        return self.PUT('{}','SELF',json.load(open(path)))
		
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
        gc.collect()				
        return treeIDs          
			
    def _getNodes(self,id,ref):
        if id == '_ROOT':
            return [self]
        if not self.PM.has_key(id):
            return []
        if ref == 'SELF':
            return [self.PM[id]]
        elif ref == 'CHILDREN':
            return self.PM[id]['_children']
        elif ref == 'DESCENDANTS':
            retNodes = []
            for node in self.PM[id]['_children']:
                retNodes.extend(flattenTree(node))
        elif ref == 'PARENT':
            node = self.PM[id]
            parent = self.parentChildMap[node['_id']]
            if parent == '_ROOT':
                return [self]
            return [self.PM[parent]]
        elif ref == 'ANCESTOR':
            retNodes = []
            while True:
                id = self.parentChildMap[self.PM[id]['_id']]
                if id == '_ROOT':
                    break
                retNodes.append(self.PM[id])
            return retNodes
           
    def _getAllID(self,expr):
        prefix = Selector(expr).toPrefix()
        if not prefix:
            return set([self['_id']])
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
               
    def _putTree(self,here,tree,num):
        if num > 1:
            tree = deepcopy(tree)
        attrsMap = {}		
        traverser = traverse(tree)
        while True:
            try:
                node = traverser.next()
            except StopIteration:
                break
            parentID = self._setID(node)
            self.PM[parentID] = node			
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
            for child in children:   
                id = self._setID(child)
                self.parentChildMap[id] = parentID 	
				
        self.parentChildMap[tree['_id']] = here['_id']  				
        here['_children'].append(tree)
        try:
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
        flatTree = flattenTree(node)
        for tree in flatTree:
            self._delAttrs(tree)
            del self.PM[tree['_id']]
            del self.parentChildMap[tree['_id']]
            
        del parent['_children'][index]
						
    def _delAttrs(self,here,attrs='*',replace={}):
        if attrs == '*':
            attrs = [a for a in here.keys() if a != '_id' and a!='_children']
        for k in attrs:
            if here.has_key(k):
                v = here[k]
                here.pop(k)
                if k!='_id' and k!='_children' and not isinstance(v,dict)\
                    and not isinstance(v,list):
                    if self.RI.has_key(k):
                        if self.RI[k].has_key(v):
                            self.RI[k][v].remove(here['_id'])
                if not self.RI[k][v]:
                    del self.RI[k][v]
                if not self.RI[k]:
                    del self.RI[k]
						
            if replace.has_key(k):
                oldVal = replace[k]
                here[k] = oldVal
                if not isinstance(oldVal,dict) and not isinstance(oldVal,list):
                    self.RI[k][oldVal].add(here['_id'])	
	   
    def _setID(self,node):
        if not isinstance(node, dict):
            raise TypeError("Node should be Object Type")
        if node.has_key('_id'):
            id = node['_id']
            if self.PM.has_key(id):
                raise KeyError('ID %s already present' %id)
        else:
            id = generateID()
            while self.PM.has_key(id):
                id = generateID()
            node['_id'] = id
        return id
		
    def dump(self,out):
        breaker = treebreaker(self)
        with open(out,'w') as f:
            while True:
                try:
                    s = breaker.next()
                    f.write(s)
                except StopIteration:
                    break

		

                
            
            

    