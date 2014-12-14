import zmq
import sys
from zmq.error import Again

port = "5555"

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.RCVTIMEO = 20000
socket.LINGER = 100
socket.connect ("tcp://localhost:%s" % port)

socket.send("b"*13)
try:
    message = socket.recv()
    print message
except Again, e: 
    print e
        
