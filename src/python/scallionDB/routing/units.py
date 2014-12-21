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
 
from collections import OrderedDict
import time

class Worker(object):
    def __init__(self, address, ewp, hl):
        self.address = address
        self.ewp = ewp
        self.hl = hl
        self.expiry = time.time() + ewp * hl 

class WorkerQueue(OrderedDict):

    def ready(self, worker):

        if not self.has_key(worker.address):
            self[worker.address] = worker
        else:
            self[worker.address].expiry = time.time() + worker.ewp * worker.hl 


    def purge(self):
        """Look for & kill expired workers."""
        t = time.time()
        expired = []
        for address,worker in self.iteritems():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            self.pop(address, None)

    def next(self):
        address, worker = self.popitem(False)
        return address
		
class Message(object):
    def __init__(self, frames, tree, expiry, type):
        self.frames = frames
        self.tree = tree
        self.expiry = expiry 
        self.type = type