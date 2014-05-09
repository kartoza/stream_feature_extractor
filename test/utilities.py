# coding=utf-8
"""Common functionality used by regression tests."""

import os
import sys
import logging
import hashlib
from datetime import datetime
from shutil import copy2


LOGGER = logging.getLogger('QGIS')
QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None
TEMP_DIR = os.path.join(
    os.path.expanduser('~'), 'temp', 'extractor')


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from PyQt4 import QtGui, QtCore
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas
        from qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP  # pylint: disable=W0603

    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode
        #noinspection PyPep8Naming
        QGIS_APP = QgsApplication(sys.argv, gui_flag)
        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

    global PARENT  # pylint: disable=W0603
    if PARENT is None:
        #noinspection PyPep8Naming
        PARENT = QtGui.QWidget()

    global CANVAS  # pylint: disable=W0603
    if CANVAS is None:
        #noinspection PyPep8Naming
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE  # pylint: disable=W0603
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        #noinspection PyPep8Naming
        IFACE = QgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT


def get_random_string(length=7):
    """Return random string with length=length.

    :param length: length of the produced string
    :type length: int

    :returns: random string
    :rtype: str
    """
    return hashlib.sha512(str(datetime.now())).hexdigest()[:length]


def copy_temp_layer(shapefile_path, temp_dir=TEMP_DIR):
    """Copy shapefile_path to temp directory and weird name.

    :param shapefile_path: a path to shapefile
    :type shapefile_path: str

    :param temp_dir: temporary directory for saving the temporary shapefile
    :type temp_dir: str

    :returns: path to temporary shapefile
    :rtype: str
    """
    # Avoid error
    if not os.path.exists(shapefile_path):
        raise OSError('Failed to copy.')

    current_date = datetime.now().strftime('%Y%m%d')
    temp_dir = os.path.join(temp_dir, current_date)

    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except OSError:
            raise OSError('Failed to create dirs %s.' % temp_dir)

    exts = ['cpg', 'dbf', 'prj', 'qpj', 'shp', 'shx']
    filename = os.path.basename(shapefile_path)
    basename, ext = os.path.splitext(filename)
    parent_dir = os.path.dirname(shapefile_path)

    random_basename = get_random_string()
    for ext in exts:
        real_file = os.path.join(parent_dir, basename + '.' + ext)
        if not os.path.exists(real_file):
            continue
        # copy file
        temp_file = os.path.join(temp_dir, random_basename + '.' + ext)
        copy2(real_file, temp_file)

    # Checking
    temp_shapefile = os.path.join(temp_dir, random_basename + '.shp')
    if os.path.exists(temp_shapefile):
        return temp_shapefile
    else:
        raise OSError('Failed to copy.')


def get_shapefile_layer(shapefile_path, title):
    """Return a layer of shapefile from shapefile_path.

    :param shapefile_path: a file path to the shapefile
    :type shapefile_path: str

    :param title: the title of the layer
    :type title: str

    :param temp_dir: temporary directory for saving the temporary shapefile
    :type temp_dir: str

    :returns: A layer
    :rtype: QGISVectorLayer
    """
    layer = QgsVectorLayer(shapefile_path, title, 'ogr')
    return layer


def get_temp_shapefile_layer(shapefile_path, title, temp_dir=TEMP_DIR):
    """Return a copy of layer of shapefile from shapefile_path.

    :param shapefile_path: a file path to the shapefile
    :type shapefile_path: str

    :param title: the title of the layer
    :type title: str

    :returns: A layer
    :rtype: QGISVectorLayer

    """
    temp_shapefile = copy_temp_layer(shapefile_path, temp_dir)
    print 'temporary file: ', temp_shapefile, title
    return get_shapefile_layer(temp_shapefile, title)

