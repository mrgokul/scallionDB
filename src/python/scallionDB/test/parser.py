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

import unittest

_or = Operator('$or')
_and = Operator('$and')

class SelectorTest(unittest.TestCase):
    
    def test_simple_0(self):
        expr = Selector({})
        self.assertEqual({},expr.toPrefix())

    def test_simple_1(self):
        expr = Selector({"_id": 20})
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_2(self):
        expr = Selector({"id": 20})
        self.assertEqual([('id', 20)],expr.toPrefix())

    def test_simple_3(self):
        expr = Selector({"id":{"$lt":2,"$neq":"1"}})
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_4(self):
        expr = Selector({"_id":{"$lt":2}})
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_5(self):
        expr = Selector({"_id":{"$eq":2}})
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_6(self):
        expr = Selector({"_id":{"$eq":"foo"}})
        self.assertEqual([('_id', {'$eq': 'foo'})],expr.toPrefix())	
		
    def test_simple_7(self):
        expr = Selector({"id":{"$eq":[2]}})
        self.assertRaises(SyntaxError,expr.toPrefix) 

    def test_simple_8(self):
        expr = Selector({"id":[4312]})
        self.assertRaises(SyntaxError,expr.toPrefix)  

    def test_simple_9(self):
        expr = Selector({"id":{"$eq":"42313"}})
        self.assertEqual([('id', {'$eq': '42313'})],expr.toPrefix())
		
    def test_simple_10(self):
        expr = Selector({"$or":[]})
        self.assertRaises(SyntaxError,expr.toPrefix)  
		
    def test_simple_11(self):
        expr = Selector({"$or":[2,{"a":3}]})
        self.assertRaises(SyntaxError,expr.toPrefix)  
		
    def test_simple_12(self):
        expr = Selector({"$or":[{"a":3}]})
        self.assertRaises(SyntaxError,expr.toPrefix)  

    def test_complex_1(self):
        expr = Selector({"foo":{"$eq":"42313"},"_id":"321"})
        self.assertEqual([_and, ('foo', {'$eq': '42313'}), ('_id', '321')],expr.toPrefix())     

    def test_complex_2(self):
        expr = Selector({"foo":{"$eq":"42313"},"_id":"321","moo":4})
        self.assertEqual([ _and, _and, ('foo', {'$eq': '42313'}), ('moo', 4),('_id', '321')],expr.toPrefix())  		
		
    def test_complex_3(self):
        expr = Selector({"$or":[{"a":3},{"b":4}]})
        self.assertEqual([_or, ('a', 3), ('b', 4)],expr.toPrefix()) 

    def test_complex_4(self):
        expr = Selector({"$or":[{"a":3},{"b":4},{"c":"5"}]})
        self.assertEqual([ _or, _or, ('a', 3), ('b', 4), ('c', '5')],expr.toPrefix())  

    def test_complex_5(self):
        expr = Selector({"$or":[{"a":3},{"b":4},{"c":"5"}],"_id":"foo"})
        self.assertEqual([_and,_or,_or,('a', 3), ('b', 4),('c', '5'), ('_id', 'foo')],expr.toPrefix())  

    def test_complex_6(self):
        expr = Selector({"$or":[{"a":3},{"b":4},{"c":"5"}],"$and":[{"_id":"foo"},{"d":True}]})
        self.assertEqual([_and,_or, _or,('a', 3),('b', 4),('c', '5'), _and, ('_id', 'foo'),('d', True)],expr.toPrefix()) 

    def test_complex_7(self):
        expr = Selector({"$and":[{"$or":[{"a":3},{"c":"5"}]},{"$or":[{"_id":"foo"},{"d":True}]}]})
        self.assertEqual([_and, _or, ('a', 3), ('c', '5'), _or, ('_id', 'foo'),('d', True)],expr.toPrefix())        

    def test_complex_8(self):
        expr = Selector({"$or":[{"$or":[{"h":8},{"g":7}]},{"$and":[{"a":1},{"$and":[{"$or":[{"b":2},{"c":3}]},{"$or":[{"d":4},{"e":5},{"f":6}]}]}]}]})
        self.assertEqual([_or,_or,('h', 8),('g', 7),_and,('a', 1),_and,_or,('b', 2),('c', 3),_or,_or,('d', 4),('e', 5),('f', 6)],expr.toPrefix())      		
