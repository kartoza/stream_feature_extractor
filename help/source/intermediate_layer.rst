.. _intermediate_layer:

Intermediate Layer
==================

Intermediate layer is a temporary layer that is used for helping the tool to
identify the nodes. You can show it when you run the tool by check the option
in options dialog.

If you open the attribute table of this intermediate layer,
you will find something like this:

   .. image:: /static/intermediate_layer.png
      :align: center
      :scale: 70 %

How to obtain this intermediate layer:

1. For each line in input layer, the tool will retrieve the first and the last
   vertex. The first one will be assigned as upstream node,
   and the last one will be assigned as downstream node for *node_type*. We
   also add the *line_id* as the attribute of the nodes.

2. The tool will find the nearby nodes for each nodes according to their type
   and add their id on the attributes (*up_nodes* and *down_nodes*).

3. The tool add another attributes, up_num and down_num. Basically,
   they represent the number of nearby upstream nodes and downstream nodes
   respectively. We will add 1 to *up_num* if the node is upstream_node,
   this applies for *down_num*.

4. The tool will populate each node type based on the rules in :doc:`features`.
