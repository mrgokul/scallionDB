import os, sys, unittest
sys.path.append(os.path.abspath('../src/python'))

from scallionDB.test import parser
suite = unittest.TestLoader().loadTestsFromModule(parser)
unittest.TextTestRunner(verbosity=2).run(suite)