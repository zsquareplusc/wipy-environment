#! /usr/bin/env python3
"""\
Tests for upathlib.
"""

import os
import unittest

class Test_upathlib(unittest.TestCase):

    def test_create(self):
        p = upathlib.Path('/')
        self.assertFalse(p._parts)
        self.assertTrue(p._is_abs)
        self.assertEqual(p.root, '/')
        #~ self.assertEqual(p.drive, '')
        self.assertEqual(p.anchor, '/')

    def test_parents(self):
        p = upathlib.Path('/1/2/3/x')
        self.assertEqual(tuple(p.parents), ('1', '2', '3'))

    def test_name(self):
        p = upathlib.Path('/1/2/3/x')
        self.assertEqual(p.name, 'x')

    #~ def suffix:
    #~ def suffixes:
    #~ def stem:
    #~ def as_posix(self)
    #~ def as_uri(self):

    def test_is_absolute(self):
        self.assertTrue(upathlib.Path('/1/2/3/x').is_absolute())
        self.assertFalse(upathlib.Path('.').is_absolute())
        self.assertFalse(upathlib.Path('a').is_absolute())

    #~ def is_reserved(self):
    #~ def joinpath(self, *other):
    #~ def match(self, pattern):
    #~ def relative_to(self, *other):
    #~ def with_name(self, name):
    #~ def with_suffix(self, suffix):
    #~ def __eq__(self, other):
    #~ def __lt__(self, other):
    #~ def __contains__(self, other):
    #~ def __div__(self, other):

    #~ @classmethod
    def test_cwd(self):
        self.assertEqual(str(upathlib.Path.cwd()), os.getcwd())

    def test_stat(self):
        self.assertTrue(upathlib.Path('test_upathlib.py').stat())
        #~ self.assertRaises(upathlib.Path('wontfindme').stat(), OSError)

    def test_exists(self):
        self.assertTrue(upathlib.Path('test_upathlib.py').exists())
        self.assertFalse(upathlib.Path('wontfindme').exists())

    #~ def glob(self, pattern):
    #~ def is_dir(self):
    #~ def is_file(self):
    #~ def is_symlink(self):
    #~ def is_socket(self):
    #~ def is_fifo(self):
    #~ def is_block_device(self):
    #~ def is_char_device(self):
    #~ def iterdir(self):
    #~ def lchmod(self, mode):
    #~ def lstat(self):
    #~ def mkdir(self, mode=0o777, parents=False):
    #~ def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
    #~ def owner(self):
    #~ def rename(self, target):
    #~ def replace(self, target):
    #~ def resolve(self):
    #~ def rglob(self, pattern):
    #~ def rmdir(self):
    #~ def symlink_to(self, target, target_is_directory=False):
    #~ def unlink(self):

if __name__ == '__main__':
    import sys
    sys.path.append('../device/flash/lib')
    import upathlib
    unittest.main()
