# -*- coding: utf-8 -*-
"""**Utilities class for extract feature from stream.**

.. tip::
   Detailed multi-paragraph description...

"""
from PyQt4.QtCore import QVariant

__author__ = 'Ismail Sunni <ismail@linfiniti.com>'
__revision__ = '$Format:%H$'
__date__ = '17/04/2014'
__license__ = "GPL"
__copyright__ = ''


from exceptions import NotImplementedError
from qgis.core import *

def extract_node(layer, line_id_attribute='id'):
    """Return a list of tuple that represent line_id, first_point, last_point.

    This method will extract node from vector line layer. We only extract the
    line_id, first_point of the line, and last_point of the line.

    :param layer: A vector line layer.
    :type layer: QGISVectorLayer

    :param line_id_attribute: the name of attribute that represent line id
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

    return layer


def get_nearby_nodes(layer, node_id, threshold):
    """Return all nodes that has distance less than threshold from node_id.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer

    :param node_id: id of a point/node
    :type node_id: int

    :param threshold: distance threshold
    :type threshold: float

    :returns: list of node
    :rtype: list
    """
    raise NotImplementedError


def add_associated_nodes(layer):
    """Add node_list and node_count attribute to every node in layer.

    node_list is list of node that is near from a node.
    node_count is the number of node in node_list plus 1.

    This method will add new attributes (node_list and node_count) to the
    layer and populate those attributes with the right value.

    :param layer: A vector point layer.
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError


def count_upstream_nodes(layer):
    """Return the number of upstream nodes from a layer.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer

    :returns: The number of upstream nodes
    :rtype: int
    """
    raise NotImplementedError


def count_downstream_nodes(layer):
    """Return the number of downstream nodes from a layer.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer

    :returns: The number of downstream nodes
    :rtype: int
    """
    raise NotImplementedError


def identify_well(layer):
    """Mark nodes from the layer if it is a well

    A node is identified as a well if the number of upstream nodes = 0 and
    the number downstream node > 0.
    And add attribute `well` for marking.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError


def identify_sink(layer):
    """Mark nodes from the layer if it is a sink

    A node is identified as a sink if the number of upstream nodes > 0 and
    the number downstream node = 0.
    And add attribute `sink` for marking.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError


def identify_branch(layer):
    """Mark nodes from the layer if it is a branch

    A node is identified as a branch if the number of upstream nodes > 0 and
    the number downstream node > 1.
    And add attribute `branch` for marking.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError

def identify_confluence(layer):
    """Mark nodes from the layer if it is a confluence

    A node is identified as a confluence if the number of upstream nodes > 1
    and the number downstream node > 0.
    And add attribute `confluence` for marking.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError


def identify_pseudo_node(layer):
    """Mark nodes from the layer if it is a pseudo_node

    A node is identified as a pseudo_node if the number of upstream nodes == 1
    and the number downstream node == 1.
    And add attribute `pseudo_node` for marking.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError


def identify_self_intersection(layer):
    """Mark nodes from the layer if self intersection is found

    :param layer: A vector line layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError


def identify_segment_center(layer):
    """Mark nodes from the layer if segment center is found

    :param layer: A vector line layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError


def identify_watershed(layer):
    """Mark nodes from the layer if it is a watershed

    A node is identified as a watershed if the number of upstream nodes > 0
    and the number downstream node > 1.
    And add attribute `pseudo_node` for marking.

    :param layer: A vector point layer
    :type layer: QGISVectorLayer
    """
    raise NotImplementedError

def add_attribute(layer, attribute_name):
    """Add new attribute called attribute_name to layer.

    :param layer: A Vector layer
    :type layer: QGISVectorLayer

    :param attribute_name: the name of the new attribute
    :type attribute_name: str
    """
    raise NotImplementedError
