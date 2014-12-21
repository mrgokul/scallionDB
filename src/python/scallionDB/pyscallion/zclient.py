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
import time
from zmq.error import Again    
from constants import *

def send_request(socket, request):
    frames = ['',request]
    socket.send_multipart(frames)
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    msg = ''
    start = time.time()
    while True:
        if time.time() - start > timeout:
            if not msg:
                raise Exception("Request timed out after %d` \
                                  seconds" %timeout)
        socks = dict(poller.poll(500))
        if socks.get(socket) == zmq.POLLIN:
            rec = socket.recv_multipart()
            if rec[-2] == SDB_MESSAGE:
                msg += rec[-1]
            elif rec[-2] == SDB_FAILURE:
                raise Exception(rec[-1])
            elif rec[-2] == SDB_TIMEOUT:
                raise Again(rec[-1])
            elif rec[-2] == SDB_NONTREE:
                return rec[-1]
            else:
                return msg
                
