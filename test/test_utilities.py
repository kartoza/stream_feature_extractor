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
from qgis.core import (
    QGis,
    QgsVectorLayer,
    QgsPoint,
    QgsVectorFileWriter,
    QgsGeometry,
    QgsFeature)
from PyQt4.QtCore import QVariant

from stream_utilities import (
    list_to_str,
    str_to_list,
    add_layer_attribute,
    extract_nodes,
    create_nodes_layer,
    get_nearby_nodes,
    add_associated_nodes,
    check_associated_attributes,
    identify_wells,
    identify_sinks,
    identify_branches,
    identify_confluences,
    identify_pseudo_nodes,
    identify_watersheds,
    identify_self_intersections,
    identify_segment_center,
    identify_features,
    console_progress_callback,
    identify_intersections)

from test.utilities_for_testing import get_qgis_app
QGIS_APP = get_qgis_app()

TEMP_DIR = os.path.join(
    os.path.expanduser('~'), 'temp', 'stream-feature-extractor')
DATA_TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
JAWA_SHP = os.path.join(DATA_TEST_DIR, 'sungai_di_jawa.shp')
JAWA_NODES_SHP = os.path.join(DATA_TEST_DIR, 'nodes.shp')

DGN_SHP = os.path.join(DATA_TEST_DIR, 'dgn', 'dgn_test.shp')
DGN_NODES_SHP = os.path.join(DATA_TEST_DIR, 'dgn', 'dgn_test_nodes.shp')

THRESHOLD = 0.025


def get_random_string(length=7):
    """Return random string with length=length.

    :param length: length of the produced string
    :type length: int

    :returns: random string
    :rtype: str
    """
    return hashlib.sha512(str(datetime.now())).hexdigest()[:length]


def remove_temp_layer(shapefile_path):
    """Remove temporary layer that created on this test.

    :param shapefile_path: path to shapefile
    :type shapefile_path: str
    """
    exts = ['cpg', 'dbf', 'prj', 'qpj', 'shp', 'shx']
    filename = os.path.basename(shapefile_path)
    basename, _ = os.path.splitext(filename)

    for ext in exts:
        if os.path.exists(shapefile_path[:3] + ext):
            os.remove(shapefile_path[:3] + ext)


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


