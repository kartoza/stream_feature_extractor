# coding=utf-8
"""
Custom logging for Stream feature extractor.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import logging
from datetime import date
import getpass
from tempfile import mkstemp

from PyQt4 import QtCore

third_party_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'third_party'))
if third_party_path not in sys.path:
    sys.path.append(third_party_path)
# pylint: disable=F0401
# noinspection PyUnresolvedReferences
from raven.handlers.logging import SentryHandler
# noinspection PyUnresolvedReferences
from raven import Client
# pylint: enable=F0401
LOGGER = logging.getLogger('SFE')


class QgsLogHandler(logging.Handler):
    """A logging handler that will log messages to the QGIS logging console."""

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)

    def emit(self, message):
        """Try to log the message to QGIS if available, otherwise do nothing.

        :param message: logging message containing whatever info needs to be
                logged.
        :type message: str
        """
        try:
            from qgis.core import QgsMessageLog
            # Check logging.LogRecord properties for lots of other goodies
            # like line number etc. you can get from the log message.
            # noinspection PyCallByClass
            QgsMessageLog.logMessage(message, 'QGIS', 0)
        #Make sure it doesn't crash if using without QGIS
        except ImportError:
            pass
        except MemoryError:
            message = (
                'Due to memory limitations on this machine, the full log '
                'cannot be handled.')
            print message
            # noinspection PyUnboundLocalVariable
            QgsMessageLog.logMessage(message, 'QGIS', 0)


def add_logging_handler_once(logger, handler):
    """A helper to add a handler to a logger, ensuring there are no duplicates.

    :param logger: Logger that should have a handler added.
    :type logger: logging.logger

    :param handler: Handler instance to be added. It will not be added if an
        instance of that Handler subclass already exists.
    :type handler: logging.Handler

    :returns: True if the logging handler was added, otherwise False.
    :rtype: bool
    """
    class_name = handler.__class__.__name__
    for handler in logger.handlers:
        if handler.__class__.__name__ == class_name:
            return False

    logger.addHandler(handler)
    return True


def setup_logger(sentry_url, log_file=None):
    """Run once when the module is loaded and enable logging.

    :param sentry_url: Mandatory url to sentry api for remote logging.
        Consult your sentry instance for the client instance url.
    :type sentry_url: str

    :param log_file: Optional full path to a file to write logs to.
    :type log_file: str

    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html

    Use this to first initialise the logger in your __init__.py::

       import custom_logging
       custom_logging.setup_logger('http://path to sentry')

    You would typically only need to do the above once ever as the
    safe model is initialised early and will set up the logger
    globally so it is available to all packages / subpackages as
    shown below.

    In a module that wants to do logging then use this example as
    a guide to get the initialised logger instance::

       # The LOGGER is initialised in utilities.py by init
       import logging
       LOGGER = logging.getLogger('QGIS')

    Now to log a message do::

       LOGGER.debug('Some debug message')

    .. note:: The file logs are written to the user tmp dir e.g.:
       /tmp/23-08-2012/timlinux/logs/qgis.log

    """
    logger = logging.getLogger('QGIS')
    logger.setLevel(logging.DEBUG)
    default_handler_level = logging.DEBUG
    # create formatter that will be added to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # create syslog handler which logs even debug messages
    log_temp_dir = temp_dir('logs')
    path = os.path.join(log_temp_dir, 'qgis.log')
    if log_file is None:
        file_handler = logging.FileHandler(path)
    else:
        file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(default_handler_level)
    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    qgis_handler = QgsLogHandler()

    # Sentry handler - this is optional hence the localised import
    # It will only log if pip install raven. If raven is available
    # logging messages will be sent to the sentry host.
    # We will only log exceptions. You need to either:
    #  * Set env var 'SENTRY' present (value can be anything)
    #  * Enable the 'plugins/use_sentry' QSettings option
    # before this will be enabled.
    settings = QtCore.QSettings()
    flag = settings.value('stream-feature-extractor/sentry-logging', False)
    if 'SENTRY' in os.environ or flag:
        client = Client(sentry_url)
        sentry_handler = SentryHandler(client)
        sentry_handler.setFormatter(formatter)
        sentry_handler.setLevel(logging.ERROR)
        if add_logging_handler_once(logger, sentry_handler):
            logger.debug('Sentry logging enabled')
    else:
        logger.debug('Sentry logging disabled')
    # Set formatters
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    qgis_handler.setFormatter(formatter)

    # add the handlers to the logger
    add_logging_handler_once(logger, file_handler)
    add_logging_handler_once(logger, console_handler)
    add_logging_handler_once(logger, qgis_handler)


def temp_dir(sub_dir='work'):
    r"""Obtain the temporary working directory for the operating system.

    :param sub_dir: Optional argument which will cause an additional
        subdirectory to be created.
    :type sub_dir: str

    :returns: Path to the temporary folder placed in the system temp dir.
    :rtype: str
    """
    user = getpass.getuser().replace(' ', '_')
    current_date = date.today()
    date_string = current_date.isoformat()

    # Following 4 lines are a workaround for tempfile.tempdir()
    # unreliabilty
    handle, filename = mkstemp()
    os.close(handle)
    new_directory = os.path.dirname(filename)
    os.remove(filename)

    temp_path = os.path.join(
        new_directory, date_string, user, sub_dir)

    if not os.path.exists(temp_path):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        old_mask = os.umask(0000)
        os.makedirs(temp_path, 0777)
        # Reinstate the old mask for tmp
        os.umask(old_mask)
    return temp_path
