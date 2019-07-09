# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StreamFeatureExtractor
                                 A QGIS plugin
 A tool to extract features from a stream network.
                             -------------------
        begin                : 2014-05-07
        copyright            : (C) 2014 by Linfiniti Consulting CC.
        email                : tim@linfiniti.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import

from . import custom_logging  # pylint: disable=relative-import

# Import the PyQt and QGIS libraries
# this import required to enable PyQt API v2


SENTRY_URL = (
    'http://b257c02328384628a50de20d257cf06e:'
    'ab515d8c88b746d484351321b0111b44@sentry.linfiniti.com/10')
custom_logging.setup_logger(SENTRY_URL)


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """load StreamFeatureExtractor class from file StreamFeatureExtractor."""
    # pylint: disable=relative-import
    from .stream_feature_extractor import StreamFeatureExtractor
    # pylint: enable=relative-import
    return StreamFeatureExtractor(iface)
