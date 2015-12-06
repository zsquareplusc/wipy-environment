upathlib
========

This module provides a subset of the Python :mod:`pathlib`.

.. class:: Path

    Manage a path on the filesystem.

    .. method:: __init__(\*pathsegments)

        :param pathsegments: one or more strings representing a path.

    .. method:: __str__

        :return str: return full path as string.

    .. attribute:: name

        Return the filename without directories.

    .. attribute:: is_absolute

        :returns bool: if path is starting with a slash.


    Testing/reading files/directories:

    .. method:: exists()

        :returns bool: return if the target of the path exists

    .. method:: stat()

        :return tuple: file stats (access times, size etc.).

    .. method:: iterdir()

        :returns iterator: get an iterator that yields path objects for all
                           files and subdirectories of that path.

    .. method:: is_dir

        :returns bool: return if path is pointing to a directory.

    .. method:: is_file

        :returns bool: return if path is pointing to a normal file.


    Modifying files/directories:

    .. method:: open(mode='r')

        :returns fileobj: Open the file represented by the path.

    .. method:: rename(target)

        Change filename of current path.

    .. method:: mkdir()

        Create a directory representing the current path.

    .. method:: rmdir()

        Delete current path if it is an empty direcotry.

    .. method:: unlink()

        Delete current path if it is a regular file.

    Sorting:

    ``__eq__`` and ``__lt__`` are implemented so that paths can be compared lexically.

    Operator:

    .. method:: __truediv__(other)

        :param other: A path object or string.
        :returns Path: new Path instance with combined paths
        The operator ``/`` is implemented to join path segments.

    Class Methods:

    .. method:: cwd()

        :returns Path: get a Path object pointing to the current directory.


Module Attributes:

.. attribute:: S_IFDIR = 0x4000
.. attribute:: S_IFREG = 0x8000

