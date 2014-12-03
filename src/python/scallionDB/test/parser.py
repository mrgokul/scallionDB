from scallionDB.parser.selection import Selector, Operator

import unittest

_or = Operator('_or')
_and = Operator('_and')

class SelectorTest(unittest.TestCase):

    def test_simple_1(self):
        expr = Selector('{"_id": 20}')
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_2(self):
        expr = Selector('{"id": 20}')
        self.assertEqual([('id', 20)],expr.toPrefix())

    def test_simple_3(self):
        expr = Selector('{"id":{"_lt":2,"_neq":"1"}}')
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_4(self):
        expr = Selector('{"_id":{"_lt":2}}')
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_5(self):
        expr = Selector('{"_id":{"_eq":2}}')
        self.assertRaises(SyntaxError,expr.toPrefix)
		
    def test_simple_6(self):
        expr = Selector('{"_id":{"_eq":"foo"}}')
        self.assertEqual([('_id', {'_eq': 'foo'})],expr.toPrefix())	
		
    def test_simple_7(self):
        expr = Selector('{"id":{"_eq":[2]}}')
        self.assertRaises(SyntaxError,expr.toPrefix) 

    def test_simple_8(self):
        expr = Selector('{"id":[4312]}')
        self.assertRaises(SyntaxError,expr.toPrefix)  

    def test_simple_9(self):
        expr = Selector('{"id":{"_eq":"42313"}}')
        self.assertEqual([('id', {'_eq': '42313'})],expr.toPrefix())
		
    def test_simple_10(self):
        expr = Selector('{"_or":[]}')
        self.assertRaises(SyntaxError,expr.toPrefix)  
		
    def test_simple_11(self):
        expr = Selector('{"_or":[2,{"a":3}]}')
        self.assertRaises(SyntaxError,expr.toPrefix)  
		
    def test_simple_12(self):
        expr = Selector('{"_or":[{"a":3}]}')
        self.assertRaises(SyntaxError,expr.toPrefix)  

    def test_complex_1(self):
        expr = Selector('{"foo":{"_eq":"42313"},"_id":"321"}')
        self.assertEqual([_and, ('foo', {'_eq': '42313'}), ('_id', '321')],expr.toPrefix())     

    def test_complex_2(self):
        expr = Selector('{"foo":{"_eq":"42313"},"_id":"321","moo":4}')
        self.assertEqual([ _and, _and, ('foo', {'_eq': '42313'}), ('moo', 4),('_id', '321')],expr.toPrefix())  		
		
    def test_complex_3(self):
        expr = Selector('{"_or":[{"a":3},{"b":4}]}')
        self.assertEqual([_or, ('a', 3), ('b', 4)],expr.toPrefix()) 

    def test_complex_4(self):
        expr = Selector('{"_or":[{"a":3},{"b":4},{"c":"5"}]}')
        self.assertEqual([ _or, _or, ('a', 3), ('b', 4), ('c', '5')],expr.toPrefix())  

    def test_complex_5(self):
        expr = Selector('{"_or":[{"a":3},{"b":4},{"c":"5"}],"_id":"foo"}')
        self.assertEqual([_and, ('_id', 'foo'),_or,_or, ('a', 3), ('b', 4),('c', '5')],expr.toPrefix())  

    def test_complex_6(self):
        expr = Selector('{"_or":[{"a":3},{"b":4},{"c":"5"}],"_and":[{"_id":"foo"},{"d":true}]}')
        self.assertEqual([_and, _and, ('_id', 'foo'),('d', True),_or, _or,('a', 3),('b', 4),('c', '5')],expr.toPrefix()) 

    def test_complex_7(self):
        expr = Selector('{"_and":[{"_or":[{"a":3},{"c":"5"}]},{"_or":[{"_id":"foo"},{"d":true}]}]}')
        self.assertEqual([_and, _or, ('a', 3), ('c', '5'), _or, ('_id', 'foo'),('d', True)],expr.toPrefix())        

    def test_complex_8(self):
        expr = Selector('{"_or":[{"_or":[{"h":8},{"g":7}]},{"_and":[{"a":1},{"_and":[{"_or":[{"b":2},{"c":3}]},{"_or":[{"d":4},{"e":5},{"f":6}]}]}]}]}')
        self.assertEqual([_or,_or,('h', 8),('g', 7),_and,('a', 1),_and,_or,('b', 2),('c', 3),_or,_or,('d', 4),('e', 5),('f', 6)],expr.toPrefix())      		
