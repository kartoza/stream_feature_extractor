# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OptionsDialog
                                 A QGIS plugin
 options
                             -------------------
        begin                : 2014-05-16
        copyright            : (C) 2014 by Options
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
"""

import os

# Import the PyQt and QGIS libraries
# this import required to enable PyQt API v2
# do it before Qt imports
import qgis  # pylint: disable=W0611

from PyQt4 import QtGui, uic
from PyQt4.QtCore import QSettings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'stream_options_dialog_base.ui'))


class OptionsDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(OptionsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        settings = QSettings()
        self.distance.setValue(
            settings.value(
                'stream-feature-extractor/search-distance', 0, type=float)
        )
        self.show_intermediate_layer.setChecked(
            settings.value(
                'stream-feature-extractor/load-intermediate-layer',
                False,
                type=bool)
        )
        self.sentry_logging.setChecked(
            settings.value(
                'stream-feature-extractor/sentry-logging',
                False,
                type=bool)
        )

    def accept(self):
        """Event handler for when ok is pressed."""
        settings = QSettings()
        settings.setValue(
            'stream-feature-extractor/search-distance',
            self.distance.value()
        )
        settings.setValue(
            'stream-feature-extractor/load-intermediate-layer',
            self.show_intermediate_layer.isChecked()
        )
        settings.setValue(
            'stream-feature-extractor/sentry-logging',
            self.sentry_logging.isChecked()
        )
        self.close()
