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
 
import types
import itertools

from collections import defaultdict
from operator import itemgetter

from apply import reduce_, map_, filter_
 
reduceFuncs = {'$'+fn[1:]:reduce_.__dict__.get(fn) for fn in dir(reduce_) 
               if isinstance(reduce_.__dict__.get(fn),types.FunctionType)}
mapFuncs = {'$'+fn[1:]:map_.__dict__.get(fn) for fn in dir(map_) 
               if isinstance(map_.__dict__.get(fn),types.FunctionType)}
filterFuncs = {'$'+fn[1:]:filter_.__dict__.get(fn) for fn in dir(filter_) 
               if isinstance(filter_.__dict__.get(fn),types.FunctionType)}
			   

def _flatten(request,result):
    if not result: 
        return []
    if not request:
        raise SyntaxError ("Always be truthful to flatten")
    if isinstance(result[0],list):
        return sum(result,[])
    else:
        return result

def _reduce(request,result):
    """
    {"foo":{"$sum":"$foo"}}	
	"""
    if not result: 
        return []
    result = _flatten(True,result)
    red = defaultdict(lambda: defaultdict(list))
    output = {}
    for okey, req in request.items():
        if okey.startswith('$'):
            raise SyntaxError("Aliases cannot start with $")	
        if len(req) > 1:
            raise SyntaxError("apply length > 1. Got %s" %str(req))
        operator, operand = req.items()[0]      
        if operator not in reduceFuncs.keys():
            raise SyntaxError("apply function should be one of %s"
			                   %str(reduceFuncs.keys()))  
        if isinstance(operand, basestring):
            if not operand.startswith('$'):
                raise SyntaxError("Variable %s should be prefixed with '$'"
			                   %operand)     
            operand = operand[1:]
        elif operator == '$sum' and operand == 1:
                operator = '$sum1'
        else:
            raise SyntaxError("Variable should start '$' or set to 1"
			                      " if operator is '$sum' (for group counts)")    			
        for res in result:
            red[operator][okey].append(res.get(operand,None))
			
    for operator, groups in red.iteritems():
        for okey, l in groups.iteritems():
            output[okey] = reduceFuncs[operator](l)	
    return output
   

def _refreduce(request,result):
    if not result: 
        return []
    if not isinstance(result[0],list):
        raise ValueError("Cannot reference reduce on a flat tree")
    return [_reduce(request, res) for res in result]


def _unwind(request,result):
    if not result: 
        return []
    if result and isinstance(result[0],list):
        return [_unwind(request,res) for res in result]
    unwinded = []
    for res in result:
        unwMap = {}
        for l in request:
            if not isinstance(res.get(l),list):
                raise ValueError("Can only unwind arrays. Not %s in %s"
                					%(l,str(res)))
            unwMap[l] = res[l]
            if not unwMap[l]:
                unwMap[l] = [None]
        keys, values = zip(*unwMap.items())
        prodValues = itertools.product(*values)
        for prodVal in prodValues:
            unwMap = dict(zip(keys,prodVal))
            for k,v in res.iteritems():
                if not k in request:
                    unwMap[k] = v
            unwinded.append(unwMap)         
    return unwinded
 
def _group(request,result):
    """
	{"_id":{"":""},"a":{"$sum":"$a"}}
	"""
    if not result: 
        return []
    if result and isinstance(result[0],list):
        return [_group(request,res) for res in result]

    aggregate = defaultdict(list)
    if not request.has_key('_id'):
        raise SyntaxError("No grouping keys provided")
    g = request.pop('_id')
    if not isinstance(g, dict):
        raise SyntaxError("Grouping should be of dict type") 
    grouping = {}
    for k, v in g.iteritems():
        if not isinstance(v,basestring):
            raise SyntaxError("Grouping keys should be string")		
        if not v.startswith('$'):
            raise SyntaxError("Grouping keys should start with $")		
        if k.startswith('$'):
            raise SyntaxError("Aliases cannot start with $")		
        grouping[k] = v[1:]	
    for res in result:
        key = tuple([res.get(k) for k in grouping.keys()])
        aggregate[key].append(res)
    output = []
    for k,v in aggregate.items():
        ret = {}
        for gk, gv in zip(grouping.values(),k):
            ret[gk] = gv
        red = _reduce(request,v)
        ret.update(red)
        output.append(ret)
    return output
	
def _map(request,result):
    if not result: 
        return []
    if result and isinstance(result[0],list):
        return [_map(request,res) for res in result]    
    for okey, req in request.items():
        if okey.startswith('$'):
            raise SyntaxError("Aliases cannot start with $")	
        if len(req) > 1:
            raise SyntaxError("apply length > 1. Got %s" %str(req))
        operator, operand = req.items()[0]      
        if operator not in mapFuncs.keys():
            raise SyntaxError("apply function should be one of %s"
			                   %str(mapFuncs.keys()))  
        if isinstance(operand, basestring):
            if not operand.startswith('$'):
                raise SyntaxError("Variable %s should be prefixed with '$'"
			                   %operand)     
            operand = operand[1:]
        for res in result:
            if res.has_key(operand):
                res[operand] = mapFuncs[operator](res[operand])
    return result
    
			
def _limit(request,result):
    if not result: 
        return []
    if not isinstance(request,int):
        raise SyntaxError("Limit number should be integer")
    if result and isinstance(result[0],list):
        return [_limit(request,res) for res in result]
    return result[:request]
		
def _sort(request,result):
    if not result: 
        return []
    if result and isinstance(result[0],list):
        return [_sort(request,res) for res in result] 
    if not isinstance(request,list):
        raise SyntaxError("Sort request should be a list of sorting key/value pairs")
    if not all([isinstance(d,dict) for d in request]):
        raise SyntaxError("Sort request should be a list of sorting key/value pairs")
    if any([len(d)>1 for d in request]):
        raise SyntaxError("Each sort key should be of length 1")
		
    sortKeys, sortOrder = zip(*[d.items()[0] for d in request])		
		
    if any([k.startswith('$') for k in sortKeys]):
        raise SyntaxError("Sort keys should not start with $")
	    
    for v in sortOrder:
        if v != 1 and v != -1:
            raise SyntaxError("Sort values should be 1 or -1 ")	 			
    for res in result:
        for k in sortKeys:
            if not res.has_key(k):
                res[k] = None
	
    comparers = [(itemgetter(k),v) for k,v in zip(sortKeys,sortOrder)]
    def comparer(left,right):
        for fn, mult in comparers:
            result = cmp(fn(left),fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(result,cmp=comparer)