import time
import zmq
import threading

from units import Worker, WorkerQueue, Message
from random import randint
from constants import *
from collections import Counter

def get_tree(x):
    return x     

		
class BrokerThread(threading.Thread):

    def __init__(self, context, client_port, hi, hl, ewp):
        super(BrokerThread, self).__init__()
        self.context = context
        self.client_port = str(client_port)
        self.BEAT_INTERVAL = hi
        self.BEAT_LIVENESS = hl
        self.EXPECTED_PERFORMANCE = ewp
        print "Started Broker"

    def run(self):
	
        frontend = context.socket(zmq.ROUTER) # ROUTER
        backend = context.socket(zmq.ROUTER)  # ROUTER
        frontend.bind("tcp://*:" + str(self.client_port) ) # For clients
        backend.bind("inproc://workers" )  # For workers
        
        poller = zmq.Poller()
        poller.register(frontend, zmq.POLLIN)
        poller.register(backend, zmq.POLLIN)
        
        workers = WorkerQueue()
        mq = [] #non FIFO queue
        activeTrees = set()    
        heartbeat_at = time.time() + self.BEAT_INTERVAL
        
        while True:
            socks = dict(poller.poll(self.BEAT_INTERVAL * 1000))
            #print socks.get(frontend,None), socks.get(backend,None), workers, activeTrees, mq

            # Handle worker activity on backend
            if socks.get(backend) == zmq.POLLIN:
                # Use worker address for LRU routing
                frames = backend.recv_multipart()
                if not frames:
                    break
        
                address = frames[0]
                workers.ready(Worker(address,self.EXPECTED_PERFORMANCE, self.BEAT_LIVENESS))
        
                # Validate control message, or return reply to client
                msg = frames[1:]
                if len(msg) > 1:
                    tree = frames.pop()
                    #print "worker", tree, frames
                    frontend.send_multipart(msg)
                    activeTrees.remove(tree)
        
                # Send heartbeats to idle workers if it's time
                if time.time() >= heartbeat_at:
                    for worker in workers:
                        msg = [worker, SDB_HEARTBEAT]
                        backend.send_multipart(msg)
                    heartbeat_at = time.time() + self.BEAT_INTERVAL
        			
            #Work with existing queue first
            t = time.time()
            remove = []
            for index, msg in enumerate(mq):
                if t > msg.expiry:
                    msg[-1] = SDB_TIMEOUT
                    frontend.send_multipart(msg)
                    remove.append(index)
                else:
                    if msg.tree not in activeTrees and len(workers) > 0:
                        activeTrees.add(msg.tree)
                        msg.frame.insert(0,workers.next())
                        backend.send_multipart(msg.frame)
                        remove.append(index)
            for index in remove:
                mq.pop(index)   			
        			
            if socks.get(frontend) == zmq.POLLIN:
        	           			
                frames = frontend.recv_multipart()
                if len(frames) == 4:
                    timeout = int(frames.pop())*1e-3 - (self.EXPECTED_PERFORMANCE * 
        			                                    self.BEAT_LIVENESS) + time.time()
                else:
                    timeout = EXPECTED_WORKER_PERFORMANCE + time.time()
                if timeout < 0:
                    msg[-1] = SDB_TIMEOUT
                    frontend.send_multipart(msg)                      
                else:
                    tree = get_tree(frames[-1])
                    if not tree:
                        tree = SDB_NONTREE
                    if tree not in activeTrees and len(workers) > 0:
                        activeTrees.add(tree)
                        frames.insert(0, workers.next())
                        backend.send_multipart(frames)
                    else:         
                        msg = Message(frames, tree, timeout)
                        mq.append(msg)
        
            workers.purge()
			

class WorkerThread(threading.Thread):

    def __init__(self, context, hi, hl, interval, interval_max):
        super(WorkerThread, self).__init__()
        self.context = context
        self.BEAT_INTERVAL = hi
        self.BEAT_LIVENESS = hl
        self.INTERVAL_INIT = interval
        self.INTERVAL_MAX = interval_max
		
        self.worker = context.socket(zmq.DEALER) 	
        identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        self.worker.setsockopt(zmq.IDENTITY, identity)
        self.worker.setsockopt(zmq.LINGER, 0)
        self.worker.connect("inproc://workers")
		
        self.poller = zmq.Poller()
        self.poller.register(self.worker, zmq.POLLIN)
        print "Started Worker-" + identity

 		
    def run(self):
        self.worker.send(SDB_READY)    
        liveness = self.BEAT_LIVENESS
        interval = self.INTERVAL_INIT
        
        heartbeat_at = time.time() + self.BEAT_INTERVAL

        cycles = 0
        while True:
            socks = dict(self.poller.poll(self.BEAT_INTERVAL * 1000))
        
            # Handle worker activity on backend
            if socks.get(self.worker) == zmq.POLLIN:
                #  Get message
                #  - 3+-part envelope + content -> request
                #  - 1-part HEARTBEAT -> heartbeat
                frames = self.worker.recv_multipart()
                if len(frames) == 3:
                    tree = get_tree(frames[-1])
                    frames.append(tree)
                    #print "I: Normal reply", frames
                    time.sleep(5)  # Do some heavy work
                    self.worker.send_multipart(frames)
         
                    liveness = self.BEAT_LIVENESS
                elif len(frames) == 1 and frames[0] == SDB_HEARTBEAT:
                    #print "I: Queue heartbeat"
                    liveness = self.BEAT_LIVENESS
                interval = self.INTERVAL_INIT
            else:
                liveness -= 1
                liveness = max(liveness, 0)
                if liveness == 0:
                    #print "W: Heartbeat failure, can't reach queue"
                    #print "W: Reconnecting in %0.2fs..." % interval
                    time.sleep(interval)
        
                    if interval < INTERVAL_MAX:
                        interval *= 2
                    else:
                        break
            if time.time() > heartbeat_at:
                heartbeat_at = time.time() + self.BEAT_INTERVAL
                #print "I: Worker heartbeat"
                self.worker.send(SDB_HEARTBEAT)
	
context = zmq.Context(1)
PORT = 5555
HEARTBEAT_LIVENESS = 3     
HEARTBEAT_INTERVAL = 1.0  
EXPECTED_WORKER_PERFORMANCE = 5.0
INTERVAL_INIT = 1
INTERVAL_MAX = 32
NBR_WORKERS = 2

bthread = BrokerThread(context, PORT, HEARTBEAT_INTERVAL, 
                       HEARTBEAT_LIVENESS, EXPECTED_WORKER_PERFORMANCE)
					  
bthread.start()

for _ in range(NBR_WORKERS):
    wthread = WorkerThread(context, HEARTBEAT_INTERVAL, HEARTBEAT_LIVENESS,
                        INTERVAL_INIT, INTERVAL_MAX)						
    wthread.start()
