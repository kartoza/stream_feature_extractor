# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StreamFeatureExtractor
                                 A QGIS plugin
 A tool to extract features from a stream network.
                             -------------------
        begin                : 2014-05-07
        copyright            : (C) Kartoza (Pty) Ltd.
        email                : tim@kartoza.com
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

import os

mute_logs = os.getenv('MUTE_LOGS')

# On testing environment logs are muted, check if we are in a testing enviroment,
# if so no need of loading logs libraries
if not mute_logs:
    from . import custom_logging  # pylint: disable=relative-import

    SENTRY_URL = (
        'http://8a67c7961c844500a25d7dfd048c4da9:'
        'de927b27fe5342dbb358accd031661ad@sentry.kartoza.com/31')
    custom_logging.setup_logger(SENTRY_URL)


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """load StreamFeatureExtractor class from file StreamFeatureExtractor."""
    # pylint: disable=relative-import
    from .stream_feature_extractor import StreamFeatureExtractor
    # pylint: enable=relative-import
    return StreamFeatureExtractor(iface)
