from scallionDB.core.tree import Tree
import json
import os
import unittest
fn = os.path.join(os.path.dirname(__file__), 'files/test.json')
t = Tree('test')
t.LOAD(fn)
j = json.load(open(fn))

class TreeTest(unittest.TestCase):
    
    def test_load(self):
        self.assertEqual(j,t['_children'][0])
		
    #PUT tests GET as well
	
    def test_put(self):
        t.PUT('{"_or":[{"a":{"_gt":10}},{"a":{"_lt":-45}}]}','PARENT',{"_id":"xxxx"})
        j['_children'][0]['_children'].append({"_id":"xxxx","_children":[]})
        self.assertEqual(j,t['_children'][0])	

    def test_z_delete_attrs(self):	
        t.DELETE('{"_id":"xxxx"}','ANCESTORS',attrs='*')		
        del j['a'], j['b'], j['_children'][0]['a'],  j['_children'][0]['c']
        self.assertEqual(j,t['_children'][0])	