# noinspection PyUnresolvedReferences,PyStatementEffect
class TestUtilities(unittest.TestCase):
    """Class for testing utilities."""

    @classmethod
    def setUpClass(cls):
        cls.sungai_layer = get_temp_shapefile_layer(
            JAWA_SHP, 'sungai_di_jawa')
        cls.dgn_layer = get_temp_shapefile_layer(
            DGN_SHP, 'dgn_test  ')

        cls.jawa_nodes_layer = get_temp_shapefile_layer(
            JAWA_NODES_SHP, 'nodes')
        cls.dgn_nodes_layer = get_temp_shapefile_layer(
            DGN_NODES_SHP, 'nodes')

        cls.prepared_nodes_layer = get_temp_shapefile_layer(
            JAWA_NODES_SHP, 'prepared_nodes')
        add_associated_nodes(cls.prepared_nodes_layer, THRESHOLD)

    @classmethod
    def tearDownClass(cls):
        remove_temp_layer(cls.jawa_nodes_layer.source())
        remove_temp_layer(cls.jawa_nodes_layer.source())
        remove_temp_layer(cls.dgn_nodes_layer.source())
        remove_temp_layer(cls.dgn_nodes_layer.source())
        remove_temp_layer(cls.prepared_nodes_layer.source())

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
        self.assertEqual(the_list, expected_list, message)

        the_str = ''
        the_list = str_to_list(the_str, ',', int)
        expected_list = []
        message = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list, message)

        the_str = '1.5X4.5'
        the_list = str_to_list(the_str, 'X', float)
        expected_list = [1.5, 4.5]
        message = 'Expected %s but I got %s' % (expected_list, the_list)
        self.assertEqual(the_list, expected_list, message)

        the_str = '1.5X4.5'
        message = 'Expect TypeError, but not found'
        # noinspection PyTypeChecker
        self.assertRaises(
            TypeError, lambda: str_to_list(the_str, 'X', 'integer'), message)

    def test_layer_add_attribute(self):
        """test add_layer_attribute."""
        layer = self.jawa_nodes_layer
        attribute_name = 'new_att'
        add_layer_attribute(layer, attribute_name, QVariant.Int)
        id_index = layer.fieldNameIndex(attribute_name)
        message = 'New attribute has not been added yet.'
        self.assertTrue(id_index > -1, message)

    def test_check_data(self):
        """Test for checking the data test."""
        layer = self.sungai_layer
        assert layer.name() == 'sungai_di_jawa', (
            'Title should be %s' % layer.name())
        assert layer.isValid(), 'Layer is not valid'
        assert layer.featureCount() == 6, 'Feature count is not equal to 6'
        assert layer.geometryType() == QGis.Line, (
            'Geometry type should be %s' % QGis.Line)

    def test_extract_nodes(self):
        """Test for extracting nodes."""
        expected_nodes = [
            (5, QgsPoint(110.23989972376222113, -7.43262727664988976),
             QgsPoint(110.25117617289369321, -7.77253167189859795)),
            (4, QgsPoint(110.24634340898020923, -7.77092075059410181),
             QgsPoint(110.47509423421867325, -7.97067499235163623)),
            (3, QgsPoint(110.47670515552316317, -7.96745314974264396),
             QgsPoint(110.52181095204906569, -8.14626541454172681)),
            (2, QgsPoint(110.46865054900068515, -7.96745314974264396),
             QgsPoint(110.69579045293465924, -7.75964430146262796)),
            (0, QgsPoint(110.73123072163357961, -7.47773307317578428),
             QgsPoint(110.69417953163015511, -7.75803338015813182)),
            (1, QgsPoint(110.69256861032566519, -7.75964430146262796),
             QgsPoint(110.97286891730800562, -7.7483678523311541)),
        ]
        layer = self.sungai_layer
        nodes = extract_nodes(layer=layer)
        for node in expected_nodes:
            assert node in nodes, 'Node %s not found,' % str(node)
        assert len(nodes) == len(expected_nodes), (
            'Number of nodes should be %d' % len(expected_nodes))

    def test_extract_nodes_dgn(self):
        """Test for extracting nodes using dgn dataset."""

        layer = self.dgn_layer
        nodes = extract_nodes(layer=layer)
        self.assertEqual(len(nodes), 4115)

    def test_create_nodes_layer(self):
        """Test for creating nodes layer."""
        layer = self.sungai_layer
        nodes = extract_nodes(layer=layer)
        point_layer = create_nodes_layer(nodes=nodes)
        assert point_layer.name() == 'Nodes', 'Layer names should be Nodes'
        assert point_layer.isValid(), 'Layer is not valid.'
        assert point_layer.featureCount() == 12, (
            'Feature count is not equal to 12')
        assert point_layer.geometryType() == QGis.Point, (
            'Geometry type should be %s' % QGis.Point)

        expected_nodes = [
            [0, 0, 'upstream'],
            [1, 0, 'downstream'],
            [2, 1, 'upstream'],
            [3, 1, 'downstream'],
            [4, 2, 'upstream'],
            [5, 2, 'downstream'],
            [6, 3, 'upstream'],
            [7, 3, 'downstream'],
            [8, 4, 'upstream'],
            [9, 4, 'downstream'],
            [10, 5, 'upstream'],
            [11, 5, 'downstream']
        ]

        real_nodes = point_layer.getFeatures()
        for node in real_nodes:
            node_attributes = node.attributes()
            message = 'Node %s should not be found.' % node_attributes
            self.assertIn(node_attributes, expected_nodes, message)

        # error = QgsVectorFileWriter.writeAsVectorFormat(
        #     point_layer, JAWA_NODES_SHP, "CP1250", None, "ESRI Shapefile")
        #
        # if error == QgsVectorFileWriter.NoError:
        #     print "success!"

    def test_get_nearby_nodes(self):
        """Test for get_nearby_nodes function."""
        nodes_layer = self.jawa_nodes_layer
        nodes = nodes_layer.getFeatures()
        node = None
        # finding node with id == 1
        for i in nodes:
            print i.attributes()
            if i['id'] == 1:
                node = i
                break
        message = 'Node with id == 1 not found.'
        self.assertIsNotNone(node, message)
        upstream_nodes, downstream_nodes = get_nearby_nodes(
            nodes_layer, node, THRESHOLD)
        expected_upstream_nodes = [2]
        expected_downstream_nodes = [5]
        message = ('Expect upstream nearby nodes %s but got %s' % (
            expected_upstream_nodes, upstream_nodes))
        self.assertItemsEqual(upstream_nodes, expected_upstream_nodes, message)
        message = ('Expect downstream nearby nodes %s but got %s' % (
            expected_downstream_nodes, downstream_nodes))
        self.assertItemsEqual(
            downstream_nodes, expected_downstream_nodes, message)

    def test_check_associated_attributes(self):
        """Test for check_associated_attributes"""
        nodes_layer = get_temp_shapefile_layer(JAWA_NODES_SHP, 'nodes')
        message = 'Should be False.'
        assert not check_associated_attributes(nodes_layer), message

        add_associated_nodes(nodes_layer, THRESHOLD)
        message = 'Should be True.'
        assert check_associated_attributes(nodes_layer), message

    def test_add_associated_nodes(self):
        """test for add_associated_nodes"""
        nodes_layer = self.jawa_nodes_layer
        add_associated_nodes(nodes_layer, THRESHOLD)
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

    def test_identify_wells(self):
        """Test for identify_well method."""
        nodes_layer = self.prepared_nodes_layer
        identify_wells(nodes_layer)
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

    def test_identify_sinks(self):
        """Test for identify_sink method."""
        nodes_layer = self.prepared_nodes_layer
        identify_sinks(nodes_layer)
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

    def test_identify_branches(self):
        """Test for identify_branch method."""
        nodes_layer = self.prepared_nodes_layer
        identify_branches(nodes_layer)
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

    def test_identify_confluences(self):
        """Test for identify_confluence method."""
        nodes_layer = self.prepared_nodes_layer
        identify_confluences(nodes_layer)
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
        identify_pseudo_nodes(nodes_layer)
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

    def test_identify_watersheds(self):
        """Test for identify_watershed method."""
        nodes_layer = self.prepared_nodes_layer
        identify_watersheds(nodes_layer)
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

    # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
    def test_identify_self_intersections(self):
        """Test for identify_self_intersections."""
        line_intersect = os.path.join(DATA_TEST_DIR, 'line_intersect.shp')
        line_intersect = get_temp_shapefile_layer(line_intersect, 'lines')

        data_provider = line_intersect.dataProvider()
        features = data_provider.getFeatures()

        expected_intersections = [
            QgsPoint(134.0448322208192, -0.8665865028884477),
            QgsPoint(134.04461808806883, -0.8669101919296638),
            QgsPoint(134.04498200744285, -0.8672037401540066)
        ]

        for feature in features:
            intersections = identify_self_intersections(feature)
            message = 'The number of intersections points should be 3.'
            self.assertEqual(len(intersections), 3, message)
            message = 'There is item not equal in %s and %s.' % (
                expected_intersections, intersections)
            self.assertListEqual(
                intersections, expected_intersections, message)

    # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
    def test_identify_segment_center(self):
        """Test for identify_segment_center."""
        points = [
            (QgsPoint(0, 0)),
            (QgsPoint(1, 0)),
            (QgsPoint(2, 0)),
        ]

        geom = QgsGeometry.fromPolyline(points)
        line = QgsFeature()
        line.setGeometry(geom)

        center = identify_segment_center(line)
        expected_center = QgsPoint(1, 0)
        message = 'Expected %s but I got %s' % (expected_center, center)
        self.assertEqual(expected_center, center, message)

        points.append(QgsPoint(5, 0))

        geom = QgsGeometry.fromPolyline(points)
        line = QgsFeature()
        line.setGeometry(geom)

        center = identify_segment_center(line)
        expected_center = QgsPoint(2.5, 0)
        message = 'Expected %s but I got %s' % (expected_center, center)
        self.assertEqual(expected_center, center, message)

    def test_identify_features_jawa(self):
        """Test for identify_features on the jawa dataset."""
        sungai_layer = get_temp_shapefile_layer(
            JAWA_SHP, 'sungai_di_jawa')
        output_layer = identify_features(sungai_layer, THRESHOLD)

        i = 0
        for f in output_layer.getFeatures():
            print f.id(), f.attributes(), f.geometry().asPoint()
            i += 1
        message = 'There should be 22 features, but I got %s' % i
        self.assertEqual(i, 22, message)

        random_basename = get_random_string()
        temp_file = os.path.join(TEMP_DIR, random_basename + '.shp')
        output_layer = identify_features(sungai_layer, THRESHOLD)

        error = QgsVectorFileWriter.writeAsVectorFormat(
            output_layer, temp_file, "CP1250", None, "ESRI Shapefile")

        if error == QgsVectorFileWriter.NoError:
            print "success!"
        message = '%s is not exist' % temp_file
        self.assertTrue(os.path.exists(temp_file), message)
        remove_temp_layer(temp_file)

    def test_identify_features_dgn(self):
        """Test for identify_features on the dgn test dataset."""
        full_start = datetime.now()
        layer = get_temp_shapefile_layer(DGN_SHP, 'dgn_lines')
        start = datetime.now()
        output_layer = identify_features(
            layer, THRESHOLD, callback=console_progress_callback)
        end = datetime.now()
        delta = end - start
        i = 0
        num_wells = 0
        num_sinks = 0
        num_branches = 0
        num_confluences = 0
        num_pseudo_nodes = 0
        num_watersheds = 0
        num_self_intersections = 0
        num_segment_center = 0
        for f in output_layer.getFeatures():
            # print f.id(), f.attributes(), f.geometry().asPoint()
            node_type = f.attributes()[3]
            if node_type == 'WELL':
                num_wells += 1
            if node_type == 'SINK':
                num_sinks += 1
            if node_type == 'BRANCH':
                num_branches += 1
            if node_type == 'CONFLUENCE':
                num_confluences += 1
            if node_type == 'PSEUDO_NODE':
                num_pseudo_nodes += 1
            if node_type == 'WATERSHED':
                num_watersheds += 1
            if node_type == 'SELF INTERSECTION':
                num_self_intersections += 1
            if node_type == 'SEGMENT CENTER':
                num_segment_center += 1
            i += 1
        print 'wells', num_wells
        print 'sinks', num_sinks
        print 'branches', num_branches
        print 'confluences', num_confluences
        print 'pseudo nodes', num_pseudo_nodes
        print 'watersheds', num_watersheds
        print 'self intersections', num_self_intersections
        print 'segment center', num_segment_center

        full_end = datetime.now()
        print 'identify_features duration', delta
        print 'full duration', full_end - full_start

        message = 'There should be 24005 features, but I got %s' % i
        self.assertEqual(i, 24005, message)

        message = ('There should be 12 self intersections / kreuzung, '
                   'but I got %s' % i)
        self.assertEqual(num_self_intersections, 12, message)

        message = 'There should be 1893 pseudo node, but I got %s' % i
        self.assertEqual(num_pseudo_nodes, 1893, message)

        message = 'There should be 847 wells / quelle, but I got %s' % i
        self.assertEqual(num_wells, 847, message)

        message = 'There should be 125 sinks / senke, but I got %s' % i
        self.assertEqual(num_sinks, 125, message)

        message = ('There should be 186 branches / verzweigung, but I got %s'
                   % i)
        self.assertEqual(num_branches, 186, message)

        message = ('There should be 867 confluences / Zusammenfluss, '
                   'but I got %s' % i)
        self.assertEqual(num_confluences, 867, message)

    def test_intersections(self):
        """Test identify_intersections."""
        line_intersect = os.path.join(DATA_TEST_DIR, 'lines.shp')
        print line_intersect
        line_layer = get_temp_shapefile_layer(line_intersect, 'lines')
        line_layer2 = get_temp_shapefile_layer(line_intersect, 'lines')

        intersections = identify_intersections(line_layer, line_layer2)
        for a in intersections:
            print a
        print len(intersections)

if __name__ == '__main__':
    unittest.main()