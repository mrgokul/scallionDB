from scallionDB.parser.selection import Selector, Operator

import unittest,re,json

_or = Operator('_or')
_and = Operator('_and')
r = re.compile("((?P<GETREQ>GET)|(?P<PUTREQ>PUT)|(?P<DELREQ>DELETE))\s((?P<Attr>ATTR)|(?P<Tree>TREE))\s(?P<ObjName>[a-zA-Z0-9_]+)\s(?(Attr)(SELF|CHILDREN|DESCENDANT|ANCESTOR|PARENT)|(?(GETREQ)(SELF|CHILDREN|PARENT)|(SELF)))\s(?P<JSON>\{.+?\})(?(PUTREQ)(\s(?P<JSON2>\{.+\}))|(?(Attr)(\s(?P<LIST2>\[.+?\]))|(?!(.+?))))")

class SelectorTest(unittest.TestCase):

    def test_simple_1(self):
        grps = [m.groupdict() for m in r.finditer("GET TREE TABLE_1 SELF {\"id\": 20}")]
        if grps:
            json_get = grps[0]["JSON"]
            try:
                json.loads(json_get)
            except:
                self.assertRaises(SyntaxError,"Invalid JSON format")
            expr = Selector(json_get)
        else:
            self.assertRaises(SyntaxError,"Error in syntax of GET request")
        #expr = Selector('{"_id": 20}')
        #self.assertRaises(SyntaxError,expr.toPrefix)
    	
    def test_simple_2(self):
        grps = [m.groupdict() for m in r.finditer("GET TREE TABLE_1 ANCESTOR {\"id\": 20}")]
        if grps:
            json_get = grps[0]["JSON"]
            try:
                json.loads(json_get)
            except:
                raise SyntaxError("Invalid JSON format")
            expr = Selector(json_get)
        else:
            raise SyntaxError("Invalid GET request")
    
    def test_simple_3(self):
        grps = [m.groupdict() for m in r.finditer("GET TREE TABLE_1 PARENT {\"id\": 20}")]
        if grps:
            json_get = grps[0]["JSON"]
            try:
                json.loads(json_get)
            except:
                self.assertRaises(SyntaxError,"Invalid JSON format")
            expr = Selector(json_get)
        else:
            self.assertRaises(SyntaxError,"Error in syntax of GET request")
        		
    def test_simple_4(self):
        grps = [m.groupdict() for m in r.finditer("PUT ATTR TABLE_1 SELF {\"id\": 20} {\"a\": \"a1\"}")]
        if grps:
            json_get = grps[0]["JSON"]
            json_get2 = grps[0]["JSON2"]
            try:
                json.loads(json_get)
                json.loads(json_get2)
            except:
                self.assertRaises(SyntaxError,"Invalid JSON format")
            expr = Selector(json_get)
        else:
            self.assertRaises(SyntaxError,"Error in syntax of GET request")
    		
    def test_simple_5(self):
        grps = [m.groupdict() for m in r.finditer("PUT ATTR TABLE_1 DESCENDANT {\"foo\":{\"_eq\":\"42313\"},\"_id\":\"321\"} {\"a\": \"a1\"}")]
        if grps:
            json_get = grps[0]["JSON"]
            json_get2 = grps[0]["JSON2"]
            try:
                json.loads(json_get)
                json.loads(json_get2)
            except:
                raise SyntaxError("Invalid JSON format")
            expr = Selector(json_get)
        else:
            raise SyntaxError("Invalid PUT request")
    		
    def test_simple_6(self):
        grps = [m.groupdict() for m in r.finditer("PUT TREE TABLE_1 PARENT {\"foo\":{\"_eq\":\"42313\"},\"_id\":\"321\"} {\"a\": \"a1\"}")]
        if grps:
            json_get = grps[0]["JSON"]
            json_get2 = grps[0]["JSON2"]
            try:
                json.loads(json_get)
                json.loads(json_get2)
            except:
                raise SyntaxError("Invalid JSON format")
            expr = Selector(json_get)
        else:
            raise SyntaxError("Invalid PUT request")	
    '''		
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
    '''
