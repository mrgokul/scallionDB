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

from scallionDB.parser.request import parse_request

import unittest


class SelectorTest(unittest.TestCase):

    def test_simple_1(self):
        expr = "GET TREE TABLE_1 SELF {\"id\": 20}"
        self.assertEqual({'Attr': None, 'DELREQ': None, 'GETREQ': 'GET', 'JSON': '{"id": 20}', 'JSON2': None, 'LIST2': None, 'ObjName': 'TABLE_1', 'PUTREQ': None, 'Tree': 'TREE'},parse_request(expr))
    
    def test_simple_2(self):
        expr = "GET TREE TABLE_1 SELF {\"_id\": 20}"
        self.assertEqual({'Attr': None, 'DELREQ': None, 'GETREQ': 'GET', 'JSON': '{"_id": 20}', 'JSON2': None, 'LIST2': None, 'ObjName': 'TABLE_1', 'PUTREQ': None, 'Tree': 'TREE'},parse_request(expr))
		
    def test_simple_3(self):
        expr = "GET TREE TABLE_1 ANCESTOR {\"id\": 20}"
        self.assertRaises(SyntaxError,parse_request(expr))
    '''	
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
