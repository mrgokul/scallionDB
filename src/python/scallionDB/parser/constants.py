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
logical = ['_and','_or']
path_logical = ['$&','$|']
path = ['$child','$desc']
relational = ['_eq','_neq','_lte','_gte','_lt','_gt','_regex','_exists',
               '_in', '_contains']
id_type = ['_eq','_in']
requests = ['GET','PUT','DELETE','LOAD','SHOW','DESCRIBE','SAVE','AGGREGATE']
request_types = {'GETREQ':'GET',
                 'PUTREQ':'PUT',
				 'DELREQ':'DELETE',
				 'SHOWREQ':'SHOW',
				 'LOADREQ':'LOAD',
				 'SAVEREQ':'SAVE',
				 'AGGREQ':'AGGREGATE'}
tree_requests = ['GET','PUT','DELETE','LOAD','DESCRIBE','SAVE']
nontree_requests = ['SHOW']
read_request = ['GET','DESCRIBE']
resources = ['TREE','ATTR']
references = ['ANCESTORS','PARENT','SELF','CHILDREN','DESCENDANTS']
tree_references = ['SELF','PARENT']
