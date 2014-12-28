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
 
from zclient import send_request
from validators import *

class Tree(object):

    def __init__(self,name,request):
        self.name = name
        self.request = request
        
    def getTree(self,selector,reference="SELF"): 
        validateTreeReferences(reference)
        selector = validateSelector(selector)
        
        statement = ' '.join(["GET","TREE",str(self.name),
                              reference.upper(),selector])                    
        return send_request(self.request, statement)
    
    def getAttrs(self,selector,attribute_list='*',reference='SELF'):
        reference = validateAttrReferences(reference)
        selector = validateSelector(selector)
        attribute_list = validateAttrList(attribute_list)

        statement = ' '.join(["GET","ATTR",str(self.name),reference.upper(),
                           selector,attribute_list])                        
        return send_request(self.request, statement)
        
    def putTree(self,selector,tree,reference='SELF'):
        validateTreeReferences(reference)
        selector = validateSelector(selector)
        tree = validateTree(tree)            

        statement = ' '.join(["PUT","TREE",self.name,reference.upper(),
                               selector,tree])                              
        return send_request(self.request, statement)
        
    def putAttrs(self,selector,attr_dict,reference='SELF'):
        reference = validateAttrReferences(reference)
        selector = validateSelector(selector)
        attr_dict = validateAttrDict(attr_dict)            
        statement = ' '.join(["PUT","ATTR",self.name,reference.upper(),
                              selector,attr_dict])                            
        return send_request(self.request, statement)   
        
    def delTree(self,selector,reference="SELF"):
        validateTreeReferences(reference)
        selector = validateSelector(selector)
            
        statement = ' '.join(["DELETE","TREE",self.name,
                              reference.upper(),selector])
                                  
        return send_request(self.request, statement)   
    
    def delAttrs(self,selector,attribute_list='*',reference="SELF"):
        attribute_list = validateAttrList(attribute_list)
        selector = validateSelector(selector)
        reference = validateAttrReferences(reference)

        statement = ' '.join(["DELETE","ATTR",self.name,reference.upper(),
                              selector,attribute_list])
                            
        return send_request(self.request, statement)    
        
    def loadTree(self,path):
        statement = ' '.join(["LOAD",self.name,path])                        
        return send_request(self.request, statement)   
        
    def saveTree(self):
        statement = ' '.join(["SAVE", self.name])
        return send_request(self.request, statement)
    
    def descTree(self):
        raise Exception("Need to think about what this will do")

        
