# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StreamFeatureToolDialog
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
"""

from qgis.core import *
from stream_feature_extractor_dialog_base import Ui_StreamFeatureToolDialogBase

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QMessageBox
from PyQt4 import QtGui, uic

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'stream_feature_extractor_dialog_base.ui'))
# FORM_CLASS = Ui_StreamFeatureToolDialogBase


class StreamFeatureToolDialog(QtGui.QDialog, Ui_StreamFeatureToolDialogBase):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(StreamFeatureToolDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Save reference to the QGIS interface
        self.iface = iface
        self.setupUi(self)

        # properties
        self.input_layer = None
        self.output_layer = None

    def get_vector_line_layers(self):
        """Populate combo box with loaded vector line layer."""
        # noinspection PyArgumentList
        registry = QgsMapLayerRegistry.instance()
        layers = registry.mapLayers().values()
        line_layers = []
        self.cboVectorLineLayer.clear()
        for layer in layers:
            name = layer.name()
            # check if layer is a vector polygon layer
            if (layer.type() == QgsMapLayer.VectorLayer and layer
                    .geometryType() == QGis.Line):
                line_layers.append(name)
                self.cboVectorLineLayer.addItem(name, layer)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tbFeaturesLayer_clicked(self):
        file_name = QtGui.QFileDialog.getSaveFileName(
            self,
            self.tr('Set features layer...'),
            '',
            self.tr('ESRI Shapefile (*.ogr *.shp)'))
        if file_name != '':
            self.leFeaturesLayer.setText(file_name)

    def accept(self):
        """Run the feature extraction"""
        input_layer_index = self.cboVectorLineLayer.currentIndex()
        self.input_layer = self.cboVectorLineLayer.itemData(input_layer_index)
        QMessageBox.warning(None, 'stream', self.input_layer.name())