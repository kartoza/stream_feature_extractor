# -*- coding: utf-8 -*-
"""**Utilities class for extract feature from stream.**

.. tip::
   Detailed multi-paragraph description...

"""
from __future__ import division

__author__ = 'Ismail Sunni <ismail@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '17/04/2014'
__license__ = "GPL"
__copyright__ = ''


from math import sqrt

from PyQt4.QtCore import QVariant, QCoreApplication

from qgis.core import (
    QGis,
    QgsField,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    QgsMapLayer,
    QgsRectangle,
    QgsFeatureRequest,
    QgsSpatialIndex)


def tr(message):
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    return QCoreApplication.translate('@default', message)


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


def extract_nodes(layer):
    """Return a list of tuple that represent line_id, first_point, last_point.

    This method will extract node from vector line layer. We only extract the
    line_id, first_point of the line, and last_point of the line.

    :param layer: A vector line layer.
    :type layer: QGISVectorLayer

    :returns: list of tuple. The tuple contains line_id, first_point of the
        line, and last_point of the line.
    :rtype: list
    """
    nodes = []
    lines = layer.getFeatures()
    for feature in lines:
        geom = feature.geometry()
        points = geom.asPolyline()
        if len(points) < 1:
            continue
        line_id = feature.id()
        first_point = points[0]
        last_point = points[-1]
        nodes.append((line_id, first_point, last_point))

    return nodes


def create_nodes_layer(authority_id='EPSG:4326', nodes=None, name=None):
    """Return QgsVectorLayer (point) that contains nodes.

    This method also create attribute for the layer as follow:
    id - line_id - node_type
    id : the id of the node, generated
    line_id : the id of the line. It should be existed in the nodes
    node_type : upstream (first point) or downstream (last point).

    :param authority_id: Coordinate reference system authid (as represented in
        QgsCoordinateReferenceSystem.authid() for the nodes layer that will
        be created. Defaults to 'EPSG:4326'.
    :type authority_id: str

    :param nodes: A list of nodes. Represent as line_id, first_point,
        and last_point in a tuple.
    :type nodes: list, None

    :param name: The name of the layer. If None, set to Nodes.
    :type name: str

    :returns: A vector point layer that contains nodes as attributes.
    :rtype: QgsVectorLayer
    """
    if name is None:
        name = tr('Stream features')

    layer = QgsVectorLayer(
        'Point?crs=%s&index=yes' % authority_id, name, 'memory')

    data_provider = layer.dataProvider()

    # Start edit layer
    layer.startEditing()

    # Add fields
    data_provider.addAttributes([
        QgsField('id', QVariant.Int),
        QgsField('line_id', QVariant.Int),
        QgsField('node_type', QVariant.String)
    ])

    layer.commitChanges()

    # For creating node_id
    node_id = 0
    # Add features
    features = []
    for node in nodes:
        line_id = node[0]
        first_point = node[1]
        last_point = node[2]

        # Add upstream node
        feature = QgsFeature()
        # noinspection PyArgumentList
        feature.setGeometry(QgsGeometry.fromPoint(first_point))
        feature.setAttributes([node_id, line_id, 'upstream'])
        features.append(feature)
        node_id += 1

        # Add upstream node
        feature = QgsFeature()
        # noinspection PyArgumentList
        feature.setGeometry(QgsGeometry.fromPoint(last_point))
        feature.setAttributes([node_id, line_id, 'downstream'])
        features.append(feature)
        node_id += 1

    data_provider.addFeatures(features)
    # Commit changes
    layer.commitChanges()
    return layer


def get_nearby_nodes(layer, node, threshold):
    """Return all nodes that has distance less than threshold from node_id.

    The list will be divided into two groups, upstream nodes and downstream
    nodes.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer

    :param node: The point/node.
    :type node: QgsFeature

    :param threshold: Distance threshold.
    :type threshold: float

    :returns: Tuple of list of nodes. (upstream_nodes, downstream_nodes).
    :rtype: tuple
    """
    id_index = layer.fieldNameIndex('id')
    node_attributes = node.attributes()
    node_id = node_attributes[id_index]
    id_index = layer.fieldNameIndex('id')
    node_type_index = layer.fieldNameIndex('node_type')
    center_node_point = node.geometry().asPoint()

    rectangle = QgsRectangle(
        center_node_point.x() - threshold,
        center_node_point.y() - threshold,
        center_node_point.x() + threshold,
        center_node_point.y() + threshold)

    # iterate through all nodes
    upstream_nodes = []
    downstream_nodes = []
    request = QgsFeatureRequest()
    request.setFilterRect(rectangle)
    for feature in layer.getFeatures(request):
        attributes = feature.attributes()
        if feature[id_index] == node_id:
            continue

        if attributes[node_type_index] == 'upstream':
            upstream_nodes.append(attributes[id_index])
        if attributes[node_type_index] == 'downstream':
            downstream_nodes.append(attributes[id_index])

    return upstream_nodes, downstream_nodes


def add_associated_nodes(layer, threshold, callback=None):
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

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int) and 'maximum' (int). Defaults to
        None.
    :type callback: function

    """
    nodes = layer.getFeatures()
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

    node_count = layer.featureCount()
    counter = 1

    dictionary_changes = {}
    for node in nodes:
        if callback is not None:
            if counter % 100 == 0:
                callback(current=counter, maximum=node_count)
        counter += 1
        node_fid = int(node.id())
        node_attributes = node.attributes()
        #node_id = node_attributes[id_index]
        node_type = node_attributes[node_type_index]
        upstream_nodes, downstream_nodes = get_nearby_nodes(
            layer, node, threshold)
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
        dictionary_changes[node_fid] = attributes

    data_provider.changeAttributeValues(dictionary_changes)

    if callback:
        callback(current=node_count, maximum=node_count)

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


def identify_wells(layer):
    """Mark nodes from the layer if it is a well.

    A node is identified as a well if the number of upstream nodes == 1 and
    the number downstream node 0.
    And add attribute `well` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    add_layer_attribute(layer, 'well', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    well_index = layer.fieldNameIndex('well')

    dictionary_attributes = {}
    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num == 1 and down_num == 0:
            well_value = 1
        else:
            well_value = 0
        attributes = {well_index: well_value}
        dictionary_attributes[node_fid] = attributes

    data_provider = layer.dataProvider()
    layer.startEditing()
    data_provider.changeAttributeValues(dictionary_attributes)
    layer.commitChanges()


def identify_sinks(layer):
    """Mark nodes from the layer if it is a sink.

    A node is identified as a sink if the number of upstream nodes == 0 and
    the number downstream node = 1.
    And add attribute `sink` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    add_layer_attribute(layer, 'sink', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    sink_index = layer.fieldNameIndex('sink')

    dictionary_attributes = {}
    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num == 0 and down_num == 1:
            sink_value = 1
        else:
            sink_value = 0
        attributes = {sink_index: sink_value}
        dictionary_attributes[node_fid] = attributes

    data_provider = layer.dataProvider()
    layer.startEditing()
    data_provider.changeAttributeValues(dictionary_attributes)
    layer.commitChanges()


def identify_watersheds(layer):
    """Mark nodes from the layer if it is a watershed.

    A node is identified as a watershed if the number of upstream nodes > 1 and
    the number downstream node = 0.
    And add attribute `watershed` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    add_layer_attribute(layer, 'watershed', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    watershed_index = layer.fieldNameIndex('watershed')

    dictionary_attributes = {}
    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if up_num > 1 and down_num == 0:
            watershed_value = 1
        else:
            watershed_value = 0
        attributes = {watershed_index: watershed_value}
        dictionary_attributes[node_fid] = attributes

    data_provider = layer.dataProvider()
    layer.startEditing()
    data_provider.changeAttributeValues(dictionary_attributes)
    layer.commitChanges()


def identify_unclear_bifurcations(layer):
    """Mark nodes from the layer if it is a unclear bifurcations.

    A node is identified as a unclear_bifurcations if the number of upstream
    nodes > 1 and the number downstream node > 1 and both of them must have
    the sam number.
    And add attribute `unclear_bi` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    add_layer_attribute(layer, 'unclear_bi', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    unclear_bifurcation_index = layer.fieldNameIndex('unclear_bi')

    dictionary_attributes = {}
    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if 1 < up_num == down_num > 1:
            unclear_bifurcation_value = 1
        else:
            unclear_bifurcation_value = 0
        attributes = {unclear_bifurcation_index: unclear_bifurcation_value}
        dictionary_attributes[node_fid] = attributes

    data_provider = layer.dataProvider()
    layer.startEditing()
    data_provider.changeAttributeValues(dictionary_attributes)
    layer.commitChanges()


def identify_branches(layer):
    """Mark nodes from the layer if it is a branch.

    A node is identified as a branch if 1 <= the number of upstream nodes <
    the number of downstream nodes.
    And add attribute `branch` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    add_layer_attribute(layer, 'branch', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    branch_index = layer.fieldNameIndex('branch')

    dictionary_attributes = {}
    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if 1 <= down_num < up_num:
            branch_value = 1
        else:
            branch_value = 0
        attributes = {branch_index: branch_value}
        dictionary_attributes[node_fid] = attributes

    data_provider = layer.dataProvider()
    layer.startEditing()
    data_provider.changeAttributeValues(dictionary_attributes)
    layer.commitChanges()


def identify_confluences(layer):
    """Mark nodes from the layer if it is a confluence.

    A node is identified as a confluence if 1 <= the number of downstream
    nodes < the number of upstream nodes.
    And add attribute `confluence` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    add_layer_attribute(layer, 'confluence', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    confluence_index = layer.fieldNameIndex('confluence')

    dictionary_attributes = {}
    for node in nodes:
        node_fid = node.id()
        node_attributes = node.attributes()
        up_num = node_attributes[up_num_index]
        down_num = node_attributes[down_num_index]
        if 1 <= up_num < down_num:
            confluence_value = 1
        else:
            confluence_value = 0
        attributes = {confluence_index: confluence_value}
        dictionary_attributes[node_fid] = attributes

    data_provider = layer.dataProvider()
    layer.startEditing()
    data_provider.changeAttributeValues(dictionary_attributes)
    layer.commitChanges()


def identify_pseudo_nodes(layer):
    """Mark nodes from the layer if it is a pseudo_node.

    A node is identified as a pseudo_node if the number of upstream nodes == 1
    and the number downstream node == 1.
    And add attribute `pseudo_node` for marking.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    if not check_associated_attributes(layer):
        raise Exception('You should add associated node first')

    add_layer_attribute(layer, 'pseudo', QVariant.Int)
    nodes = layer.getFeatures()

    up_num_index = layer.fieldNameIndex('up_num')
    down_num_index = layer.fieldNameIndex('down_num')
    pseudo_node_index = layer.fieldNameIndex('pseudo')

    dictionary_attributes = {}
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
        dictionary_attributes[node_fid] = attributes

    data_provider = layer.dataProvider()
    layer.startEditing()
    data_provider.changeAttributeValues(dictionary_attributes)
    layer.commitChanges()


def between(a, b, c):
    """True if c is between a and b."""
    if a < b < c:
        return True
    if c < b < a:
        return True
    return False


def point_in_line(point, line):
    """True if a point is in a line that has only two vertices."""
    x_point = point[0]
    y_point = point[1]
    x1_line = line[0][0]
    y1_line = line[0][1]
    x2_line = line[1][0]
    y2_line = line[1][1]
    return (between(x1_line, x_point, x2_line)
            and between(y1_line, y_point, y2_line))


def get_spatial_index(data_provider):
    """Create spatial index from a data provider."""
    qgs_feature = QgsFeature()
    index = QgsSpatialIndex()
    qgs_features = data_provider.getFeatures()
    while qgs_features.nextFeature(qgs_feature):
        index.insertFeature(qgs_feature)
    return index


def identify_intersections(layer):
    """Return all self intersection points of a line.

    :param layer: A vector line to be identified.
    :type layer: QgsVectorLayer

    :returns: List of QgsPoint that represent the intersection point.
    :rtype: list

    """
    intersections = []
    data_provider = layer.dataProvider()
    spatial_index = get_spatial_index(data_provider)

    feature_2 = QgsFeature()
    features = layer.getFeatures()
    for feature in features:
        geometry = feature.geometry()
        vertices = geometry.asPolyline()
        intersect_lines = spatial_index.intersects(geometry.boundingBox())
        for intersect_line in intersect_lines:
            line_id = int(intersect_line)
            data_provider.getFeatures(
                QgsFeatureRequest().setFilterFid(line_id)).nextFeature(
                    feature_2)
            geometry_2 = feature_2.geometry()
            if geometry.intersects(geometry_2):
                temp_geom = geometry.intersection(geometry_2)
                if temp_geom.type() == QGis.Point:
                    temp_list = []
                    if temp_geom.isMultipart():
                        temp_list = temp_geom.asMultiPoint()
                    else:
                        temp_list.append(temp_geom.asPoint())
                    if len(vertices) > 1:
                        if vertices[0] in temp_list:
                            temp_list.remove(vertices[0])
                        if vertices[-1] in temp_list:
                                temp_list.remove(vertices[-1])
                    intersections.extend(temp_list)
    # Note(ismailsunni): if I converted directly from list to set, there is a
    # problem. The elements in the set are not unique in qgis 2.0.
    # Yes, this is strange.
    result = []
    for intersection in intersections:
        if intersection not in result:
            result.append(intersection)
    return result


# noinspection PyArgumentList,PyCallByClass,PyTypeChecker
def identify_self_intersections(line):
    """Return all self intersection points of a line.

    Adapted from:
    http://qgis.osgeo.org/api/qgsgeometryvalidator_8cpp_source.html#l00371

    :param line: A line to be identified.
    :type line: QgsFeature

    :returns: List of QgsPoint that represent the intersection point.
    :rtype: list
    """
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
                # Continue to the next part of line
                continue

            dx = vertices[j].x() - vertices[i].x()
            dy = vertices[j].y() - vertices[i].y()

            k = (dy * w[0] - dx * w[1]) / float(d)

            intersection = vertices[i][0] + v[0] * k, vertices[i][1] + v[1] * k
            if not point_in_line(intersection, vertices[i:i + 2]):
                continue
            if not point_in_line(intersection, vertices[j:j + 2]):
                continue
            self_intersections.append(
                QgsPoint(intersection[0], intersection[1]))

    return self_intersections


def identify_segment_center(line):
    """Return a QgsPoint of linear segment center of the line.

    :param line: A line to be identified.
    :type line: QgsFeature

    :returns: A linear segment center.
    :rtype: QgsPoint
    """
    geometry = line.geometry()
    vertices = geometry.asPolyline()
    vertex_count = len(vertices)

    if vertex_count < 1:
        return None

    part_lengths = []
    for i in range(vertex_count - 1):
        length = vertices[i].sqrDist(vertices[i + 1])
        part_lengths.append(sqrt(length))

    segment_count = len(part_lengths)
    line_length = sum(part_lengths)
    half_length = 0.5 * line_length

    current_length = 0
    i = 0
    add_length = 0
    while current_length <= half_length and i < segment_count:
        add_length = part_lengths[i]
        current_length += add_length
        i += 1

    current_length -= add_length
    delta_length = half_length - current_length
    i -= 1

    if add_length > 0:
        ratio = float(delta_length) / float(add_length)

        center_x = vertices[i].x()
        center_x += ratio * (vertices[i + 1].x() - vertices[i].x())

        center_y = vertices[i].y()
        center_y += ratio * (vertices[i + 1].y() - vertices[i].y())
    else:
        try:
            center_x = vertices[i].x()
            center_y = vertices[i].y()
        except IndexError:
            return None

    return QgsPoint(center_x, center_y)


def identify_segment_centers(layer):
    """Return a list of QgsPoint of linear segment centers in layer.

    :param layer: A vector line layer to be identified.
    :type layer: QgsVectorLayer

    :returns: A list of linear segment center.
    :rtype: list
    """
    segment_centers = []
    data_provider = layer.dataProvider()
    features = data_provider.getFeatures()
    for feature in features:
        center = identify_segment_center(feature)
        if center is not None:
            segment_centers.append(center)

    return segment_centers


def identify_self_intersections_layer(layer):
    """Return all self intersection points of a vector line layer.

    :param layer: A vector line layer to be identified.
    :type layer: QgsVectorLayer

    :returns: List of QgsPoint that represent the intersection point.
    :rtype: list
    """

    self_intersections_layer = []
    data_provider = layer.dataProvider()
    features = data_provider.getFeatures()
    for feature in features:
        self_intersections = identify_self_intersections(feature)
        if self_intersections:
            self_intersections_layer.extend(self_intersections)

    return self_intersections_layer


def create_intermediate_layer(input_layer, threshold=0, callback=None):
    """Helper function to create intermediate layer.

    Intermediate layer is a temporary layer that is used for helping the tool
    to identify the nodes.

    :param input_layer: A vector line layer.
    :type input_layer: QGISVectorLayer

    :param threshold: Distance threshold for node snapping. Defaults to 1.
    :type threshold: float

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int) and 'maximum' (int). Defaults to
        None.
    :type callback: function

    :returns: Intermediate layer.
    :rtype: QgsVectorLayer
    """
    # Creating intermediate layer
    authority_id = input_layer.crs().authid()
    nodes = extract_nodes(layer=input_layer)
    nodes_layer_name = tr('Intermediate layer')
    # noinspection PyTypeChecker
    intermediate_layer = create_nodes_layer(
        authority_id=authority_id, nodes=nodes, name=nodes_layer_name)
    add_associated_nodes(intermediate_layer, threshold, callback)

    # Create a collection of function references that we will call in turn
    # Note the actually run order is non deterministic so each function
    # should be independent.
    rules = {
        tr('Finding wells...'): identify_wells,
        tr('Finding sinks...'): identify_sinks,
        tr('Finding branches...'): identify_branches,
        tr('Finding confluences...'): identify_confluences,
        tr('Finding pseudo nodes...'): identify_pseudo_nodes,
        tr('Finding watersheds...'): identify_watersheds,
        tr('Finding unclear bifurcations...'): identify_unclear_bifurcations}
    rule_count = len(rules)
    index = 1

    for message, rule in rules.iteritems():
        callback(current=index, maximum=rule_count, message=message)
        rule(intermediate_layer)
        index += 1

    return intermediate_layer


def create_new_features(
        intermediate_layer,
        self_intersections,
        intersections,
        segment_centers):
    """Create list of features ready to add to final layer.

    This function will extract node from intermediate_layer, then add points
    from self_intersections, intersections, and segment_centers to complete
    the list of features.

    :param intermediate_layer: An intermediate layer.
    :type intermediate_layer: QgsVectorLayer

    :param self_intersections: List of self_intersection points.
    :type self_intersections: list

    :param intersections: List of intersection points.
    :type intersections: list

    :param segment_centers: List of segment_center points.
    :type segment_centers: list

    :returns: List of QgsFeature
    :rtype: list
    """
    new_features = []
    id_index = intermediate_layer.fieldNameIndex('id')
    upstream_index = intermediate_layer.fieldNameIndex('up_nodes')
    downstream_index = intermediate_layer.fieldNameIndex('down_nodes')
    well_index = intermediate_layer.fieldNameIndex('well')
    sink_index = intermediate_layer.fieldNameIndex('sink')
    branch_index = intermediate_layer.fieldNameIndex('branch')
    confluence_index = intermediate_layer.fieldNameIndex('confluence')
    pseudo_node_index = intermediate_layer.fieldNameIndex('pseudo')
    watershed_index = intermediate_layer.fieldNameIndex('watershed')
    unclear_bifurcation_index = intermediate_layer.fieldNameIndex('unclear_bi')

    feature_indexes = [
        well_index,
        sink_index,
        branch_index,
        confluence_index,
        pseudo_node_index,
        watershed_index,
        unclear_bifurcation_index]

    feature_names = [
        tr('Well'),
        tr('Sink'),
        tr('Branch'),
        tr('Confluence'),
        tr('Pseudo node'),
        tr('Watershed'),
        tr('Unclear Bifurcation')]

    self_intersection_name = tr('Self Intersection')
    segment_center_name = tr('Segment Center')
    intersection_name = tr('Intersection')

    intermediate_data_provider = intermediate_layer.dataProvider()
    nodes = intermediate_data_provider.getFeatures()

    new_node_id = 1
    expired_node_id = set()
    for node in nodes:
        # get data from intermediate layers
        node_attribute = node.attributes()
        node_id = node_attribute[id_index]
        if str(node_id) in expired_node_id:
            # Continue to the next node if its nearby nodes has been already
            # computed
            continue

        # Put nearby nodes to expired nodes
        node_upstream = node_attribute[upstream_index]
        node_upstream = set(str_to_list(node_upstream))
        expired_node_id = expired_node_id.union(node_upstream)

        node_downstream = node_attribute[downstream_index]
        node_downstream = set(str_to_list(node_downstream))
        expired_node_id = expired_node_id.union(node_downstream)

        node_point = node.geometry().asPoint()
        x = node_point.x()
        y = node_point.y()
        for i in range(len(feature_indexes)):
            if node_attribute[feature_indexes[i]] == 1:
                new_feature = QgsFeature()
                new_feature.setGeometry(QgsGeometry.fromPoint(node_point))
                new_feature.setAttributes(
                    [new_node_id, x, y, feature_names[i]])
                new_features.append(new_feature)

    for self_intersection in self_intersections:
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPoint(self_intersection))
        x = self_intersection.x()
        y = self_intersection.y()
        new_feature.setAttributes(
            [new_node_id, x, y, tr(self_intersection_name)])
        new_features.append(new_feature)

    for segment_center in segment_centers:
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPoint(segment_center))
        x = segment_center.x()
        y = segment_center.y()
        new_feature.setAttributes([new_node_id, x, y, segment_center_name])
        new_features.append(new_feature)

    intersection_points = []
    for intersection in intersections:
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPoint(intersection))
        x = intersection.x()
        y = intersection.y()
        new_feature.setAttributes([new_node_id, x, y, intersection_name])
        intersection_points.append(new_feature)
    new_features.extend(intersection_points)

    return new_features


