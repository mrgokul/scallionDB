import zmq
from zmq.error import Again    
from constants import *

def send_request(socket, request):
    frames = ['',request]
    socket.send_multipart(frames)
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    msg = ''
    while True:
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
                
