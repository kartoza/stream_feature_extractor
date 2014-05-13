# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StreamFeatureTool
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

import os.path

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.core import QgsMapLayerRegistry
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from stream_feature_extractor_dialog import StreamFeatureToolDialog
from utilities_stream import (
    identify_features, is_line_layer)


class StreamFeatureTool:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'StreamFeatureTool_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = StreamFeatureToolDialog(self.iface)

        # Declare instance attributes
        self.run_action = None
        self.options_action = None
        self.active_layer = None

        # For enable/disable the menu option and setting active_layer
        self.iface.currentLayerChanged.connect(self.layer_changed)

        if self.iface.activeLayer() is not None:
            self.layer_changed()

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Create action that will start plugin configuration
        self.run_action = QAction(
            QIcon(":/plugins/StreamFeatureTool/icon.svg"),
            u"Extract from current layer",
            self.iface.mainWindow())
        # connect the action to the run method
        self.run_action.triggered.connect(self.run)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.run_action)
        self.iface.addPluginToVectorMenu(
            u"&Stream Feature Extractor",
            self.run_action)

        # self.options_action = QAction(
        #     QIcon(":/plugins/StreamFeatureTool/icon.svg"),
        #     u"Options",
        #     self.iface.mainWindow())
        # # connect the action to the run method
        # self.run_action.triggered.connect(self.show_options)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu(
            u"&Stream Feature Extractor",
            self.run_action)
        self.iface.removeToolBarIcon(self.run_action)

    def run(self):
        """Run method that performs all the real work."""

        threshold = 0.025
        layer = identify_features(self.iface.activeLayer(), threshold)
        QgsMapLayerRegistry.instance().addMapLayers([layer])

    def show_options(self):
        """Show dialog with plugin options."""
        # show the dialog
        self.dlg.show()
        self.dlg.get_vector_line_layers()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def layer_changed(self, layer):
        """Enable or disable extract features action when active layer changes.

        :param layer: The layer that is now active.
        :type layer: QgsMapLayer
        """
        flag = is_line_layer(layer)
        self.run_action.setEnabled(flag)
