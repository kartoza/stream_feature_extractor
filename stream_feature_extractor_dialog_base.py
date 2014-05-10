# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stream_feature_extractor_dialog_base.ui'
#
# Created: Sat May 10 13:11:40 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_StreamFeatureToolDialogBase(object):
    def setupUi(self, StreamFeatureToolDialogBase):
        StreamFeatureToolDialogBase.setObjectName(_fromUtf8("StreamFeatureToolDialogBase"))
        StreamFeatureToolDialogBase.resize(462, 143)
        self.gridLayout = QtGui.QGridLayout(StreamFeatureToolDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.button_box = QtGui.QDialogButtonBox(StreamFeatureToolDialogBase)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.button_box.setFont(font)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.gridLayout.addWidget(self.button_box, 5, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblFeaturesLayer = QtGui.QLabel(StreamFeatureToolDialogBase)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lblFeaturesLayer.setFont(font)
        self.lblFeaturesLayer.setObjectName(_fromUtf8("lblFeaturesLayer"))
        self.gridLayout_2.addWidget(self.lblFeaturesLayer, 1, 0, 1, 1)
        self.lblVectorLineLayer = QtGui.QLabel(StreamFeatureToolDialogBase)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lblVectorLineLayer.setFont(font)
        self.lblVectorLineLayer.setObjectName(_fromUtf8("lblVectorLineLayer"))
        self.gridLayout_2.addWidget(self.lblVectorLineLayer, 0, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tbFeaturesLayer = QtGui.QToolButton(StreamFeatureToolDialogBase)
        self.tbFeaturesLayer.setObjectName(_fromUtf8("tbFeaturesLayer"))
        self.gridLayout_3.addWidget(self.tbFeaturesLayer, 0, 1, 1, 1)
        self.leFeaturesLayer = QtGui.QLineEdit(StreamFeatureToolDialogBase)
        self.leFeaturesLayer.setObjectName(_fromUtf8("leFeaturesLayer"))
        self.gridLayout_3.addWidget(self.leFeaturesLayer, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 1, 1, 1, 1)
        self.cboVectorLineLayer = QtGui.QComboBox(StreamFeatureToolDialogBase)
        self.cboVectorLineLayer.setObjectName(_fromUtf8("cboVectorLineLayer"))
        self.gridLayout_2.addWidget(self.cboVectorLineLayer, 0, 1, 1, 1)
        self.cbLoadToQGIS = QtGui.QCheckBox(StreamFeatureToolDialogBase)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.cbLoadToQGIS.setFont(font)
        self.cbLoadToQGIS.setObjectName(_fromUtf8("cbLoadToQGIS"))
        self.gridLayout_2.addWidget(self.cbLoadToQGIS, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(StreamFeatureToolDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), StreamFeatureToolDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), StreamFeatureToolDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(StreamFeatureToolDialogBase)

    def retranslateUi(self, StreamFeatureToolDialogBase):
        StreamFeatureToolDialogBase.setWindowTitle(QtGui.QApplication.translate("StreamFeatureToolDialogBase", "Stream Feature Extractor", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFeaturesLayer.setText(QtGui.QApplication.translate("StreamFeatureToolDialogBase", "Features Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.lblVectorLineLayer.setText(QtGui.QApplication.translate("StreamFeatureToolDialogBase", "Vector Line Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.tbFeaturesLayer.setText(QtGui.QApplication.translate("StreamFeatureToolDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.cbLoadToQGIS.setText(QtGui.QApplication.translate("StreamFeatureToolDialogBase", "Load to QGIS", None, QtGui.QApplication.UnicodeUTF8))

