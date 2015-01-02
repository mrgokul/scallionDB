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
from constants import *
		
def validateTreeReferences(reference):		
    if reference.upper() not in tree_references:
        raise SyntaxError("Error: - Invalid reference type."
                          "Valid references are %s" %str(tree_references))

def validateSelector(selector):
    if isinstance(selector,dict):
        try:
            selector = json.dumps(selector)
        except:
            raise SyntaxError("Error: - Invalid JSON")
    elif isinstance(selector,list):
        if not all([isinstance(a,dict) for a in selector]):
            raise SyntaxError("All elements in selector should be dict type")          
        try:
            selector = json.dumps(selector)
        except:
            raise SyntaxError("Error: - Invalid JSON")        
    else:
        raise SyntaxError("Error: - Selector is not of type dict or list")
		
    return selector
	
def validateAttrReferences(reference):
    if isinstance(reference,list):
        reference = [r.upper() for r in reference]
        for ref in reference:
            if ref not in references:
                raise SyntaxError("Error: - Invalid reference type."
                           "Valid references are %s" %str(references))
 
        parentCheck = "PARENT" in reference and "ANCESTORS" in reference
        childCheck = "CHILDREN" in reference and "DESCENDANTS" in reference
        if parentCheck:
            raise SyntaxError("Error: - Invalid References."
                        "PARENT and ANCESTORS cannot be referenced together!")
        if childCheck:
            raise SyntaxError("Error: - Invalid References."
                    "CHILDREN and DESCENDANTS cannot be referenced together!")
        reference = ','.join(reference)
    else:
        if reference.upper() not in references:
            raise SyntaxError("Error: - Invalid reference type."
                                    "Valid references are %s" %str(references))
	
    return reference
	
def validateAttrList(attribute_list):
    if not(isinstance(attribute_list,list) or attribute_list == '*'):
        raise SyntaxError("Error: - attribute_list should be" 
                           " a list of attributes (or * for all attributes)")
    if isinstance(attribute_list,list):
        if "_children" in attribute_list:
            raise Exception("Error: - _children isn't a valid attribute")
        #if not all([isinstance(each,basestring) for each in attribute_list]):
         #   raise SyntaxError("Error: - Invalid list of attributes!"
         #                         "Each attribute should be of string type")
        attribute_list = json.dumps(attribute_list)
    return attribute_list
		
def validateTree(tree):
    if isinstance(tree,dict):
        try:
            tree = json.dumps(tree)
        except:
            raise SyntaxError("Error: - INVALID Tree JSON!!")
    else:
        raise SyntaxError("Error: - Tree should be of dict type") 
    return tree
	
def validateAttrDict(attr_dict):
    if isinstance(attr_dict,dict):
        if "_id" in attr_dict.keys() or "_children" in attr_dict.keys():
            raise Exception("Error: - _id & _children aren't"
                            " attrs types that can be put")
        try:
            attr_dict = json.dumps(attr_dict)
        except:
            raise SyntaxError("Error: - INVALID attrdict JSON!")
    else:
        raise SyntaxError("Error: - attrdict should be of dict type")
    return attr_dict