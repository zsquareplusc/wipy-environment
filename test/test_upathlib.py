#! /usr/bin/env python3
"""\
Tests for upathlib.
"""

import os
import unittest

test_root = os.path.dirname(__file__)

class Test_upathlib(unittest.TestCase):

    def test_create(self):
        p = upathlib.Path('/')
        self.assertFalse(p._parts)
        self.assertTrue(p._is_abs)
        #~ self.assertEqual(p.root, '/')
        #~ self.assertEqual(p.drive, '')
        #~ self.assertEqual(p.anchor, '/')

    #~ def test_parents(self):
        #~ p = upathlib.Path('/1/2/3/x')
        #~ self.assertEqual(tuple(p.parents), ('3', '2', '1'))

    def test_name(self):
        self.assertEqual(upathlib.Path('/1/2/3/x').name, 'x')
        self.assertEqual(upathlib.Path('1/2/3/x').name, 'x')
        self.assertEqual(upathlib.Path('/x').name, 'x')
        self.assertEqual(upathlib.Path('x').name, 'x')

    #~ def suffix:
    #~ def suffixes:
    #~ def stem:

    def test_is_absolute(self):
        self.assertTrue(upathlib.Path('/1/2/3/x').is_absolute())
        self.assertFalse(upathlib.Path('.').is_absolute())
        self.assertFalse(upathlib.Path('a').is_absolute())

    #~ def joinpath(self, *other):
    #~ def match(self, pattern):
    #~ def relative_to(self, *other):
    #~ def with_name(self, name):
    #~ def with_suffix(self, suffix):
    #~ def __eq__(self, other):
    #~ def __lt__(self, other):
    #~ def __contains__(self, other):

    def test_div(self):
        self.assertEqual(upathlib.Path('1', '2'), upathlib.Path('1') / '2')

    def test_cwd(self):
        self.assertEqual(str(upathlib.Path.cwd()), os.getcwd())

    def test_stat(self):
        self.assertTrue(upathlib.Path(test_root, 'test_upathlib.py').stat())
        #~ self.assertRaises(upathlib.Path('wontfindme').stat(), OSError)

    def test_exists(self):
        self.assertTrue(upathlib.Path(test_root, 'test_upathlib.py').exists())
        self.assertFalse(upathlib.Path('wontfindme').exists())

    #~ def glob(self, pattern):

    def test_is_dir(self):
        self.assertTrue(upathlib.Path('.').is_dir())
        self.assertFalse(upathlib.Path(test_root, 'test_upathlib.py').is_dir())

    def test_is_file(self):
        self.assertFalse(upathlib.Path('.').is_file())
        self.assertTrue(upathlib.Path(test_root, 'test_upathlib.py').is_file())

    #~ def iterdir(self):
    #~ def mkdir(self, mode=0o777, parents=False):
    #~ def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
    #~ def rename(self, target):
    #~ def replace(self, target):
    #~ def resolve(self):
    #~ def rmdir(self):
    #~ def touch(self):
    #~ def unlink(self):

    def test_untests(self):
        """a few calls with output for manual verification"""
        print('XXX')
        print('test/', list(upathlib.Path(test_root).iterdir()))
        print('../', list(upathlib.Path(test_root, '..').iterdir()))


if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../device/flash/lib'))
    import upathlib
    unittest.main()
