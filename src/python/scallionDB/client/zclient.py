import zmq
import sys
from zmq.error import Again

port = "5556"

context = zmq.Context()
socket = context.socket(zmq.REQ)
#socket.RCVTIMEO = 2000
#socket.LINGER = 100
socket.connect ("tcp://localhost:%s" % port)

socket.send("b"*131072)
try:
    message = socket.recv()
    print message
except Again, e: 
    print e
        
