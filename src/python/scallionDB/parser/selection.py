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
from constants import * 

class Operator(object):
    def __init__(self,type):
        self.type = type
    def __str__(self):
        return "<Operator " + self.type +">"
    def __repr__(self):
        return self.__str__()
    def __eq__(self,other):
        return self.type == other.type
    def __neq__(self,other):
        return self.type != other.type

class OperatorTimesReference(object):
    def __init__(self,operator,reference):
        self.operator = Operator(operator)
        self.reference = reference
        self.times = 0

			
class Selector(object):

    def __init__(self,expr):
        self.expr = expr
		
    def toPrefix(self):
        if not isinstance(self.expr,dict):
            raise SyntaxError("Selector must be dict type")            
        if not self.expr:
            return self.expr
        if len(self.expr) == 1 :
            if self.expr.keys()[0] not in logical:
                k,v = self.expr.items()[0]
                self._checkAttribute(k,v)
                return self.expr.items()
            else: 				
                self.operatorStack = []
                self.prefix = []        
        else:
            self.operatorStack = [OperatorTimesReference('$and',0)]
            self.prefix = [Operator('$and')]		
        for k,v in self.expr.iteritems():
            if k in logical:
                self._evalOperator(k,v)
            else:
                self._evalOperand(k,v)
        return self.prefix
    	
    def _evalOperator(self,operator,items):
        if not isinstance(items, list):
            raise SyntaxError("Expecting array type for operator %s" %(operator,))
        if not all([isinstance(i,dict) for i in items]):
            raise SyntaxError("Expecting all Object type for items in operator %s"
                    			%(operator,))								
        if len(items) < 2:
            raise SyntaxError("At least two array items required in operator %s"
                    			%(operator,))		
        self.operatorStack.append(OperatorTimesReference(operator,len(self.prefix)))
        self.prefix.append(Operator(operator))
        for item in items:
            for k,v in item.iteritems():
                if k in logical:
                    self._evalOperator(k,v)
                else:
                    if len(item) > 1:
                        self.prefix.extend(Selector(item).toPrefix())
                        break
                    else:
                        self._evalOperand(k,v)   				
    	self.operatorStack.pop()
    
    def _evalOperand(self,k,v):
        self._checkAttribute(k,v)
        if self.operatorStack[-1].times > 1:
            ref = self.operatorStack[-1].reference
            self.prefix.insert(ref, Operator(self.operatorStack[-1].operator.type))
        self.prefix.append((k,v))
        self.operatorStack[-1].times += 1    	
    
    def _checkAttribute(self,k,v):
        if k == '_id':
            if isinstance(v, dict):
                op, vals = v.items()[0]
                if(len(v) > 1) or op not in id_type:
                    raise SyntaxError("Only $eq or $in operator accepted for _id")
                if op == '$eq':
                    if not isinstance(vals, basestring):
                        raise SyntaxError("_id should be alphanumeric string")
                    if not vals.isalnum():
                        raise SyntaxError("_id should be alphanumeric")
                if op == '$in':
                    if not all([isinstance(e, basestring) for e in vals]):
                        raise SyntaxError("_id should be alphanumeric string")
                    if not all([e.isalnum() for e in vals]):
                        raise SyntaxError("_id should be alphanumeric")               
            elif isinstance(v,basestring):
                if not v.isalnum():
                    raise SyntaxError("_id should be alphanumeric")
            else:
                raise SyntaxError("_id should be alphanumeric")
        elif k == '$child' or k == '$desc':
            if not isinstance(v, dict):
                raise SyntaxError("$child or $desc should be of dict type")
            keys = set(v.keys())
            if not keys.issubset(set(path_logical)):
                 raise SyntaxError("$child or $desc keys can only be of %s"
				                    %(str(path_logical),)) 
            values = v.values()
            if not all([isinstance(l,list) for l in values]):   
                raise SyntaxError("$child or $desc values should be array type")                			
        else:
            if isinstance(v, list):
                raise SyntaxError("Array comparison not supported")
            if isinstance(v, dict):
                if(len(v) > 1) or v.keys()[0] not in relational:
                    raise SyntaxError("Only one of %s operators or %s logical_paths"
                    				  " accepted" %(str(relational),str(path_logical)))

                operator, val = v.items()[0]
                if operator == '$exists':
                    if not isinstance(val, bool):
                        raise SyntaxError("$exists should be of boolean type") 
                if operator == '$in' or operator == '$contains':
                    if not isinstance(val,list):
                        raise SyntaxError("%s operator should compare lists" %operator)
                elif isinstance(val,(dict,list)):
                    raise SyntaxError("Comparison of Array/Object type not accepted"
					                   " for operator %s" %operator)				
				
		
 
        			
			