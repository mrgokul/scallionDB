logical = ['_and','_or']
relational = ['_eq','_neq','_lte','_gte','_lt','_gt','_regex']
id_type = '_eq'
requests = ['GET','PUT','DELETE','LOAD','SHOW','DESCRIBE','SAVE']
resources = ['TREE','ATTR']
references = ['ANCESTORS','PARENT','SELF','CHILDREN','DESCENDANTS']
tree_references = ['PARENT','SELF','CHILDREN']
#  ScallionDB Protocol constants
SDB_READY = "\x01"      # Signals worker is ready
SDB_HEARTBEAT = "\x02"  # Signals worker heartbeat
SDB_TIMEOUT = "\x03"    # Signals timeout to client
SDB_NONTREE = "\x04"    # For Non-tree statements, precedes response message
SDB_MESSAGE = "\x05"    # For any message response, precedes response message
SDB_COMPLETE = "\x06"   # For completed, precedes tree name
SDB_FAILURE = "\x07"    # Failure message, precedes error message
