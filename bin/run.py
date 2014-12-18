import sys, os, zmq
sys.path.append(os.path.abspath('../src/python'))
from scallionDB.routing import BrokerThread, WorkerThread, FlusherThread, LoaderThread
from collections import Counter
import logging

logfolder = os.path.abspath('../log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger('scallionDB')
logger.setLevel(logging.DEBUG)

rlog = logging.StreamHandler()
rlog.setLevel(logging.DEBUG)
#rlog.setFormatter(formatter)

flog = logging.FileHandler(os.path.join(logfolder,'flush','flush.log'))
flog.setLevel(logging.DEBUG)
flog.setFormatter(formatter)

elog = logging.FileHandler(os.path.join(logfolder,'error','error.log'))
elog.setLevel(logging.ERROR)
elog.setFormatter(formatter)

clog = logging.FileHandler(os.path.join(logfolder,'commit','commit.log'))
clog.setLevel(logging.DEBUG)
clog.setFormatter(formatter)




context = zmq.Context(1)
PORT = 27890
HEARTBEAT_LIVENESS = 3     
HEARTBEAT_INTERVAL = 1.0  
EXPECTED_WORKER_PERFORMANCE = 5.0
INTERVAL_INIT = 1
INTERVAL_MAX = 32
NBR_WORKERS = 2
trees = {}
flushCounter = Counter()
flushLimit = 2
folder = os.path.abspath('../data')

bthread = BrokerThread(context, PORT, HEARTBEAT_INTERVAL, 
                       HEARTBEAT_LIVENESS, EXPECTED_WORKER_PERFORMANCE,
 					   trees, flushCounter, flushLimit)
					  
bthread.start()

for _ in range(NBR_WORKERS):
    wthread = WorkerThread(context, HEARTBEAT_INTERVAL, HEARTBEAT_LIVENESS,
                        INTERVAL_INIT, INTERVAL_MAX, trees, folder)						
    wthread.start()
	
fthread = FlusherThread(context, trees, flushCounter, folder)

fthread.start()

lthread = LoaderThread(context, PORT, folder)
rlog.info('Started Loading trees')
lthread.start()
lthread.join()
rlog.info('Finished Loading trees')
