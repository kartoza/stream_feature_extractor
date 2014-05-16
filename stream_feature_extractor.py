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
"""

import os.path

#from pydev import pydevd  # pylint: disable=F0401

from PyQt4.QtCore import Qt, QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QProgressBar, QPushButton
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from stream_utilities import is_line_layer, identify_features
from stream_options_dialog import OptionsDialog

MENU_GROUP_LABEL = u'Stream feature extractor'
MENU_RUN_LABEL = u'Extract from current layer'


class StreamFeatureExtractor:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Enable remote debugging - should normally be commented out.
        # pydevd.settrace(
        #    'localhost', port=5678, stdoutToServer=True,
        #     stderrToServer=True)

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'StreamFeatureExtractor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.run_action = None
        self.options_action = None
        self.active_layer = None
        self.message_bar = None

        # Declare instance attributes

        self.actions = []
        self.menu = self.tr(MENU_GROUP_LABEL)
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(MENU_GROUP_LABEL)
        self.toolbar.setObjectName(u'StreamFeatureExtractor')

        # To enable/disable the menu option and setting active_layer
        self.iface.currentLayerChanged.connect(self.layer_changed)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('StreamFeatureExtractor', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str, QString

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.menu = u'Stream feature extractor'
        icon_path = ':/plugins/StreamFeatureExtractor/icon.svg'
        self.run_action = self.add_action(
            icon_path,
            text=self.tr(u"Extract from current layer",),
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_menu=True)

        self.options_action = self.add_action(
            icon_path,
            text=self.tr(u"Options ...", ),
            callback=self.show_options,
            parent=self.iface.mainWindow(),
            add_to_menu=True,
            add_to_toolbar=False)

        if self.iface.activeLayer() is not None:
            self.layer_changed(self.iface.activeLayer())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(MENU_RUN_LABEL),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work."""
        message_bar = self.iface.messageBar().createMessage(
            self.tr('Extracting stream features'),
            self.tr('Please stand by while calculation is in progress.'),
            self.iface.mainWindow())

        progress_bar = QProgressBar()
        progress_bar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cancel_button = QPushButton()
        cancel_button.setText(self.tr('Cancel'))
        #cancel_button.clicked.connect(worker.kill)
        message_bar.layout().addWidget(progress_bar)
        message_bar.layout().addWidget(cancel_button)
        self.iface.messageBar().pushWidget(
            message_bar, self.iface.messageBar().INFO)
        self.message_bar = message_bar

        def progress_callback(current, maximum):
            """GUI based callback implementation for showing progress.

            :param current: Current progress.
            :type current: int

            :param maximum: Maximum range (point at which task is complete.
            :type maximum: int
            """
            if progress_bar is not None:
                progress_bar.setMaximum(maximum)
                progress_bar.setValue(current)

        nodes = identify_features(
            self.iface.activeLayer(),
            threshold=1,
            callback=progress_callback)

        QgsMapLayerRegistry.instance().addMapLayer(nodes)

        #QgsMapLayerRegistry.instance().addMapLayers([layer])
        self.iface.messageBar().pushMessage(
            self.tr('Extraction completed.'),
            self.tr('Use "Layer->Save as" to save the results permanently.'),
            level=QgsMessageBar.INFO,
            duration=3)

    @staticmethod
    def show_options():
        """Show dialog with plugin options."""
        # show the dialog
        dialog = OptionsDialog()
        result = dialog.exec_()
        # See if OK was pressed
        if result:
            pass
        else:
            pass

    def layer_changed(self, layer):
        """Enable or disable extract features action when active layer changes.

        :param layer: The layer that is now active.
        :type layer: QgsMapLayer
        """
        flag = is_line_layer(layer)
        self.run_action.setEnabled(flag)
