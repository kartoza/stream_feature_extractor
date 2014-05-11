# -*- coding: utf-8 -*-
"""**Utilities class for extract feature from stream.**

.. tip::
   Detailed multi-paragraph description...

"""
from __future__ import division
from math import sqrt
from PyQt4.QtCore import QVariant

__author__ = 'Ismail Sunni <ismail@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '17/04/2014'
__license__ = "GPL"
__copyright__ = ''


from qgis.core import *


def list_to_str(the_list, sep=','):
    """Convert a list to str. If empty, return empty string.

    :param the_list: A list.
    :type the_list: list

    :param sep: Separator for each element in the result.
    :type sep: str

    :returns: String represent the_list.
    :rtype: str
    """
    if len(the_list) > 0:
        return sep.join([str(x) for x in the_list])
    else:
        return ''


def str_to_list(the_str, sep=',', the_type=None):
    """Convert the_str to list.

    :param the_str: String represents a list.
    :type the_str: str

    :param sep: Separator for each element in the_str.
    :type sep: str

    :param the_type: Type of the element.
    :type the_type: type

    :returns: List from the_str.
    :rtype: list
    """
    if len(the_str) == 0:
        return []
    the_list = the_str.split(sep)
    if the_type is None:
        return the_list
    else:
        try:
            return [the_type(x) for x in the_list]
        except TypeError:
            raise TypeError('%s is not valid type' % the_type)


def add_layer_attribute(layer, attribute_name, qvariant):
    """Add new attribute called attribute_name to layer.

    :param layer: A Vector layer.
    :type layer: QGISVectorLayer

    :param attribute_name: The name of the new attribute.
    :type attribute_name: str

    :param qvariant: Attribute type of the new attribute.
    :type qvariant: QVariant
    """
    id_index = layer.fieldNameIndex(attribute_name)
    if id_index == -1:
        data_provider = layer.dataProvider()
        layer.startEditing()
        data_provider.addAttributes([QgsField(attribute_name, qvariant)])
        layer.updateFields()
        layer.commitChanges()


def extract_node(layer, line_id_attribute='id'):
    """Return a list of tuple that represent line_id, first_point, last_point.

    This method will extract node from vector line layer. We only extract the
    line_id, first_point of the line, and last_point of the line.

    :param layer: A vector line layer.
    :type layer: QGISVectorLayer

    :param line_id_attribute: The name of attribute that represent line id.
    :type line_id_attribute: str

    :returns: list of tuple. The tuple contains line_id, first_point of the
        line, and last_point of the line.
    :rtype: list
    """
    nodes = []
    lines = layer.getFeatures()
    id_index = layer.fieldNameIndex(line_id_attribute)
    for feature in lines:
        geom = feature.geometry()
        points = geom.asPolyline()
        line_id = feature.attributes()[id_index]
        first_point = points[0]
        last_point = points[-1]
        nodes.append((line_id, first_point, last_point))

    return nodes


def create_nodes_layer(nodes=None, name=None):
    """Return QgsVectorLayer (point) that contains nodes.

    This method also create attribute for the layer as follow:
    id - line_id - node_type
    id : the id of the node, generated
    line_id : the id of the line. It should be existed in the nodes
    node_type : upstream (first point) or downstream (last point).

    :param nodes: A list of nodes. Represent as line_id, first_point,
        and last_point in a tuple.
    :type nodes: list, None

    :param name: The name of the layer. If None, set to Nodes.
    :type name: str

    :returns: A vector point layer that contains nodes as attributes.
    :rtype: QgsVectorLayer
    """
    if name is None:
        name = 'Nodes'
    layer = QgsVectorLayer('Point', name, 'memory')
    data_provider = layer.dataProvider()

    # Start edit layer
    layer.startEditing()

    # Add fields
    data_provider.addAttributes([
        QgsField('id', QVariant.Int),
        QgsField('line_id', QVariant.Int),
        QgsField('node_type', QVariant.String)
    ])

    # For creating node_id
    node_id = 0
    # Add features
    for node in nodes:
        line_id = node[0]
        first_point = node[1]
        last_point = node[2]

        # Add upstream node
        feature = QgsFeature()
        # noinspection PyArgumentList
        feature.setGeometry(QgsGeometry.fromPoint(first_point))
        feature.setAttributes([node_id, line_id, 'upstream'])
        data_provider.addFeatures([feature])
        node_id += 1

        # Add upstream node
        feature = QgsFeature()
        # noinspection PyArgumentList
        feature.setGeometry(QgsGeometry.fromPoint(last_point))
        feature.setAttributes([node_id, line_id, 'downstream'])
        data_provider.addFeatures([feature])
        node_id += 1
    # Commit changes
    layer.commitChanges()
    return layer


