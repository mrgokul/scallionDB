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
        self.expr = json.loads(expr)
		
    def toPrefix(self):
        if len(self.expr) == 1 :
            if self.expr.keys()[0] not in logical:
                k,v = self.expr.items()[0]
                self._checkAttribute(k,v)
                return self.expr.items()
            else: 				
                self.operatorStack = []
                self.prefix = []        
        else:
            self.operatorStack = [OperatorTimesReference('_and',0)]
            self.prefix = [Operator('_and')]		
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
                if(len(v) > 1) or v.keys()[0] != id_type:
                    raise SyntaxError("Only equality operator accepted for _id")
                if not isinstance(v[id_type], basestring):
                    raise SyntaxError("_id should be alphanumeric string")
                if not v[id_type].isalnum():
                    raise SyntaxError("_id should be alphanumeric")
            elif isinstance(v,basestring):
                if not v.isalnum():
                    raise SyntaxError("_id should be alphanumeric")
            else:
                raise SyntaxError("_id should be alphanumeric")
        else:
            if isinstance(v, list):
                raise SyntaxError("Array comparison not supported")
            if isinstance(v, dict):
                if(len(v) > 1) or v.keys()[0] not in relational:
                    raise SyntaxError("Only one of %s operators accepted"
                    					%(str(relational),))
                val = v.values()[0]
                if isinstance(val,dict) or isinstance(val,list):
                    raise SyntaxError("Comparison of Array/Object type not accepted")				
				
		
 
        			
			