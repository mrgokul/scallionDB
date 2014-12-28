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
import traceback
import os
import shutil
from tree import Tree

def evaluate(trees,parsed,folder):
    treename =  parsed['tree']
    if parsed['request'] == 'LOAD':
        if treename in trees:
            raise Exception("Tree with name %s already exists" %treename)
        tree = Tree(treename)
        trees[treename] = tree
        try:
            tree.LOAD(parsed['path'])
            return treename
        except Exception, e:
            del trees[treename]
            raise Exception(traceback.format_exc())	
  
    selector = parsed['selector'] 
    reference = parsed['reference']
    req = parsed['request']
    attrs = parsed['attrs']
    if attrs:
        if attrs != '*':
            attrs = json.loads(attrs)
    tree = trees.get(treename,None)	
	
    if req == 'PUT':      
        if not tree:
            tree = Tree(treename)
            trees[treename] = tree		
        if attrs: 
            return tree.PUT(selector,reference,attrs=attrs)
        else:
            return tree.PUT(selector,reference,tree=json.loads(parsed['newtree'])) 
	
    if not tree:
        raise Exception("Tree %s does not exist" %treename)	

    if req == 'GET':
        if attrs: 
            return tree.GET(selector,reference,attrs)
        else:
            return tree.GET(selector,reference)
    elif req == 'DELETE':
        if attrs: 
            return tree.DELETE(selector,reference,attrs)
        else:
            if selector == '{}':
                del trees[treename]
                fn = os.path.join(folder, treename + '.tree')
                os.path.exists(fn) and os.remove(fn)
                return 'Tree %s deleted successfully' %treename
            return tree.DELETE(selector,reference)  
    elif req == 'SAVE':
        fname = os.path.join(folder, treename + '.tmp')
        newname = os.path.join(folder, treename + '.tree')
        tree.dump(fname)
        shutil.move(fname, newname) 
        return 'Successfuly saved tree %s' %treename
		
