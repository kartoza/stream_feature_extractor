# coding=utf-8
"""
Help dialog implementation.

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

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'stream_help_dialog_base.ui'))


class HelpDialog(QtGui.QDialog, FORM_CLASS):
    """Dialog for showing the results of the plugin creation process."""
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
