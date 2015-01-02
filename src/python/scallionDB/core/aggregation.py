
# coding: utf-8

# In[34]:

import itertools


# In[35]:

from itertools import islice


# In[5]:

def add(iplist):
    if iplist and isinstance(iplist,list):
        return sum([i for i in iplist if i])
    else:
        return 0


# In[6]:

def count(iplist):
    if iplist and isinstance(iplist,list):
        return len([i for i in iplist if i])
    else:
        return 0


# In[7]:

def unique(iplist):
    if iplist and isinstance(iplist,list):
        return list(set(iplist))
    else:
        return None


# In[8]:

def append(iplist):
    if all([True if isinstance(node,list) else False for node in iplist]):
        return [item for sublist in iplist for item in sublist]
    else:
        return None


# In[9]:

def union(iplist):
    if all([True if isinstance(node,list) else False for node in iplist]):
        return list(set.union(set(iplist[0]), *islice(iplist, 1, None)))
    else:
        return None


# In[10]:

def intersection(iplist):
    if all([True if isinstance(node,list) else False for node in iplist]):
        return list(set.intersection(set(iplist[0]), *islice(iplist, 1, None)))
    else:
        return None


# In[11]:

def lenunique(iplist):
    if iplist and isinstance(iplist,list):
        return count(unique(iplist))
    else:
        return 0


# In[12]:

def avg(iplist):
    if iplist and isinstance(iplist,list):
        return sum([i for i in iplist if i])/len(iplist)
    else:
        return 0


# In[13]:

def avg1(iplist):
    if iplist and isinstance(iplist,list):
        return sum([i for i in iplist if i])/len(count(iplist))
    else:
        return 0


# In[14]:

def flatten(tree):
    if tree and isinstance(tree,list):
        if all([True if isinstance(node,list) else False for node in tree]):
            return [item for sublist in tree for item in sublist]
        elif all([True if isinstance(node,dict) else False for node in tree]):
            return tree
    else:
        raise SyntaxError("Invalid argument for reduce, It should be a list!!!")


# In[95]:

def reduce_tree(request_type,aggr_req,tree):
    tree = flatten(tree)
    output = {}
    operations = {}
    result = {}
    for node in tree:
        for o_var, oper in aggr_req[request_type].items():
            operation = oper.items()[0][0]
            operand = oper.items()[0][1]
            operand = operand[1:]
            operations[operand] = operation
            if output.has_key(operand):
                output[operand].append(node.get(operand,None))
            else:
                output[operand] = [node.get(operand,None)]
    for operand,operation in operations.items():
        #print "Request of ", operation, "(", operand, ")"
        result[(operand,operation)] = fns[operation](output[operand])
    return result


# In[96]:

def refreduce_tree(aggr_req,tree):
    refreduced = []
    if isinstance(tree,list) and all([True if isinstance(node,list) else False for node in tree]):
        for each in tree:
            refreduced.append(reduce_tree("refreduce",refreduce_req,each))
    else:
        raise SyntaxError("Invalid refreduce request")
    return refreduced


# In[97]:

def multiply(node):
    k = []
    v = []
    if all([True if isinstance(each_node,dict) else False for each_node in node]):
        b1 = list(dict([(key, [value]) if not isinstance(value,list) else (key, value) for key,value in node[0].items()]).iteritems())
        for each in b1:
            k.append(each[0])
            v.append(each[1])
            p = list(itertools.product(*v))
    return [dict([(k[j],p[i][j]) for j in range(len(p[i])) ]) for i in range(len(p))]


# In[98]:

def unwind(tree):
    if isinstance(tree,list) and all([True if isinstance(node,list) else False for node in tree]):
        unwinded = []
        for each in tree:
            unwinded.append(multiply(each))
    elif isinstance(tree,list) and all([True if isinstance(node,dict) else False for node in tree]):
        unwinded = multiply(tree)
    else:
        raise SyntaxError("Invalid Syntax for unwind!!!")
    return unwinded
    


# In[99]:

input_tree = [[{"a":3,"b":["green","red"],"c":"sedan"},{"a":4,"b":["red"]}],[{"a":5,"b":["red"],"c":"SUV"}]]


# In[100]:

fns = {"$sum":add,"$count":count,"$unique":unique,"$append":append,"$union":union,"$intersection":intersection,"$lenunique":lenunique,"$avg":avg,"$avg1":avg1}


# In[101]:

reduce_req = {"reduce":{"a_red":{"$sum":"$a"},"b_red":{"$intersection":"$b"},"c_red":{"$count":"$c"}}}


# In[102]:

refreduce_req = {"refreduce":{"a_red":{"$sum":"$a"},"b_red":{"$intersection":"$b"},"c_red":{"$count":"$c"}}}


# In[103]:

reduce_tree('reduce',reduce_req,input_tree)


# In[104]:

refreduce_tree(refreduce_req,input_tree)


# In[105]:

unwind(input_tree)


# In[ ]:



