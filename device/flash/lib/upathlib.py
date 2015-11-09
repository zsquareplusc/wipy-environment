#! /usr/bin/env python3
"""\
Class working with paths
"""
# Methods that are not implemented, compared to standard pathlib:
# is_symlink(), is_socket(), is_fifo(), is_block_device(), is_char_device(),
# as_posix(), as_uri(), is_reserved(), lchmod(), lstat(), symlink_to(),
# owner()
# Attributes that are not implemented, compared to standard pathlib:
# drive, root, anchor

# a few more may not yet be implemented

import os

S_IFDIR = 0x4000
S_IFREG = 0x8000


class Path(object):
    def __init__(self, *pathsegments):
        full = '/'.join(pathsegments)
        self._is_abs = full.startswith('/')
        if self._is_abs:
            full = full[1:]
        if full:
            self._parts = full.split('/')
        else:
            self._parts = []

    #~ drive = ''   # we have no drives
    #~ root = '/'  # name of root directory
    #~ anchor = '/' # drive + root

    #~ @property
    #~ def parents(self):
        #~ return tuple(reversed(self._parts[:-1]))

    @property
    def name(self):
        return self._parts[-1]

    #~ @property
    #~ def suffix(self):
        #~ return self.name.split('.')[-1]

    #~ @property
    #~ def suffixes(self):
        #~ return self.name.split('.')[1:]

    #~ @property
    #~ def stem(self):
        #~ return self.name.split('.')[0]

    def is_absolute(self):
        return self._is_abs

    #~ def joinpath(self, *other):
        #~ return Path(self.parts + other)

    #~ def match(self, pattern):
    #~ def relative_to(self, *other):
    #~ def with_name(self, name):
        #~ return Path(self.pathsegments[:-1] + [name])
    #~ def with_suffix(self, suffix):
        #~ return Path(self.pathsegments[:-1] + [self.stem + suffix])

    def __str__(self):
        return '{}{}'.format(
                '/' if self._is_abs else '',
                '/'.join(self._parts))

    def __repr__(self):
        return "Path('{}')".format(self)

    def __eq__(self, other):
        if isinstance(other, Path):
            return str(self) == str(other)
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, Path):
            return str(self) < str(other)
        else:
            return False

    #~ def __contains__(self, other):

    def __truediv__(self, other):
        return Path(str(self), other)

    @classmethod
    def cwd(cls):
        return Path(os.getcwd())

    def stat(self):
        return os.stat(str(self))

    def exists(self):
        try:
            os.stat(str(self))
            return True
        except OSError:
            return False

    #~ def glob(self, pattern):

    def is_dir(self):
        return (self.stat()[0] & S_IFDIR) != 0

    def is_file(self):
        return (self.stat()[0] & S_IFREG) != 0

    def iterdir(self):
        for name in os.listdir(str(self)):
            yield Path(str(self), name)

    #~ def mkdir(self, mode=0o777, parents=False):
    def mkdir(self):
        os.mkdir(str(self))

    #~ def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
    def open(self, mode='r'):
        return open(str(self), mode)

    def rename(self, target):
        os.rename(str(self), target)

    #~ def replace(self, target):
    #~ def resolve(self):
    #~ def rglob(self, pattern):

    def rmdir(self):
        os.rmdir(str(self))

    #~ def touch(self):

    def unlink(self):
        os.unlink(str(self))
