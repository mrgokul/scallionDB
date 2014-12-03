from collections import OrderedDict
import time

class Worker(object):
    def __init__(self, address, ewp, hl):
        self.address = address
        self.expiry = time.time() + ewp * hl 

class WorkerQueue(OrderedDict):

    def ready(self, worker):
        self.pop(worker.address, None)
        self[worker.address] = worker

    def purge(self):
        """Look for & kill expired workers."""
        t = time.time()
        expired = []
        for address,worker in self.iteritems():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            print "W: Idle worker expired: %s" % address
            self.pop(address, None)

    def next(self):
        address, worker = self.popitem(False)
        return address
		
class Message(object):
    def __init__(self, frame, tree, expiry):
        self.frame = frame
        self.tree = tree
        self.expiry = time.time() + expiry