def get_duplicate_points(layer, threshold):
    """Identified duplicated points from a layer based on a threshold.

    It will return two list. The first list is unique points and the second
    one is duplicated points.

    True point will be decided from the points that have lower feature.id()

    :param layer: A vector point layer.
    :type layer: QgsVectorLayer

    :param threshold: Distance threshold for deciding whether nodes are
        converged or not.
    :type threshold: float

    :returns: List of real points and fake points
    :rtype: list
    """
    data_provider = layer.dataProvider()
    output_spatial_index = get_spatial_index(data_provider)
    duplicate_features = list()
    unique_features = []
    duplicated_features = []
    for feature in data_provider.getFeatures():
        geometry = feature.geometry()
        rectangle = QgsRectangle(
            geometry.asPoint().x() - threshold,
            geometry.asPoint().y() - threshold,
            geometry.asPoint().x() + threshold,
            geometry.asPoint().y() + threshold
        )
        duplicate_feature = output_spatial_index.intersects(rectangle)
        if len(duplicate_feature) > 1:
            duplicate_feature.sort()
            if duplicate_feature not in duplicate_features:
                duplicate_features.append(duplicate_feature)
                unique_features.append(int(duplicate_feature[0]))
                duplicated_features.extend(duplicate_feature[1:])

    return  unique_features, duplicated_features