def get_nearby_nodes(layer, node_id, threshold):
    """Return all nodes that has distance less than threshold from node_id.

    The list will be divided into two groups, upstream nodes and downstream
    nodes.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer

    :param node_id: The id of a point/node.
    :type node_id: int

    :param threshold: Distance threshold.
    :type threshold: float

    :returns: Tuple of list of nodes. (upstream_nodes, downstream_nodes).
    :rtype: tuple
    """
    threshold *= threshold
    # get location of the node_id
    nodes = layer.getFeatures()
    center_node = None
    id_index = layer.fieldNameIndex('id')
    node_type_index = layer.fieldNameIndex('node_type')
    for node in nodes:
        if node.attributes()[id_index] == node_id:
            center_node = node
            break
    if center_node is None:
        raise Exception('node id is not found')

    center_node_point = center_node.geometry().asPoint()
    # iterate through all nodes
    upstream_nodes = []
    downstream_nodes = []
    nodes = layer.getFeatures()
    for node in nodes:
        node_attributes = node.attributes()
        if node_attributes[id_index] == node_id:
            continue
        node_point = node.geometry().asPoint()
        if center_node_point.sqrDist(node_point) <= threshold:
            if node_attributes[node_type_index] == 'upstream':
                upstream_nodes.append(node.attributes()[id_index])
            if node_attributes[node_type_index] == 'downstream':
                downstream_nodes.append(node.attributes()[id_index])
    return upstream_nodes, downstream_nodes


def add_associated_nodes(layer, threshold):
    """Add node_list and node_count attribute to every node in layer.

    node_list is list of node that is near from a node. There are two node
    list; upstream_node_list and downstream_node_list. There are also two
    node_count; upstream_node_count and downstream_node_count.
    node_count will have the same value as the number of the element in
    node_list. But, will be add by one according to the type of the node.


    This method will add new attributes (upstream_node_list,
    upstream_node_count, downstream_node_list, downstream_node_count) to the
    layer and populate those attributes with the right value.

    it will use get_nearby_nodes function to populate them.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer

    :param threshold: Distance threshold.
    :type threshold: float

    """
    nodes = layer.getFeatures()
    id_index = layer.fieldNameIndex('id')
    node_type_index = layer.fieldNameIndex('node_type')

    # add attributes
    data_provider = layer.dataProvider()

    add_layer_attribute(layer, 'up_nodes', QVariant.String)
    add_layer_attribute(layer, 'down_nodes', QVariant.String)
    add_layer_attribute(layer, 'up_num', QVariant.Int)
    add_layer_attribute(layer, 'down_num', QVariant.Int)

    up_nodes_index = layer.fieldNameIndex('up_nodes')
    down_nodes_index = layer.fieldNameIndex('down_nodes')
    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')

    layer.startEditing()

    for node in nodes:
        node_fid = int(node.id())
        node_attributes = node.attributes()
        node_id = node_attributes[id_index]
        node_type = node_attributes[node_type_index]
        upstream_nodes, downstream_nodes = get_nearby_nodes(
            layer, node_id, threshold)
        upstream_count = len(upstream_nodes)
        downstream_count = len(downstream_nodes)
        if node_type == 'upstream':
            upstream_count += 1
        if node_type == 'downstream':
            downstream_count += 1
        attributes = {
            up_nodes_index: list_to_str(upstream_nodes),
            down_nodes_index: list_to_str(downstream_nodes),
            up_num_index: upstream_count,
            down_num_index: downstream_count
        }
        data_provider.changeAttributeValues({node_fid: attributes})
    layer.commitChanges()


