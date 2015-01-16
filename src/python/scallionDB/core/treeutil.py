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


from random import randint
import json, re

def generateID():
    return "%09x" % randint(0,10**11)
		
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
    if not isinstance(tree,dict):
        yield json.dumps(tree)
        raise StopIteration        
    if not tree.has_key('_children'):
        yield json.dumps(tree)
        raise StopIteration
    if not tree['_children']:
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
		
           
		

    