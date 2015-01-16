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
 
from scallionDB.parser.selection import Selector, Operator
from scallionDB.parser.constants import *
_and = Operator('$and')
_or = Operator('$or')
 
def _filter(request,result):
        prefix = Selector(request).toPrefix()
        if not prefix:
            return result
        if len(prefix) == 1:
            indices =  sorted(_getIndex(prefix[0],result))
            return [result[i] for i in indices]
        operandStack = []
        while prefix:
            pop = prefix.pop()
            if isinstance(pop, Operator):
                operand_1 = operandStack.pop()
                if isinstance(operand_1, tuple):
                    operand_1 = _getIndex(operand_1,result)
                operand_2 = operandStack.pop()
                if isinstance(operand_2, tuple):
                    operand_2 = _getIndex(operand_2,result)					
                computed = evaluate(operand_1,operand_2,pop)
                operandStack.append(computed)	
            else:
                operandStack.append(pop)			
        return [result[i] for i in sorted(operandStack[0])]
		
def _getIndex(expr,result):
    attrKey = expr[0]
    attrValue = expr[1]
    operator = '$eq'

    if isinstance(attrValue,dict):
        operator, attrValue = attrValue.items()[0] 
		
    if operator == '$exists':
        ex = set([i for i,j in enumerate(result) if attrKey in j])
        if attrValue:
            return ex
        else:
            return set(range(len(result))) - ex
	
    if attrKey.startswith('_ts_'):
        raise Exception("Timestamp filtering not yet supported")
             			
    matchKeys = filterByRelation([res.get(attrKey) for res in result],
		                             attrValue,operator)
    matchIndex = set([i for i,j in enumerate(result) if j.get(attrKey)
                    	in matchKeys])
					
    return matchIndex
	
def evaluate(op1,op2,operator):
    if operator == _and:
        return op1 & op2
    if operator == _or:
        return op1 | op2
				

def filterByRelation(keys,value,operator):
    if operator not in relational:
        raise ValueError("Comparison should be made with one of "
		                 "%s" %str(relational))
    if operator == '$in':
        ret = set()
        for key in keys:
            if isinstance(key,tuple):
                if any([v in key for v in value]):
                    ret.add(key)
            else:
                if key in value:
                    ret.add(key)
        return ret
    if operator == '$contains':
        ret = set()
        for key in keys:
            if isinstance(key,tuple):
                if all([v in key for v in value]):
                    ret.add(key)
        return ret
    if operator == '$eq':
        return set(filter((lambda x: x == value), keys))
    if operator == '$neq':
        return set(filter((lambda x: x != value), keys))
    if operator == '$lt':
        return set(filter((lambda x: x < value), keys))
    if operator == '$gt':
        return set(filter((lambda x: x > value), keys))
    if operator == '$lte':
        return set(filter((lambda x: x <= value), keys))
    if operator == '$gte':
        return set(filter((lambda x: x >= value), keys))	
    if operator == '$regex':
        str_keys = [a for a in keys if isinstance(a,basestring)]
        return set(filter((lambda x: re.search(value,x)), str_keys))	
