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


# noinspection PyPep8Naming
def classFactory(iface):
    """load StreamFeatureExtractor class from file StreamFeatureExtractor."""
    from stream_feature_extractor import StreamFeatureExtractor
    return StreamFeatureExtractor(iface)
