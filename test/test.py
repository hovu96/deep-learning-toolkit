import os
import sys

bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "bin"))
if bin_path not in sys.path:
    sys.path.insert(0, bin_path)
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "lib"))
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

import unittest
import inspect

from dltk.test.cases import *

test_types = []
for name in dir():
    t = getattr(sys.modules[__name__], name)
    if inspect.isclass(t):
        if issubclass(t, unittest.TestCase):
            test_types.append(t)

suite = unittest.TestSuite()
for test_type in test_types:
    test = test_type()
    suite.addTest(test)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
