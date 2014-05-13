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

import os

from PyQt4.QtCore import pyqtSignature, QVariant
from PyQt4.QtGui import QMessageBox
from PyQt4 import QtGui, uic

from qgis.core import (
    QGis,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsMapLayerRegistry,
    QgsMapLayer)

from utilities import (
    identify_features,
    add_layer_attribute)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
     os.path.dirname(__file__), 'stream_feature_extractor_dialog_base.ui'))


class StreamFeatureToolDialog(QtGui.QDialog, FORM_CLASS):
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
        self.leThreshold.setText('0.025')

        # properties
        self.input_layer = None
        self.output_path = None
        self.load_layer = False
        self.threshold = float(self.leThreshold.text())

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

    def get_ingredients(self):
        """Update all properties for extracting nodes."""
        # Input layer
        input_layer_index = self.cboVectorLineLayer.currentIndex()
        self.input_layer = self.cboVectorLineLayer.itemData(input_layer_index)
        # Output path
        self.output_path = self.leFeaturesLayer.text()
        if self.output_path == '':
            self.output_path = None
        # Threshold
        self.threshold = float(self.leThreshold.text())
        # Load to QGIS
        self.load_layer = self.cbLoadToQGIS.isChecked()

    def extract(self):
        """The main feature extraction process."""
        output_layer = identify_features(
            self.input_layer, self.threshold, self.output_path)

        for f in output_layer.getFeatures():
            print f.id(), f.attributes(), f.geometry().asPoint()

        error = QgsVectorFileWriter.writeAsVectorFormat(
                output_layer,
                self.output_path,
                'CP1250',
                None,
                'ESRI Shapefile')

        if error == QgsVectorFileWriter.NoError:
            print "success!"

        QMessageBox.warning(None, 'stream', output_layer.name())

    def put_in_layer(self, memory_layer):
        """Put points from memory layer to final layer.

        :param memory_layer: A layer that contains nodes and the identifying
        results.
        :type memory_layer: QgsVectorLayer

        :returns: A layer that contains nodes and the types
        :rtype: QgsVectorLayer
        """
        layer = QgsVectorLayer(self.output_path, 'nodes', 'ogr')
        add_layer_attribute(layer, 'ID', QVariant.Int)
        add_layer_attribute(layer, 'X', QVariant.LongLong)
        add_layer_attribute(layer, 'Y', QVariant.LongLong)
        add_layer_attribute(layer, 'ART', QVariant.String)

        data_provider = memory_layer.dataProvider()



    @pyqtSignature('')  # prevents actions being handled twice
    def accept(self):
        """Run the feature extraction"""
        self.get_ingredients()
        print self.output_path, self.threshold, self.input_layer.source()
        self.extract()
        # msg = ('%s \n %s \n %s \n %s' % (
        #     self.input_layer, self.output_path, self.threshold,
        #     self.load_layer))
        # QMessageBox.warning(None, 'stream', msg)
