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
 
def listFuncs(l,operator,value):
    if operator == '$append':
        l.append(value)
        return l
    if operator == '$add':
        if not value in l:
            l.append(value)
        return l
    if operator == '$extend':
        if not isinstance(value,list):
            raise SyntaxError("Extend value should be array type")
        l.extend(value)
        return l
    if operator == '$update':
        if not isinstance(value,list):
            raise SyntaxError("Update value should be array type")
        for v in value:
            if not v in l:
                l.append(v)
        return l
    if operator == '$pop':
        if value < len(l):
            l.pop(value)
        return l
    if operator == '$chop':
        indexes = sorted(value,reverse=True)
        if indexes[-1] <0:
            raise SyntaxError("Negative Indices not allowed for $chop")
        for index in indexes:
            del l[index]
        return l		
    if operator == '$remove':
        if value in l:
            l.remove(value)
        return l 

        