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
