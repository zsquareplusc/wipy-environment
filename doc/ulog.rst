ulog
====

A simple logging module with the capability to log to multiple targets, include a remote syslog.

.. class:: Logger

    .. method:: __init__(prefix='', facility=LOG_USER)

        Create a new logger where the prefix is inserted in each message.

    .. method log(priority, message)

        Write a log message of given priority.

    .. method: debug(message)

        Write a log message with the priority DEBUG.

    .. method:: info(message)

        Write a log message with the priority LOG_INFO.

    .. method:: notice(message)

        Write a log message with the priority LOG_NOTICE.

    .. method:: warn(message)

        Write a log message with the priority LOG_WARN.

    .. method:: error(message)

        Write a log message with the priority LOG_ERROR.


.. attribute:: root

    A :class:`Logger()` instance with empty prefix.

.. function:: add_remote(host, port=514)

    :param host: Hostname or IP address
    :param port: TCP/UDP port number

    Add remote syslog destination. A new handler is created and added to the
    list.  All log messages will be sent, each as single UDP packet to the
    specified address. The format is compatible to rsyslog, so an other
    computer can be the receiver for these messages.

