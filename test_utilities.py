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
import hashlib
from datetime import datetime
from shutil import copy2
import unittest
from qgis.core import *
from PyQt4.QtCore import QVariant

from utitilities import (
    list_to_str,
    str_to_list,
    add_layer_attribute,
    extract_node,
    create_nodes_layer,
    get_nearby_nodes,
    add_associated_nodes
)

TEMP_DIR = '~/temp'
DATA_TEST_DIR = 'data_test'
sungai_di_jawa_shp = os.path.join(DATA_TEST_DIR, 'sungai_di_jawa.shp')
nodes_shp = os.path.join(DATA_TEST_DIR, 'nodes.shp')


def get_random_string(length=7):
    """Return random string with length=length.

    :param length: length of the produced string
    :type length: int

    :returns: random string
    :rtype: str
    """
    return hashlib.sha512(str(datetime.now())).hexdigest()[:length]


def copy_temp_layer(shapefile_path, temp_dir=TEMP_DIR):
    """Copy shapefile_path to temp directory and weird name.

    :param shapefile_path: a path to shapefile
    :type shapefile_path: str

    :param temp_dir: temporary directory for saving the temporary shapefile
    :type temp_dir: str

    :returns: path to temporary shapefile
    :rtype: str
    """
    # Avoid error
    if not os.path.exists(shapefile_path):
        raise OSError('Failed to copy.')

    current_date = datetime.now().strftime('%Y%m%d')
    temp_dir = os.path.join(temp_dir, current_date)

    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
        except OSError:
            raise OSError('Failed to create dirs %s.' % temp_dir)

    exts = ['cpg', 'dbf', 'prj', 'qpj', 'shp', 'shx']
    filename = os.path.basename(shapefile_path)
    basename, ext = os.path.splitext(filename)
    parent_dir = os.path.dirname(shapefile_path)

    random_basename = get_random_string()
    for ext in exts:
        real_file = os.path.join(parent_dir, basename + '.' + ext)
        if not os.path.exists(real_file):
            continue
        # copy file
        temp_file = os.path.join(temp_dir, random_basename + '.' + ext)
        copy2(real_file, temp_file)

    # Checking
    temp_shapefile = os.path.join(temp_dir, random_basename + '.shp')
    if os.path.exists(temp_shapefile):
        return temp_shapefile
    else:
        raise OSError('Failed to copy.')


def get_shapefile_layer(shapefile_path, title):
    """Return a layer of shapefile from shapefile_path.

    :param shapefile_path: a file path to the shapefile
    :type shapefile_path: str

    :param title: the title of the layer
    :type title: str

    :param temp_dir: temporary directory for saving the temporary shapefile
    :type temp_dir: str

    :returns: A layer
    :rtype: QGISVectorLayer
    """
    layer = QgsVectorLayer(shapefile_path, title, 'ogr')
    return layer


def get_temp_shapefile_layer(shapefile_path, title, temp_dir=TEMP_DIR):
    """Return a copy of layer of shapefile from shapefile_path.

    :param shapefile_path: a file path to the shapefile
    :type shapefile_path: str

    :param title: the title of the layer
    :type title: str

    :returns: A layer
    :rtype: QGISVectorLayer

    """
    temp_shapefile = copy_temp_layer(shapefile_path, temp_dir)
    return get_shapefile_layer(temp_shapefile, title)


class TestUtilities(unittest.TestCase):
    """Class for testing utilities."""

    @classmethod
    def setUpClass(cls):
        # noinspection PyCallByClass,PyTypeChecker
        QgsApplication.setPrefixPath('/usr', True)
        # noinspection PyArgumentList
        QgsApplication.initQgis()
        cls.sungai_layer = get_temp_shapefile_layer(
            sungai_di_jawa_shp, 'sungai_di_jawa')
        cls.nodes_layer = get_temp_shapefile_layer(nodes_shp, 'nodes')

    @classmethod
    def tearDownClass(cls):
        # noinspection PyArgumentList
        QgsApplication.exitQgis()

    def test_random_string(self):
        """test for get_random_string function."""
        length_str = 7
        random_str = get_random_string(length_str)
        msg = 'Length of the string should be %s I got %s' % (
            length_str, len(random_str))
        self.assertTrue(len(random_str) == length_str, msg)

        random_strings = set()
        num_string = 1000
        for i in range(num_string):
            random_strings.add(get_random_string(7))
        msg = 'There should be %s unique strings' % num_string
        self.assertTrue(len(random_strings) == num_string, msg)

    def test_list_to_str(self):
        """test for list to str."""
        the_list = [1, 2, 3, 3, 5]
        the_str = list_to_str(the_list)
        expected_str = '1,2,3,3,5'
        msg = 'Expected %s but I got %s' % (expected_str, the_str)
        self.assertEqual(the_str, expected_str, msg)

        the_str = list_to_str(the_list, sep='++')
        expected_str = '1++2++3++3++5'
        msg = 'Expected %s but I got %s' % (expected_str, the_str)
        self.assertEqual(the_str, expected_str, msg)

    def test_str_to_list(self):
        """test for str_to_list."""
        the_str = '1,2,3,3,5'
        the_list = str_to_list(the_str, ',', int)
        expected_list = [1, 2, 3, 3, 5]
        msg = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list,msg)

        the_str = ''
        the_list = str_to_list(the_str, ',', int)
        expected_list = []
        msg = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list,msg)

        the_str = '1.5X4.5'
        the_list = str_to_list(the_str, 'X', float)
        expected_list = [1.5, 4.5]
        msg = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list,msg)

        the_str = '1.5X4.5'
        msg = 'Expect TypeError, but not found'
        # noinspection PyTypeChecker
        self.assertRaises(
            TypeError, lambda: str_to_list(the_str, 'X', 'integer'))

    def test_layer_add_attribute(self):
        """test add_layer_attribute."""
        layer = self.nodes_layer
        att_name = 'new_att'
        add_layer_attribute(layer, att_name, QVariant.Int)
        id_index = layer.fieldNameIndex(att_name)
        msg = 'New attribute has not been added yet.'
        self.assertTrue(id_index > -1, msg)

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
            msg = 'Node %s should not be found.' % node_attributes
            self.assertIn(node_attributes, expected_nodes, msg)

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
        msg = ('Expect upstream nearby nodes %s but got %s' % (
            expected_upstream_nodes, upstream_nodes))
        self.assertItemsEqual(upstream_nodes, expected_upstream_nodes, msg)
        msg = ('Expect downstream nearby nodes %s but got %s' % (
            expected_downstream_nodes, downstream_nodes))
        self.assertItemsEqual(downstream_nodes, expected_downstream_nodes, msg)

    @unittest.skip('Not yet finished')
    def test_add_associated_nodes(self):
        """test for add_associated_nodes"""
        nodes_layer = self.nodes_layer
        add_associated_nodes(nodes_layer, 0.0005)
        # a = nodes_layer.getFeatures()
        # for b in a:
        #     print b.attributes()


if __name__ == '__main__':
    unittest.main()


