#  ScallionDB Protocol constants
SDB_READY = "\x01"      # Signals worker is ready
SDB_HEARTBEAT = "\x02"  # Signals worker heartbeat
SDB_TIMEOUT = "\x03"    # Signals timeout to client
SDB_NONTREE = "\x03"    # For Non-tree statements