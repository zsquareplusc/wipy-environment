ulog
====

A simple logging module with the capability to log to multiple targets,
including a remote syslog.

There is currently no filtering of loglevels in :mod:`ulog` itself. All
messages that are logged, are sent to the log handlers (including remote) which
may have a performance impact.


Logger
------
.. class:: Logger

    .. method:: __init__(prefix='', facility=LOG_USER)

        Create a new logger where the prefix is inserted in each message.

    .. method:: log(priority, message)

        Write a log message of given priority (see ``LOG_`` constants below).

    .. method:: debug(message)

        Write a log message with the priority LOG_DEBUG.

    .. method:: info(message)

        Write a log message with the priority LOG_INFO.

    .. method:: notice(message)

        Write a log message with the priority LOG_NOTICE.

    .. method:: warn(message)

        Write a log message with the priority LOG_WARN.

    .. method:: error(message)

        Write a log message with the priority LOG_ERROR.


One instance of the logger is precreated:

.. attribute:: root

    A :class:`Logger()` instance with empty prefix.

Examples::

    >>> ulog.root.info('Hello world!')
    >>> log = ulog.root.Logger('Demo: ')
    >>> log.info('Hello world!')


Configuration
-------------

.. function:: add_remote(host, port=514)

    :param host: Hostname or IP address
    :param port: UDP port number

    Add remote syslog destination. A new handler is created and
    added to the list. All log messages will be sent, each as single UDP
    packet to the specified address. The format is compatible to (older)
    syslog, so an other computer can be the receiver for these messages.


Constants
---------
Priorities (corresponding to the definitions of syslog):

.. attribute:: LOG_EMERG
.. attribute:: LOG_ALERT
.. attribute:: LOG_CRIT
.. attribute:: LOG_ERR
.. attribute:: LOG_WARNING
.. attribute:: LOG_NOTICE
.. attribute:: LOG_INFO
.. attribute:: LOG_DEBUG
