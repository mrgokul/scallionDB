import sys, os, zmq
sys.path.append(os.path.abspath('../src/python'))
from scallionDB.routing import BrokerThread, WorkerThread, FlusherThread, LoaderThread
from collections import Counter
import ConfigParser
import logging

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

config = ConfigParser.ConfigParser()
config_folder = os.path.abspath('../conf')
config.read(os.path.join(config_folder,'scallion.conf'))

PORT = config.get('INIT','PORT')
HEARTBEAT_LIVENESS = int(config.get('INIT','HEARTBEAT_LIVENESS'))
HEARTBEAT_INTERVAL = int(config.get('INIT','HEARTBEAT_INTERVAL'))
EXPECTED_WORKER_PERFORMANCE = int(config.get('INIT','EXPECTED_WORKER_PERFORMANCE'))
INTERVAL_INIT = int(config.get('INIT','INTERVAL_INIT'))
INTERVAL_MAX = int(config.get('INIT','INTERVAL_MAX'))
NBR_WORKERS = int(config.get('INIT','NBR_WORKERS'))
flushLimit = int(config.get('INIT','flushLimit'))
chunksize = int(config.get('INIT','chunksize'))
folder = os.path.abspath(config.get('INIT','data_folder'))

logfolder = os.path.abspath('../log')
formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(message)s',
                              '%Y-%m-%d %H:%M:%S')

commlog = logging.getLogger('commit')
c_handler = logging.FileHandler(os.path.join(logfolder,'commit','commit.log'))
c_handler.setFormatter(formatter)
commlog.addHandler(c_handler)
commlog.level = 20

errlog = logging.getLogger('error')
err_handler = logging.FileHandler(os.path.join(logfolder,'error','error.log'))
err_handler.setFormatter(formatter)
errlog.addHandler(err_handler)
errlog.level = 20

flushlog = logging.getLogger('flush')
f_handler = logging.FileHandler(os.path.join(logfolder,'flush','flush.log'))
f_handler.setFormatter(formatter)
flushlog.addHandler(f_handler)
flushlog.level = 20

consolelog = logging.getLogger('root')
con_handler = logging.StreamHandler()
con_handler.setFormatter(formatter)
consolelog.addHandler(con_handler)
consolelog.level = 20



context = zmq.Context(1)
trees = {}
flushCounter = Counter()

bthread = BrokerThread(context, PORT, HEARTBEAT_INTERVAL, 
                       HEARTBEAT_LIVENESS, EXPECTED_WORKER_PERFORMANCE,
 					   trees, flushCounter, flushLimit)
					  
bthread.start()
consolelog.info('Started Broker')

for _ in range(NBR_WORKERS):
    wthread = WorkerThread(context, HEARTBEAT_INTERVAL, HEARTBEAT_LIVENESS,
                           INTERVAL_INIT, INTERVAL_MAX, trees, chunksize,
						   folder, commlog, errlog)						
    wthread.start()
consolelog.info('Started Workers')	

fthread = FlusherThread(context, trees, flushCounter, folder, flushlog, errlog)

fthread.start()

lthread = LoaderThread(context, PORT, folder, consolelog)
consolelog.info('Started Loading trees')
lthread.start()
lthread.join()
consolelog.info('Finished Loading trees')
