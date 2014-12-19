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

#  ScallionDB Protocol constants
SDB_READY = "\x01"      # Signals worker is ready
SDB_HEARTBEAT = "\x02"  # Signals worker heartbeat
SDB_TIMEOUT = "\x03"    # Signals timeout to client
SDB_NONTREE = "\x04"    # For Non-tree statements, precedes response message
SDB_MESSAGE = "\x05"    # For any message response, precedes response message
SDB_COMPLETE = "\x06"   # For completed, precedes tree name
SDB_FAILURE = "\x07"    # Failure message, precedes error message