# noinspection PyPep8Naming,PyArgumentList,PyArgumentList
def identify_features(input_layer, threshold=0, callback=None):
    """Identify all features in one functions and put it in a layer.

    This function will find node that is an unseparated or ungetrennter (
    germany). The definition of this type is a node that located in a line (
    not in the start or end of a line).

    :param input_layer: A vector line layer.
    :type input_layer: QGISVectorLayer

    :param threshold: Distance threshold for node snapping. Defaults to 1.
    :type threshold: float

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int) and 'maximum' (int). Defaults to
        None.
    :type callback: function

    :returns: A tuple of an intermediate layer that contains nodes and Map
    layer (memory layer) containing identified features.
    :rtype: tuple

    """
    intermediate_layer = create_intermediate_layer(
        input_layer, threshold, callback)
    authority_id = input_layer.crs().authid()

    index = 1
    rule_count = 4
    # Find self intersections
    message = tr('Finding self intersections...')
    callback(current=index, maximum=rule_count, message=message)
    self_intersections = identify_self_intersections_layer(input_layer)
    index += 1

    # Find segment centers
    message = tr('Finding segment centers...')
    callback(current=index, maximum=rule_count, message=message)
    segment_centers = identify_segment_centers(input_layer)
    index += 1

    # Find intersections
    message = tr('Finding intersections...')
    callback(current=index, maximum=rule_count, message=message)
    intersections = identify_intersections(input_layer)
    index += 1

    # create output layer
    layer_name = tr('Stream Features')
    field_id = 'field=id:integer'
    field_x = 'field=x:double'
    field_y = 'field=y:double'
    field_type = 'field=type:string(30)'

    uri = ('Point?crs=%s&index=yes&%s&%s&%s&%s' % (
        authority_id, field_id, field_x, field_y, field_type))

    output_layer = QgsVectorLayer(uri, layer_name, 'memory')

    # Start edit layer
    output_data_provider = output_layer.dataProvider()
    output_layer.startEditing()

    type_index = output_layer.fieldNameIndex('type')

    new_features = create_new_features(
        intermediate_layer, self_intersections, intersections, segment_centers)

    output_data_provider.addFeatures(new_features)
    output_layer.updateFields()
    output_layer.commitChanges()

    message = tr('Finding Unseparated...')
    callback(current=index, maximum=rule_count, message=message)
    # How to find unseparated
    # Basically, unseparated is an intersection point in well or sink. So,
    # we find duplicate points, and replace it with Unseparated.
    unique_features, duplicated_features = get_duplicate_points(
        output_layer, threshold)

    # Deleting duplicated features
    duplicated_features = [int(x) for x in duplicated_features]
    output_data_provider.deleteFeatures(duplicated_features)

    # Replacing them with unseparated
    dictionary_attributes = {}
    attributes = {type_index: 'Unseparated'}

    for true_feature in unique_features:
        dictionary_attributes[true_feature] = attributes
    output_data_provider.changeAttributeValues(dictionary_attributes)
    output_layer.updateFields()

    # Re write the id
    features = output_layer.getFeatures()
    dictionary_attributes = {}
    i = 1
    for feature in features:
        attributes = {0: i}
        dictionary_attributes[feature.id()] = attributes
        feature.setFeatureId(i - 1)
        i += 1
    output_data_provider.changeAttributeValues(dictionary_attributes)

    output_layer.updateFields()
    output_layer.commitChanges()

    return intermediate_layer, output_layer


def is_line_layer(layer):
    """Check if a QGIS layer is vector and its geometries are lines.

    :param layer: A vector layer.
    :type layer: QgsVectorLayer, QgsMapLayer

    :returns: True if the layer contains lines, otherwise False.
    :rtype: bool
    """
    try:
        return (layer.type() == QgsMapLayer.VectorLayer) and (
            layer.geometryType() == QGis.Line)
    except AttributeError:
        return False


def console_progress_callback(current, maximum, message=None):
    """Simple console based callback implementation for tests.

    :param current: Current progress.
    :type current: int

    :param maximum: Maximum range (point at which task is complete.
    :type maximum: int

    :param message: Optional message to display in the progress bar
    :type message: str, QString
    """
    # noinspection PyChainedComparisons
    if maximum > 1000 and current % 1000 != 0 and current != maximum:
        return
    if message is not None:
        print message
    print 'Task progress: %i of %i' % (current, maximum)
