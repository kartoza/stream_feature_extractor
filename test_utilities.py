# -*- coding: utf-8 -*-
"""**Test for utilities class for extract feature from stream.**

.. tip::
   Detailed multi-paragraph description...

"""

__author__ = 'Ismail Sunni <ismail@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '17/04/2014'
__license__ = "GPL"
__copyright__ = ''

import os
import unittest
from qgis.core import *

from utitilities import (
    extract_node,
    create_nodes_layer
)

DATA_TEST_DIR = 'data_test'
sungai_di_jawa_shp = os.path.join(DATA_TEST_DIR, 'sungai_di_jawa.shp')


def get_shapefile_layer(shapefile_path):
    """Return a layer of shapefile from shapefile_path.

    :param shapefile_path: a file path to the shapefile
    :type shapefile_path: str

    :returns: A layer
    :rtype: QGISVectorLayer
    """
    layer = QgsVectorLayer(shapefile_path, 'sungai_di_jawa', 'ogr')
    return layer


class TestUtilities(unittest.TestCase):
    """Class for testing utilities."""

    @classmethod
    def setUpClass(cls):
        # noinspection PyCallByClass,PyTypeChecker
        QgsApplication.setPrefixPath('/usr', True)
        # noinspection PyArgumentList
        QgsApplication.initQgis()
        cls.layer = get_shapefile_layer(sungai_di_jawa_shp)

    @classmethod
    def tearDownClass(cls):
        # noinspection PyArgumentList
        QgsApplication.exitQgis()

    def check_data_test(self):
        """Test for checking the data test."""
        layer = self.layer
        assert layer.name() == 'sungai_di_jawa', (
            'Title should be %s' % layer.name())
        assert layer.isValid(), 'Layer is not valid'
        assert layer.featureCount() == 6, 'Feature count is not equal to 6'
        assert layer.geometryType() == QGis.Line, (
            'Geometry type should be %s' % QGis.Line)

    def test_extract_node(self):
        """Test for extracting nodes."""
        expected_nodes = [
            (1, QgsPoint(110.23989972376222113, -7.43262727664988976),
             QgsPoint(110.25117617289369321, -7.77253167189859795)),
            (2, QgsPoint(110.24634340898020923, -7.77092075059410181),
             QgsPoint(110.47509423421867325, -7.97067499235163623)),
            (3, QgsPoint(110.47670515552316317, -7.96745314974264396),
             QgsPoint(110.52181095204906569, -8.14626541454172681)),
            (4, QgsPoint(110.46865054900068515, -7.96745314974264396),
             QgsPoint(110.69579045293465924, -7.75964430146262796)),
            (5, QgsPoint(110.73123072163357961, -7.47773307317578428),
             QgsPoint(110.69417953163015511, -7.75803338015813182)),
            (6, QgsPoint(110.69256861032566519, -7.75964430146262796),
             QgsPoint(110.97286891730800562, -7.7483678523311541)),
        ]
        print expected_nodes[0][1].sqrDist(expected_nodes[0][1])
        print expected_nodes[0][1].sqrDist(expected_nodes[0][2])
        layer = self.layer
        nodes = extract_node(layer, 'id')
        for node in expected_nodes:
            assert node in nodes, 'Node %s not found,' % str(node)
        assert len(nodes) == len(expected_nodes), (
            'Number of nodes should be %d' % len(expected_nodes))

    def test_create_nodes_layer(self):
        """Test for creating nodes layer"""
        layer = self.layer
        nodes = extract_node(layer, 'id')
        point_layer = create_nodes_layer(nodes)
        assert point_layer.name() == 'Nodes', 'Layer names should be Nodes'
        assert point_layer.isValid(), 'Layer is not valid.'
        assert point_layer.featureCount() == 12, (
            'Feature count is not equal to 12')
        assert point_layer.geometryType() == QGis.Point, (
            'Geometry type should be %s' % QGis.Point)


if __name__ == '__main__':
    unittest.main()


