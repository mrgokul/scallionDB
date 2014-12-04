import os, sys, unittest
sys.path.append(os.path.abspath('../src/python'))

from scallionDB.test import parser_exp
suite = unittest.TestLoader().loadTestsFromModule(parser_exp)
unittest.TextTestRunner(verbosity=2).run(suite)