def check_associated_attributes(layer):
    """Check whether there have been associated attributes or not.

    Associated attributed : up_nodes, down_nodes, up_num, down_num

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer

    :returns: True if so, else False.
    :rtype: bool
    """
    up_nodes_index = layer.fieldNameIndex('up_nodes')
    down_nodes_index = layer.fieldNameIndex('down_nodes')
    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')

    if -1 in [up_nodes_index, down_nodes_index, up_num_index, down_num_index]:
        return False
    else:
        return True


def identify_well(layer):
    """Mark nodes from the layer if it is a well.

    A node is identified as a well if the number of upstream nodes = 0 and
    the number downstream node > 0.
    And add attribute `well` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    data_provider = layer.dataProvider()
    layer.startEditing()

    add_layer_attribute(layer, 'well', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    well_index = layer.fieldNameIndex('well')

    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num == 0 and down_num > 0:
            well_value = 1
        else:
            well_value = 0
        attributes = {well_index: well_value}
        data_provider.changeAttributeValues({node_fid: attributes})
    layer.commitChanges()


def identify_sink(layer):
    """Mark nodes from the layer if it is a sink.

    A node is identified as a sink if the number of upstream nodes > 0 and
    the number downstream node = 0.
    And add attribute `sink` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    data_provider = layer.dataProvider()
    layer.startEditing()

    add_layer_attribute(layer, 'sink', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    sink_index = layer.fieldNameIndex('sink')

    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num > 0 and down_num == 0:
            sink_value = 1
        else:
            sink_value = 0
        attributes = {sink_index: sink_value}
        data_provider.changeAttributeValues({node_fid: attributes})
    layer.commitChanges()


def identify_branch(layer):
    """Mark nodes from the layer if it is a branch.

    A node is identified as a branch if the number of upstream nodes > 0 and
    the number downstream node > 1.
    And add attribute `branch` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    data_provider = layer.dataProvider()
    layer.startEditing()

    add_layer_attribute(layer, 'branch', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    branch_index = layer.fieldNameIndex('branch')

    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num > 0 and down_num > 1:
            branch_value = 1
        else:
            branch_value = 0
        attributes = {branch_index: branch_value}
        data_provider.changeAttributeValues({node_fid: attributes})
    layer.commitChanges()


def identify_confluence(layer):
    """Mark nodes from the layer if it is a confluence.

    A node is identified as a confluence if the number of upstream nodes > 1
    and the number downstream node > 0.
    And add attribute `confluence` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    data_provider = layer.dataProvider()
    layer.startEditing()

    add_layer_attribute(layer, 'confluence', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    confluence_index = layer.fieldNameIndex('confluence')

    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num > 1 and down_num > 0:
            confluence_value = 1
        else:
            confluence_value = 0
        attributes = {confluence_index: confluence_value}
        data_provider.changeAttributeValues({node_fid: attributes})
    layer.commitChanges()


def identify_pseudo_node(layer):
    """Mark nodes from the layer if it is a pseudo_node.

    A node is identified as a pseudo_node if the number of upstream nodes == 1
    and the number downstream node == 1.
    And add attribute `pseudo_node` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    data_provider = layer.dataProvider()
    layer.startEditing()

    add_layer_attribute(layer, 'pseudo', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    pseudo_node_index = layer.fieldNameIndex('pseudo')

    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num == 1 and down_num == 1:
            pseudo_node_value = 1
        else:
            pseudo_node_value = 0
        attributes = {pseudo_node_index: pseudo_node_value}
        data_provider.changeAttributeValues({node_fid: attributes})
    layer.commitChanges()


# noinspection PyArgumentList,PyCallByClass,PyTypeChecker
def identify_self_intersection(line):
    """Return all self intersection points of a line.

    Adapted from:
    http://qgis.osgeo.org/api/qgsgeometryvalidator_8cpp_source.html#l00371

    :param line: A line to be identified.
    :type line: QgsFeature

    :returns: List of QgsPoint that represent the intersection point.
    :rtype: list
    """
    def between(a, b, c):
        """True if c is between a and b."""
        if a <= b <= c:
            return True
        if c <= b <= a:
            return True
        return False

    self_intersections = []

    geometry = line.geometry()
    vertices = geometry.asPolyline()
    if len(vertices) <= 2:
        return self_intersections

    for i in range(len(vertices) - 2):
        v = (vertices[i + 1].x() - vertices[i].x(),
             vertices[i + 1].y() - vertices[i].y())
        for j in range(i + 2, len(vertices) - 1):
            w = (vertices[j + 1].x() - vertices[j].x(),
                 vertices[j + 1].y() - vertices[j].y())
            d = v[1] * w[0] - v[0] * w[1]
            if d == 0:
                return None

            dx = vertices[j].x() - vertices[i].x()
            dy = vertices[j].y() - vertices[i].y()

            k = (dy * w[0] - dx * w[1]) / float(d)

            intersection = vertices[i][0] + v[0] * k, vertices[i][1] + v[1] * k
            if not between(
                    vertices[i][0], intersection[0], vertices[i + 1][0]):
                continue
            if not between(
                    vertices[i][1], intersection[1], vertices[i + 1][1]):
                    continue
            self_intersections.append(
                QgsPoint(intersection[0], intersection[1]))

    return self_intersections


def identify_segment_center(line):
    """Return a QgsPoint of linear segment center of the line.

    :param line: A line to be identified.
    :type line: QgsFeature

    :returns: A linear segment center
    :rtype: QgsPoint
    """
    geometry = line.geometry()
    vertices = geometry.asPolyline()

    part_length = []
    for i in range(len(vertices) - 1):
        length = vertices[i].sqrDist(vertices[i + 1])
        part_length.append(sqrt(length))

    line_length = sum(part_length)
    half_length = 0.5 * line_length

    current_length = 0
    i = 0
    add_length = 0
    while current_length <= half_length:
        add_length = part_length[i]
        current_length += add_length
        i += 1

    current_length -= add_length
    delta_length = half_length - current_length
    i -= 1

    ratio = float(delta_length) / float(add_length)

    center_x = vertices[i].x()
    center_x += ratio * (vertices[i + 1].x() - vertices[i].x())

    center_y = vertices[i].y()
    center_y += ratio * (vertices[i + 1].y() - vertices[i].y())

    return QgsPoint(center_x, center_y)


def identify_watershed(layer):
    """Mark nodes from the layer if it is a watershed.

    A node is identified as a watershed if the number of upstream nodes > 0
    and the number downstream node > 1.
    And add attribute `water_shed` for marking.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    data_provider = layer.dataProvider()
    layer.startEditing()

    add_layer_attribute(layer, 'watershed', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    watershed_index = layer.fieldNameIndex('watershed')

    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num > 0 and down_num > 1:
            watershed_value = 1
        else:
            watershed_value = 0
        attributes = {watershed_index: watershed_value}
        data_provider.changeAttributeValues({node_fid: attributes})
    layer.commitChanges()


# noinspection PyPep8Naming
def identify_features(input_layer, threshold, output_path=None):
    """Identify almost features in one functions and put it in a layer.

    :param input_layer: A vector line layer.
    :type input_layer: QGISVectorLayer

    :param threshold: Distance threshold for node snapping.
    :type threshold: float

    """
    nodes = extract_node(input_layer)
    memory_layer = create_nodes_layer(nodes)
    add_associated_nodes(memory_layer, threshold)

    identify_well(memory_layer)
    identify_sink(memory_layer)
    identify_branch(memory_layer)
    identify_confluence(memory_layer)
    identify_pseudo_node(memory_layer)
    identify_watershed(memory_layer)

    self_intersections = []
    segment_centers = []

    data_provider = input_layer.dataProvider()

    features = data_provider.getFeatures()
    for feature in features:
        self_intersections.extend(identify_self_intersection(feature))
        segment_centers.append(identify_segment_center(feature))

    # create output layer
    # if output_path is None:
    output_layer = QgsVectorLayer('Point', 'Nodes', 'memory')
    # else:
        # output_layer = QgsVectorLayer(output_path, 'Nodes', 'ogr')
    # Start edit layer
    output_data_provider = output_layer.dataProvider()
    output_layer.startEditing()
    # Add fields
    output_data_provider.addAttributes([
        QgsField('id', QVariant.Int),
        QgsField('x', QVariant.String),
        QgsField('y', QVariant.String),
        QgsField('art', QVariant.String),
    ])

    id_index = memory_layer.fieldNameIndex('id')
    upstream_index = memory_layer.fieldNameIndex('up_nodes')
    downstream_index = memory_layer.fieldNameIndex('down_nodes')
    well_index = memory_layer.fieldNameIndex('well')
    sink_index = memory_layer.fieldNameIndex('sink')
    branch_index = memory_layer.fieldNameIndex('branch')
    confluence_index = memory_layer.fieldNameIndex('pseudo')
    pseudo_node_index = memory_layer.fieldNameIndex('confluence')
    watershed_index = memory_layer.fieldNameIndex('watershed')

    feature_indexes = [
        well_index,
        sink_index,
        branch_index,
        confluence_index,
        pseudo_node_index,
        watershed_index]

    feature_names = [
        'WELL',
        'SINK',
        'BRANCH',
        'CONFLUENCE',
        'PSEUDO_NODE',
        'WATERSHED']

    memory_data_provider = memory_layer.dataProvider()
    nodes = memory_data_provider.getFeatures()

    new_node_id = 1
    expired_node_id = set()
    for node in nodes:
        # get data from memory layers
        node_attribute = node.attributes()
        node_id = node_attribute[id_index]
        if node_id in expired_node_id:
            # Continue to the next node if its nearby nodes has been already
            # computed
            continue

        # Put nearby nodes to expired nodes
        node_upstream = node_attribute[upstream_index]
        node_upstream = set(str_to_list(node_upstream))
        expired_node_id.union(node_upstream)

        node_downstream = node_attribute[downstream_index]
        node_downstream = set(str_to_list(node_downstream))
        expired_node_id.union(node_downstream)

        node_point = node.geometry().asPoint()
        x = node_point.x()
        y = node_point.y()
        for i in range(len(feature_indexes)):
            if node_attribute[feature_indexes[i]] == 1:
                new_feature = QgsFeature()
                new_feature.setGeometry(QgsGeometry.fromPoint(node_point))
                new_feature.setAttributes(
                    [new_node_id, str(x), str(y), feature_names[i]])
                output_data_provider.addFeatures([new_feature])
                output_layer.updateFields()
                new_node_id += 1

    # self intersection
    for self_intersection in self_intersections:
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPoint(self_intersection))
        x = self_intersection.x()
        y = self_intersection.y()
        new_feature.setAttributes([new_node_id, x, y, 'SELF INTERSECTION'])
        output_data_provider.addFeatures([new_feature])
        output_layer.updateFields()
        new_node_id += 1

    for segment_center in segment_centers:
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPoint(segment_center))
        x = segment_center.x()
        y = segment_center.y()
        new_feature.setAttributes([new_node_id, x, y, 'SEGMENT CENTER'])
        output_data_provider.addFeatures([new_feature])
        output_layer.updateFields()
        new_node_id += 1

    output_layer.commitChanges()
    return output_layer


