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

from PyQt4.QtCore import QVariant

from qgis.core import QGis, QgsPoint

from .extractor.utilities import (
    list_to_str,
    str_to_list,
    add_layer_attribute,
    extract_node,
    create_nodes_layer,
    get_nearby_nodes,
    add_associated_nodes,
    check_associated_attributes,
    identify_well,
    identify_sink,
    identify_branch,
    identify_confluence,
    identify_pseudo_node,
    identify_watershed
)
from test.utilities import (
    get_temp_shapefile_layer,
    get_qgis_app,
    get_random_string)

DATA_TEST_DIR = 'data_test'
sungai_di_jawa_shp = os.path.join(DATA_TEST_DIR, 'sungai_di_jawa.shp')
nodes_shp = os.path.join(DATA_TEST_DIR, 'nodes.shp')
QGIS_APP = get_qgis_app()


class TestUtilities(unittest.TestCase):
    """Class for testing utilities."""

    @classmethod
    def setUpClass(cls):
        cls.sungai_layer = get_temp_shapefile_layer(
            sungai_di_jawa_shp, 'sungai_di_jawa')
        cls.nodes_layer = get_temp_shapefile_layer(nodes_shp, 'nodes')
        cls.prepared_nodes_layer = get_temp_shapefile_layer(
            nodes_shp, 'prepared_nodes')
        add_associated_nodes(cls.prepared_nodes_layer, 0.0005)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_random_string(self):
        """test for get_random_string function."""
        length_str = 7
        random_str = get_random_string(length_str)
        message = 'Length of the string should be %s I got %s' % (
            length_str, len(random_str))
        self.assertTrue(len(random_str) == length_str, message)

        random_strings = set()
        num_string = 1000
        for i in range(num_string):
            random_strings.add(get_random_string(7))
        message = 'There should be %s unique strings' % num_string
        self.assertTrue(len(random_strings) == num_string, message)

    def test_list_to_str(self):
        """test for list to str."""
        the_list = [1, 2, 3, 3, 5]
        the_str = list_to_str(the_list)
        expected_str = '1,2,3,3,5'
        message = 'Expected %s but I got %s' % (expected_str, the_str)
        self.assertEqual(the_str, expected_str, message)

        the_str = list_to_str(the_list, sep='++')
        expected_str = '1++2++3++3++5'
        message = 'Expected %s but I got %s' % (expected_str, the_str)
        self.assertEqual(the_str, expected_str, message)

    def test_str_to_list(self):
        """test for str_to_list."""
        the_str = '1,2,3,3,5'
        the_list = str_to_list(the_str, ',', int)
        expected_list = [1, 2, 3, 3, 5]
        message = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list,message)

        the_str = ''
        the_list = str_to_list(the_str, ',', int)
        expected_list = []
        message = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list,message)

        the_str = '1.5X4.5'
        the_list = str_to_list(the_str, 'X', float)
        expected_list = [1.5, 4.5]
        message = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list,message)

        the_str = '1.5X4.5'
        message = 'Expect TypeError, but not found'
        # noinspection PyTypeChecker
        self.assertRaises(
            TypeError, lambda: str_to_list(the_str, 'X', 'integer'))

    def test_layer_add_attribute(self):
        """test add_layer_attribute."""
        layer = self.nodes_layer
        attribute_name = 'new_att'
        add_layer_attribute(layer, attribute_name, QVariant.Int)
        id_index = layer.fieldNameIndex(attribute_name)
        message = 'New attribute has not been added yet.'
        self.assertTrue(id_index > -1, message)

    def check_data_test(self):
        """Test for checking the data test."""
        layer = self.sungai_layer
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
        layer = self.sungai_layer
        nodes = extract_node(layer, 'id')
        for node in expected_nodes:
            assert node in nodes, 'Node %s not found,' % str(node)
        assert len(nodes) == len(expected_nodes), (
            'Number of nodes should be %d' % len(expected_nodes))

    def test_create_nodes_layer(self):
        """Test for creating nodes layer."""
        layer = self.sungai_layer
        nodes = extract_node(layer, 'id')
        point_layer = create_nodes_layer(nodes)
        assert point_layer.name() == 'Nodes', 'Layer names should be Nodes'
        assert point_layer.isValid(), 'Layer is not valid.'
        assert point_layer.featureCount() == 12, (
            'Feature count is not equal to 12')
        assert point_layer.geometryType() == QGis.Point, (
            'Geometry type should be %s' % QGis.Point)

        expected_nodes = [
            [0, 5, 'upstream'],
            [1, 5, 'downstream'],
            [2, 6, 'upstream'],
            [3, 6, 'downstream'],
            [4, 4, 'upstream'],
            [5, 4, 'downstream'],
            [6, 3, 'upstream'],
            [7, 3, 'downstream'],
            [8, 2, 'upstream'],
            [9, 2, 'downstream'],
            [10, 1, 'upstream'],
            [11, 1, 'downstream']
        ]

        real_nodes = point_layer.getFeatures()
        for node in real_nodes:
            node_attributes = node.attributes()
            message = 'Node %s should not be found.' % node_attributes
            self.assertIn(node_attributes, expected_nodes, message)

        # error = QgsVectorFileWriter.writeAsVectorFormat(
        #     point_layer, nodes_shp, "CP1250", None, "ESRI Shapefile")
        #
        # if error == QgsVectorFileWriter.NoError:
        #     print "success!"

    def test_get_nearby_nodes(self):
        """Test for get_nearby_nodes function."""
        nodes_layer = self.nodes_layer
        upstream_nodes, downstream_nodes = get_nearby_nodes(
            nodes_layer, 1, 0.0005)
        expected_upstream_nodes = [2]
        expected_downstream_nodes = [5]
        message = ('Expect upstream nearby nodes %s but got %s' % (
            expected_upstream_nodes, upstream_nodes))
        self.assertItemsEqual(upstream_nodes, expected_upstream_nodes, message)
        message = ('Expect downstream nearby nodes %s but got %s' % (
            expected_downstream_nodes, downstream_nodes))
        self.assertItemsEqual(downstream_nodes, expected_downstream_nodes, message)

    def test_check_associated_attributes(self):
        """Test for check_associated_attributes"""
        nodes_layer = get_temp_shapefile_layer(nodes_shp, 'nodes')
        message = 'Should be False.'
        assert not check_associated_attributes(nodes_layer), message

        add_associated_nodes(nodes_layer, 0.0005)
        message = 'Should be True.'
        assert check_associated_attributes(nodes_layer), message

    def test_add_associated_nodes(self):
        """test for add_associated_nodes"""
        nodes_layer = self.nodes_layer
        add_associated_nodes(nodes_layer, 0.0005)
        features = nodes_layer.getFeatures()
        expected_attributes = [
            [0, 5, u'upstream', None, None, 1, 0],
            [1, 5, u'downstream', u'2', u'5', 1, 2],
            [2, 6, u'upstream', None, u'1,5', 1, 2],
            [3, 6, u'downstream', None, None, 0, 1],
            [4, 4, u'upstream', u'6', u'9', 2, 1],
            [5, 4, u'downstream', u'2', u'1', 1, 2],
            [6, 3, u'upstream', u'4', u'9', 2, 1],
            [7, 3, u'downstream', None, None, 0, 1],
            [8, 2, u'upstream', None, u'11', 1, 1],
            [9, 2, u'downstream', u'4,6', None, 2, 1],
            [10, 1, u'upstream', None, None, 1, 0],
            [11, 1, u'downstream', u'8', None, 1, 1]
        ]
        i = 0
        for feature in features:
            i += 1
            message = feature.attributes()
            self.assertIn(feature.attributes(), expected_attributes, message)
        message = ('There should be %s features but I got %s.' % (
            len(expected_attributes), i))
        self.assertEqual(len(expected_attributes), i, message)

    def test_identify_well(self):
        """Test for identify_well method."""
        nodes_layer = self.prepared_nodes_layer
        identify_well(nodes_layer)
        features = nodes_layer.getFeatures()

        id_index = nodes_layer.fieldNameIndex('id')
        well_index = nodes_layer.fieldNameIndex('well')

        expected_well = [3, 7]

        for feature in features:
            node_attributes = feature.attributes()
            node_id = node_attributes[id_index]
            well_value = node_attributes[well_index]
            if node_id in expected_well:
                self.assertEqual(
                    1, well_value, 'Node %s Should be a well' % node_id)
            else:
                self.assertEqual(
                    0, well_value, 'Node %s Should not be a well' % node_id)

    def test_identify_sink(self):
        """Test for identify_sink method."""
        nodes_layer = self.prepared_nodes_layer
        identify_sink(nodes_layer)
        features = nodes_layer.getFeatures()

        id_index = nodes_layer.fieldNameIndex('id')
        sink_index = nodes_layer.fieldNameIndex('sink')

        expected_sink = [0, 10]

        for feature in features:
            node_attributes = feature.attributes()
            node_id = node_attributes[id_index]
            sink_value = node_attributes[sink_index]
            if node_id in expected_sink:
                self.assertEqual(
                    1, sink_value, 'Node %s Should be a sink' % node_id)
            else:
                self.assertEqual(
                    0, sink_value, 'Node %s Should not be a sink' % node_id)

    def test_identify_branch(self):
        """Test for identify_branch method."""
        nodes_layer = self.prepared_nodes_layer
        identify_branch(nodes_layer)
        features = nodes_layer.getFeatures()

        id_index = nodes_layer.fieldNameIndex('id')
        branch_index = nodes_layer.fieldNameIndex('branch')

        expected_branch = [1, 2, 5]

        for feature in features:
            node_attributes = feature.attributes()
            node_id = node_attributes[id_index]
            branch_value = node_attributes[branch_index]
            if node_id in expected_branch:
                self.assertEqual(
                    1, branch_value, 'Node %s Should be a branch' % node_id)
            else:
                self.assertEqual(0, branch_value,
                                 'Node %s Should not be a branch' % node_id)

    def test_identify_confluence(self):
        """Test for identify_confluence method."""
        nodes_layer = self.prepared_nodes_layer
        identify_confluence(nodes_layer)
        features = nodes_layer.getFeatures()

        id_index = nodes_layer.fieldNameIndex('id')
        confluence_index = nodes_layer.fieldNameIndex('confluence')

        expected_confluence = [4, 6, 9]

        for feature in features:
            node_attributes = feature.attributes()
            node_id = node_attributes[id_index]
            confluence_value = node_attributes[confluence_index]
            if node_id in expected_confluence:
                self.assertEqual(
                    1,
                    confluence_value,
                    'Node %s Should be a confluence' % node_id)
            else:
                self.assertEqual(
                    0,
                    confluence_value,
                    'Node %s Should not be a confluence' % node_id)

    def test_identify_pseudo_node(self):
        """Test for identify_pseudo_node method."""
        nodes_layer = self.prepared_nodes_layer
        identify_pseudo_node(nodes_layer)
        features = nodes_layer.getFeatures()

        id_index = nodes_layer.fieldNameIndex('id')
        pseudo_node_index = nodes_layer.fieldNameIndex('pseudo')

        expected_pseudo_node = [8, 11]

        for feature in features:
            node_attributes = feature.attributes()
            node_id = node_attributes[id_index]
            pseudo_node_value = node_attributes[pseudo_node_index]
            if node_id in expected_pseudo_node:
                self.assertEqual(
                    1,
                    pseudo_node_value,
                    'Node %s Should be a pseudo_node' % node_id)
            else:
                self.assertEqual(
                    0,
                    pseudo_node_value,
                    'Node %s Should not be a pseudo_node' % node_id)

    def test_identify_watershed(self):
        """Test for identify_watershed method."""
        nodes_layer = self.prepared_nodes_layer
        identify_watershed(nodes_layer)
        features = nodes_layer.getFeatures()

        id_index = nodes_layer.fieldNameIndex('id')
        watershed_index = nodes_layer.fieldNameIndex('watershed')

        expected_watershed = [1, 2, 5]

        for feature in features:
            node_attributes = feature.attributes()
            node_id = node_attributes[id_index]
            watershed_value = node_attributes[watershed_index]
            if node_id in expected_watershed:
                self.assertEqual(
                    1,
                    watershed_value,
                    'Node %s Should be a watershed' % node_id)
            else:
                self.assertEqual(
                    0,
                    watershed_value,
                    'Node %s Should not be a watershed' % node_id)

if __name__ == '__main__':
    unittest.main()


