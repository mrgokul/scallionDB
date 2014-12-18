logical = ['_and','_or']
relational = ['_eq','_neq','_lte','_gte','_lt','_gt','_regex']
id_type = '_eq'
requests = ['GET','PUT','DELETE','LOAD','SHOW','DESCRIBE','SAVE']
request_types = {'GETREQ':'GET',
                 'PUTREQ':'PUT',
				 'DELREQ':'DELETE',
				 'SHOWREQ':'SHOW',
				 'LOADREQ':'LOAD',
				 'SAVEREQ':'SAVE'}
tree_requests = ['GET','PUT','DELETE','LOAD','DESCRIBE','SAVE']
nontree_requests = ['SHOW']
read_request = ['GET','DESCRIBE']
resources = ['TREE','ATTR']
references = ['ANCESTORS','PARENT','SELF','CHILDREN','DESCENDANTS']
tree_references = ['PARENT','SELF','CHILDREN']
