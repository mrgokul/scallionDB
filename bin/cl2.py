import sys
sys.path.append('C:/Users/Nachiappan.Palaniapp/Documents/GitHub/scallionDB/src/python/')
from scallionDB.pyscallion import ScallionClient
from scallionDB.parser import parse_request
client = ScallionClient()
tree = client['new']
r = tree.getNode({"foo":"bus"})
print r