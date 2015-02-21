scallionDB
==========

An in memory JSON tree database. 

Requirements:
* Python 2.7+
* pyzmq 14.4+

ScallionDB was built with the intention to be schemaless and portable from a JSON file i.e. ScallionDB can read a JSON tree file from disc, build a complete in-memory tree and index attributes for quick lookups. To achieve this ScallionDB makes a few assumptions.
*	The ‘_id’ attribute in a JSON is a unique identifier of a node
*	The ‘_children’ attribute is an array of child nodes of a node with a given ‘_id’

##Loading and saving 

The LOAD command will load a JSON file on the server’s disc into scallionDB’s memory.
Having the entire data purely in-memory can be a hazard, as all the data gets erased in case of a failure. To tackle this issue, ScallionDB provides a couple of ways to persist data on disc.
*	The SAVE request will save a tree on disc
*	Configuring the saveLimit parameter in the configuration file. This will save a tree automatically after every <saveLimit> PUT/DELETE requests
The tree gets saved with a .tree extension in the ‘data’ folder.  The .tree file is the entire tree in JSON.  When scallionDB restarts, all .tree files get loaded into memory.

##CRUD

###GET

ScallionDB uses a unique selection expression query language called JPATH to fetch trees or attributes of a node.  JPATH is similar to XPATH, except the request is in JSON and supports features such as
*	Logical operators – and, or
*	Relational operators – greater than, less than, equals etc.
*	exists – if an attribute exists
*	regular expressions
*	in & contains – searching within list type attributes
*	Path – Get nodes which satisfy the path specified
*	node-contains – Get nodes that contain (that are ancestor/parent of ) other nodes
*	Timestamps
Additionally one can select specific attributes of a node or nodes related to it specified by one or more of the following relational fields
*	SELF
*	CHILDREN
*	PARENT
*	DESCENDANTS
*	ANCESTORS
 It can also fetch large trees, 100s of MBs big in a single request. This is achieved by breaking the in-memory down to chunks of strings and streaming to the client. The client reconstructs the JSON as it receives the stream.
 
###PUT

PUT requests are GET requests followed by what to PUT. If a tree needs to be PUT, it will be appended as child node to the selected nodes. If attributes need to be put, then it will be added to the same node (or related nodes). Note that putting attributes can update existing values

###DELETE

DELETE requests are GET requests followed by what to DELETE. One can selectively delete specific attributes of a node (or related nodes) or delete subtrees completely.

##Timestamps

Since scallionDB is schemaless and only stores/persists as JSON, it is important to identify timestamp attributes from other types. As a note, MongoDB achieves timestamp recognition by storing data in BSON.  ScallionDB on the other hand requires timestamp attributes to start with ‘_ts_’. It’s  a small price to pay, but it can effectively solve the schemaless, readable JSON (persisted trees are readable JSON and not in any encoded format) timestamp recognition problem. 
There is also the advantage that scallionDB internally uses the powerful dateutil Python library for automatic timestamp parsing. Which means as long as the timestamp is valid and unambiguous, it can recognize any format. ScallionDB also intelligently autocorrects existing indexed timestamps if it notices the month/day order ambiguity problem.  E.g. 01-03-2013 would be indexed as 03-Jan-2013 and not 01-March-2013, but in reality it should have been 01-March-2013. Now when it tries to index a new timestamp 14-04-2014, which is clearly 14-April-2014, scallionDB will autocorrect all timestamps that have been already indexed.

##Aggregation

ScallionDB’s support for aggregation is very similar to the support provided by MongoDB, hence it can be very useful for data processing and analysis. The request is given in the form a list of operators which forms the pipeline for aggregation i.e. the output of one operation feeds in as input for the next. The list of operators include –
*	$group – similar to SQL groupby
*	$reduce – apply a function without grouping by any variable 
*	$refreduce – apply a function grouping by references (e.g. ANCESTORS/DESCENDANTS)
*	$map – apply a function to transform a variable
	$filter – filter the pipeline with some conditions
*	$flatten – remove all reference grouping
*	$project – select a specified list of variables
*	$unwind – upack lists/lists into one record for each element (or cross product of elements in case of multiple lists)
*	$sort – sort the pipeline
*	$limit – limit the pipeline to the first n observations



```
{"a":1,"b":5,"_id":"aaaa",
"_children":[{"a":7, "c":20,"_id":"bbbb",
            "_children":[{"b":-1, "a":45, "bar":"a","_id":"cccc",
	                     "_children":[{"foo":"bar","_id":"dddd","_children":[]}]
						 },
                         {"b":-1, "f":25, "bar":"b","_id":"eeee",
	                     "_children":[{"foo":"baz","_id":"ffff","_children":[]}]
						 }			 
						 ]		
			},
           {"a":-4, "r":0,"_id":"gggg",
            "_children":[{"x":-1, "a":-45,"bar":"c","_id":"hhhh",
	                     "_children":[{"foo":"bar","_id":"iiii","_children":[]}]
						 },
                         {"y":-1, "f":75,"bar":"d","_id":"jjjj",
	                     "_children":[{"foo":"ball","_id":"kkkk","_children":[]}]
						 }			 
						 ]		
			}]
}
```


### Start the server

```
bin/scallion.py start
```

### Using the client library 

```python
import sys
#sys.path.append('<path to pyscallion's parent folder>')
from pyscallion import ScallionClient

client = ScallionClient()
client.showTrees()
#'[]'

###Load a tree
test = client['test']
test.loadTree('test.json')

###Get some nodes
#Learn selector expressions
selector = {"_or":[{"a":{"_gt":40}},{"a":{"_lt":-40}}]} #Get nodes where a > 40 or a < 40
nodes = test.getTree(selector)
#print nodes

###Add some children 
#Learn about references
#reference = 'PARENT' adds sibling nodes
#reference = 'SELF' adds child nodes (default)
gc = test.putTree(selector,{"hello":"world"})

###Delete some attributes
da = test.delAttrs({"hello":"world"},["b","bar"],'ANCESTORS')

### Now get the full tree
ft = test.getTree({})
#print ft
```
