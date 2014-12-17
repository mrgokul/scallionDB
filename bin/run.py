import sys, os, zmq
sys.path.append(os.path.abspath('../src/python'))
from scallionDB.routing.threads import BrokerThread, WorkerThread


context = zmq.Context(1)
PORT = 27890
HEARTBEAT_LIVENESS = 3     
HEARTBEAT_INTERVAL = 1.0  
EXPECTED_WORKER_PERFORMANCE = 5.0
INTERVAL_INIT = 1
INTERVAL_MAX = 32
NBR_WORKERS = 2
trees = {}

bthread = BrokerThread(context, PORT, HEARTBEAT_INTERVAL, 
                       HEARTBEAT_LIVENESS, EXPECTED_WORKER_PERFORMANCE, trees)
					  
bthread.start()

for _ in range(NBR_WORKERS):
    wthread = WorkerThread(context, HEARTBEAT_INTERVAL, HEARTBEAT_LIVENESS,
                        INTERVAL_INIT, INTERVAL_MAX, trees)						
    wthread.start()
