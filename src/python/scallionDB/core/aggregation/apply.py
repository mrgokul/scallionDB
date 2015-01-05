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
 
 
def add(iplist):
    if isinstance(iplist,list):
        return sum([i for i in iplist if i is not None])
    else:
        return 0
		
def sum1(iplist):
    if isinstance(iplist,list):
        return len(iplist)
    else:
        return 0 
		
def count(iplist):
    if isinstance(iplist,list):
        return len([i for i in iplist if i is not None])
    else:
        return 0

def unique(iplist):
    if isinstance(iplist,list):
        return list(set([i for i in iplist if i is not None]))
    else:
        return None

def append(iplist):
    if all([isinstance(e,list) for e in iplist]):
        return reduce(lambda x,y: x+y,iplist)
    else:
        return None

def union(iplist):
    if all([isinstance(e,list) for e in iplist]):
        return list(reduce(lambda x,y: set.union(set(x),set(y)),iplist))
    else:
        return None

def intersection(iplist):
    if all([isinstance(e,list) for e in iplist]):
        return list(reduce(lambda x,y: set.intersection(set(x),set(y)),iplist))
    else:
        return None

def lenunique(iplist):
    if isinstance(iplist,list):
        return count(unique(iplist))
    else:
        return 0

def avg(iplist):
    if iplist and isinstance(iplist,list):
        return add(iplist)/(1.0*len(iplist))
    else:
        return 0

def avg1(iplist):
    if  isinstance(iplist,list) and count(iplist):
        return add(iplist)/(1.0*count(iplist))
    else:
        return 0
		
def minimum(iplist):
    if  iplist and isinstance(iplist,list):
        return min(iplist)
    else:
        return None
		
def maximum(iplist):
    if  iplist and isinstance(iplist,list):
        return max(iplist)
    else:
        return None
		

