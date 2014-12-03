import zmq
import time
import sys
from 

port = "5556"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)

def main():
    while True:
        message = socket.recv()
        response = get_response(message)
        socket.send(response)
        time.sleep(0.2)
		
if __name__ == 'main':
    main()
    