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
            raise Exception(e)		
  
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
		
