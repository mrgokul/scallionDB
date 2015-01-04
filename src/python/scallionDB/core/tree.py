''' 
  Licensed under the Apache License, Version 2.0 (the "License"); you may
  not use this file except in compliance with the License. You may obtain
  a copy of the License at
 
      http://www.apache.org/licenses/LICENSE-2.0
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
 '''

import json
import gc
import traceback

from copy import deepcopy
from collections import defaultdict

from scallionDB.parser.selection import Selector, Operator
from treeutil import evaluate, flattenTree, traverse, generateID
from treeutil import  filterByRelation, treebreaker
from listutil import listFuncs
from dateutil import parser as tsparser

class Tree(dict):

    def __init__(self, name):
        self.name = name
        self.RI = defaultdict(lambda: defaultdict(set))
        self.PM = {}
        self.tsAttrs = {}
        self.parentChildMap = {}		
        self['_id'] = '_ROOT'		
        self['_children'] = []
		
    def GET(self,expr,ref,attrs=[]):
        expr = json.loads(expr)
        if isinstance(expr,dict):
            expr = [expr]
        ids = set(['_ROOT'])	
        for exp in expr:
            ids = self._getAllID(exp,ids)       		
        getNodes = []
        attrNodes = []
        for id in ids:
            nodes = self._getNodes(id,ref)          
            getNodes.extend(nodes)	
            attrNodes.append(nodes)			
        if not attrs:
            return getNodes					
        else:
            getAttrs = []
            for nodes in attrNodes:	
                temp = []  
                for node in nodes:			
                    if isinstance(attrs,list):
                        if '_id' not in attrs:
                            attrs.append('_id')
                        all = False
                    elif attrs == '*':
                        all = True
                    if all:
                        attr = [a for a in node.keys() if a != '_children']
                        attr.append('$children')
                    else:
                        attr = attrs
                    select = {k:node.get(k) for k in attr if k in node}
                    if '$children' in attr:
                        select['$children'] = [c['_id'] for c in node['_children']]
                    temp.append(select)
                getAttrs.append(temp)
            return getAttrs
			
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
                    raise Exception("Only %d out of %d nodes PUT, %s\n%s"
                					%(len(treeIDs), len(nodes), 
									str(treeIDs),traceback.format_exc()))
                treeIDs.append(treeID)
            else:
                if node['_id'] == '_ROOT':
                    continue
                try:
                    self._putAttrs(node, attrs)
                except Exception, e:
                    raise Exception("Only %d out of %d nodes ATTRS applied:, %s\n%s"
                					%(len(treeIDs), len(nodes), 
									str(treeIDs), traceback.format_exc()))
                treeIDs.append(node['_id'])
            num -= 1
        return treeIDs
		
    def LOAD(self,path):
        root = json.load(open(path))
        ids = []
        if root.get('_id') == '_ROOT':
            for child in root['_children']:
                ids.extend(self.PUT('{}','SELF',child))
            return ids
        else:
            return self.PUT('{}','SELF',root)
		
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
                    raise Exception("Only %d out of %d nodes DELETED, %s\n%s"
                					%(len(treeIDs), len(nodes), 
									str(treeIDs), traceback.format_exc()))
                treeIDs.append(node['_id'])
            else:
                if not self.PM.get(node['_id']):
                    treeIDs.append(node['_id'])	
                    continue
                try:
                    self._delTree(node)
                except:
                    raise Exception("Only %d out of %d nodes DELETED, %s\n%s"
               	    	%(len(treeIDs), len(nodes), 
				    	str(treeIDs), traceback.format_exc()))
                treeIDs.append(node['_id'])	
        gc.collect()		
        return treeIDs          
			
    def _getNodes(self,id,refs):
        ret = []
        for ref in refs.split(','):
            if id == '_ROOT':
                ret.append(self)
            if not self.PM.has_key(id):
                continue
            if ref == 'SELF':
                ret.append(self.PM[id])
            elif ref == 'CHILDREN':
                ret.append(self.PM[id]['_children'])
            elif ref == 'DESCENDANTS':
                for node in self.PM[id]['_children']:
                    ret.extend(flattenTree(node))
            elif ref == 'PARENT':
                node = self.PM[id]
                parent = self.parentChildMap[node['_id']]
                if parent != '_ROOT':
                    ret.append(self.PM[parent])
            elif ref == 'ANCESTORS':
                while True:
                    id = self.parentChildMap[self.PM[id]['_id']]
                    if id == '_ROOT':
                        break
                    ret.append(self.PM[id])
        return ret
           
    def _getAllID(self,expr,ids):
        prefix = Selector(expr).toPrefix()
        if not prefix:
            return set([self['_id']])
        if len(prefix) == 1:
            return self._getIDset(prefix[0],ids)
        operandStack = []
        while prefix:
            pop = prefix.pop()
            if isinstance(pop, Operator):
                operand_1 = operandStack.pop()
                if isinstance(operand_1, tuple):
                    operand_1 = self._getIDset(operand_1,ids)	
                operand_2 = operandStack.pop()
                if isinstance(operand_2, tuple):
                    operand_2 = self._getIDset(operand_2,ids)						
                computed = evaluate(operand_1,operand_2,pop)
                operandStack.append(computed)	
            else:
                operandStack.append(pop)			
        return operandStack[0]
			
    def _getIDset(self, expr,caps):
        attrKey = expr[0]
        attrValue = expr[1]
        operator = '_eq'
        if attrKey == '_id':
            return set([attrValue])

        if attrKey == '$child':      
            childset = set()
            i = 0
            for _and in attrValue.get('$&',[]):
                childIDs = self._getAllID(_and,['_ROOT'])
                if i:
                    childset.intersection_update(set([self.parentChildMap[id] 
				                                 for id in childIDs]))
                else:
                    childset.update(set([self.parentChildMap[id] 
				                                 for id in childIDs]))        
                i += 1												 
            for _or in attrValue.get('$|',[]):
                childIDs = self._getAllID(_or,['_ROOT'])
                childset.update(set([self.parentChildMap[id] 
				                for id in childIDs]))
            return childset - set(['_ROOT'])
        if attrKey == '$desc':
            descset = set()   
            i = 0
            for _and in attrValue.get('$&',[]):
                ids = set()
                descIDs = self._getAllID(_and,['_ROOT'])
                for id in descIDs:
                    fid = self.parentChildMap[id]
                    while True:
                        if fid == '_ROOT':
                            break
                        ids.add(fid)
                        fid = self.parentChildMap[fid]
                if i:
                    descset.intersection_update(ids)
                else:
                    descset.update(ids)
                i += 1
            for _or in attrValue.get('$|',[]):
                ids = set()
                descIDs = self._getAllID(_or,['_ROOT'])
                for id in descIDs:
                    fid = self.parentChildMap[id]
                    while True:
                        if fid == '_ROOT':
                            break
                        ids.add(fid)
                        fid = self.parentChildMap[fid]
                descset.update(ids)		
            return descset
			
        if isinstance(attrValue,dict):
            operator, attrValue = attrValue.items()[0] 
			
        if operator == '_exists':
            if attrValue:
                return set.union(*self.RI[attrKey].values())
            else:
                return set(self.PM.keys()) - set.union(*self.RI[attrKey].values())
				
        if attrKey.startswith('_ts_'):
            try:
                attrValue, first = tsparser.parse(attrValue,fuzzy=True)
            except:
                raise Exception("Unable to handle timestamp %s" %attrValue)
                			
        matchKeys = filterByRelation(self.RI.get(attrKey,dict()).keys(),
		                             attrValue,operator)
        ids = set()
        for matchKey in matchKeys:
            ids.update(self.RI[attrKey][matchKey])
        fids = set()
        for id in ids:
            fid = self.parentChildMap[id]
            while fid not in caps:
                fid = self.parentChildMap[fid]
            else:
                fids.add(id)					
        return fids
               
    def _putTree(self,here,tree,num):
        if num > 1:
            tree = deepcopy(tree)
        attrsMap = defaultdict(lambda: defaultdict(set))	
        traverser = traverse(tree)
        try:
            while True:
                try:
                    node = traverser.next()
                except StopIteration:
                    break
                parentID = self._setID(node)
                self.PM[parentID] = node			
                for k,v in node.iteritems():
                    if isinstance(k,basestring) and k.startswith('$'):
                        raise KeyError("attribute cannot start with '$'")
                    if isinstance(k,basestring) and '.' in k:
                        raise KeyError("attribute cannot contain '.'")
                    if k!='_id' and k!='_children' and not isinstance(v,dict):
                        if isinstance(v,list):
                            v = self._handleList(v)
                        attrsMap[k][v].add(parentID) 			
                children = node['_children']
                if not isinstance(children,list):
                    raise TypeError("_children attribute should be of Array Type")
                for child in children:   
                    id = self._setID(child)
                    self.parentChildMap[id] = parentID 	
		    		
            self.parentChildMap[tree['_id']] = here['_id']  				
            here['_children'].append(tree)
  
            for attr,valMap in attrsMap.iteritems():
                for val, map in valMap.iteritems():	
                    if isinstance(attr,basestring) and attr.startswith('_ts_'):
                        val = self._handleTS(attr,val)					
                    self.RI[attr][val].update(map)		
            return tree['_id']
        except Exception, e:
            self._delTree(tree,here)
            raise Exception(e)

    def _putAttrs(self, here, attrs):
        oldAttrs = {k:here[k] for k in attrs.keys() if here.has_key(k)}
        try:		        
            for k,v in attrs.iteritems():
                if isinstance(k,basestring) and k.startswith('$'):
                    raise KeyError("attribute cannot start with '$'")
                if isinstance(k,basestring) and '.' in k:
                    raise KeyError("attribute cannot contain '.'")
                if k == '_id' or k == '_children':
                    raise KeyError("attribute cannot be %s " %k)               
                
                if oldAttrs.has_key(k):
                    oldVal = oldAttrs[k]
                    if isinstance(oldVal,list) and isinstance(v,dict):
                        self._handleListAttrs(here,k,v)
                        continue
                    elif isinstance(k,basestring) and  k.startswith('_ts_'):
                        oldVal = self._handleTS(k,oldVal)
                    elif isinstance(v,list):
                        oldVal = self._handleList(v)
                    if not isinstance(oldVal,dict):
                        self.RI[k][oldVal].remove(here['_id'])
                    if not self.RI[k][oldVal]:
                        del self.RI[k][oldVal]
                    if not self.RI[k]:
                        del self.RI[k]
						
                here[k] = v	
				
                if not isinstance(v,dict):
                    if k.startswith('_ts_'):
                        v = self._handleTS(k,v)
                    if isinstance(v,list):
                        v = self._handleList(v)
                    self.RI[k][v].add(here['_id'])
						
        except Exception, e:
            self._delAttrs(here,attrs.keys(),oldAttrs)
            raise Exception(e)
			
    def _delTree(self, node, parent=None):
        if not parent:
            parent = self.GET(json.dumps({'_id':node['_id']}),'PARENT')[0]
        try:
            index = parent['_children'].index(node)
        except ValueError:
            index = -1
        flatTree = flattenTree(node)
        for tree in flatTree:
		
            if self.PM.has_key(tree['_id']):
                del self.PM[tree['_id']]
            if self.parentChildMap.has_key(tree['_id']):
                del self.parentChildMap[tree['_id']]
        if index > -1:           
            del parent['_children'][index]
						
    def _delAttrs(self,here,attrs='*',replace={}):
        if attrs == '*':
            attrs = [a for a in here.keys() if a != '_id' and a!='_children']
        for k in attrs:
            if isinstance(k, dict):
                self._handleListAttrs(here,k.keys()[0],k.values()[0])
                continue
            if here.has_key(k):
                v = here[k]
                del here[k]
                if k == '_id' or k == '_children':
                    raise KeyError("attribute cannot be %s " %k)    
                if k.startswith('_ts_'):
                    v = self._handleTS(k,v)
                if isinstance(v,list):
                    v = self._handleList(v)
                if self.RI.has_key(k):
                    if self.RI[k].has_key(v):
                        self.RI[k][v].remove(here['_id'])
                if self.RI.has_key(k) and self.RI[k].has_key(v):
                    if not self.RI[k][v]:
                        del self.RI[k][v]
                    if not self.RI[k]:
                        del self.RI[k]
						
            if replace.has_key(k):
                oldVal = replace[k]
                if isinstance(k,basestring) and k.startswith('_ts_'):
                    oldVal = self._handleTS(k,oldVal)                
                here[k] = oldVal
                if isinstance(oldVal,list):
                    oldVal = self._handleList(oldVal)                   
                if not isinstance(oldVal,dict):
                    self.RI[k][oldVal].add(here['_id'])	
					
    def _handleList(self,l):
        return tuple([a for a in l if not isinstance(a,(list,dict))])
			   
    def _handleTS(self,k,v)	:	
        if not self.tsAttrs.has_key(k):
            self.tsAttrs[k] = 'month'
        existing = self.tsAttrs[k]
        try:
            ts, first = tsparser.parse(v,dayfirst=existing=='day',
			                            yearfirst=existing=='year',
										fuzzy=True)
            if first != existing:
                if first == 'month':
                    raise Exception
                elif first == 'day':
                    if existing == 'year':
                        raise Exception
                    else:
                        self._resetTS(k,'day')
                        self.tsAttrs[k] = 'day'
                else:
                    self._resetTS(k,'year')
                    self.tsAttrs[k] = 'year'					
        except:
            raise Exception("Unable to guess/handle timestamp %s" %k)
        return ts
		
    def _handleListAttrs(self,node,k,v):
        operator, value = v.items()[0]
        oldKey = self._handleList(node[k])
        l = listFuncs(node[k], operator, value)  
        newKey = self._handleList(node[k])     
	
        self.RI[k][oldKey].remove(node['_id'])
        if not self.RI[k][oldKey]:
            del self.RI[k][oldKey]
        if not self.RI[k]:
            del self.RI[k]
						
        self.RI[k][newKey].add(node['_id'])       
			
    def _resetTS(self,k,first):
        if not self.RI.has_key(k):
            return
        ids = set.union(*self.RI[k].values()) 	
        self.RI[k] = defaultdict(set)
        for id in ids:      
            ts, ret = tsparser.parse(self.PM[id][k],dayfirst=first=='day',
			                           yearfirst=first=='year',fuzzy=True)
            if ret != first:
                raise Exception
            if self.RI[k].has_key(ts):
                self.RI[k][ts].add(id)
            else:
                self.RI[k][ts] = set([id])
		
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

		

                
            
            

    