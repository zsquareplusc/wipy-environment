#! /usr/bin/env python3
"""\
Class working with paths
"""
import os

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
    root = '/'  # name of root directory
    anchor = '/' # drive + root

    @property
    def parents(self):
        return tuple(self._parts[:-1])

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

    #~ def as_posix(self)
        #~ return '/'.join(pathsegments)

    #~ def as_uri(self):
        #~ return 'file://{}'.format(self.as_posix())

    def is_absolute(self):
        return self._is_abs

    #~ def is_reserved(self):
        #~ return False

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

    #~ def __eq__(self, other):
    #~ def __lt__(self, other):
    #~ def __contains__(self, other):
    #~ def __div__(self, other):

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
