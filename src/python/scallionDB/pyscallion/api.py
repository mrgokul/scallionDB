import zmq

from random import randint
from tree import Tree
from zclient import send_request

class ScallionClient(object):

    def __init__(self,host='localhost',port='27890'):
        context = zmq.Context()
        identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        request = context.socket(zmq.DEALER)

        request.setsockopt(zmq.IDENTITY, identity)
        request.connect ("tcp://%s:%s" % (host,port))
        request.LINGER = 0
		
        self.request=request	
        self.trees={}
		
    def __getitem__(self,name):
        if not(name.isalnum()):
            raise SyntaxError("Error: GETTREE - Name of a tree must be alpha numeric")
        if name is self.trees:
            return self.trees[name]
        else:
            return Tree(name, self.request)
			
    def showTrees(self):
		return send_request(self.request, 'SHOW TREES')

 