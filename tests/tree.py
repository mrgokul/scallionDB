import os, sys, unittest
sys.path.append(os.path.abspath('../src/python'))

from scallionDB.test import tree
suite = unittest.TestLoader().loadTestsFromModule(tree)
unittest.TextTestRunner(verbosity=2).run(suite)