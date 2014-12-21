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

 