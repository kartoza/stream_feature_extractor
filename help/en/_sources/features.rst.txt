.. _features-label:

Feature Definitions
===================

This document describes the logic used for determining what type (if any) of
feature each node represents.

1. Crossing or Intersection / *Kreuzung*
----------------------------------------

   If two lines cross each other (without a node).

   .. image:: /static/crossing.png
      :align: center

2. Pseudo node / *Pseudonode*
-----------------------------

   A node that has one upstream and one downstream node. The node is
   superfluous as it can be represented by one line instead of two.

   .. image:: /static/pseudo_node.png
      :align: center

3. Well or Source / *Quelle*
----------------------------

   A node that has one downstream node and zero upstream nodes.

   .. image:: /static/well.png
      :align: center

4. Sink / *Senke*
-----------------

   A node that has no downstream node and one or more upstream nodes.

   .. image:: /static/sink.png
      :align: center

5. Watershed / *Top*
--------------------

   A node that has more than one downstream node and zero upstream nodes.

   .. image:: /static/watershed.png
      :align: center

6. Unseparated / *Ungetrennter*
-------------------------------

   Only one upstream node or only one downstream node and intersects with one or more other lines.
   Note that in the lines below, there is only one node under the star, the other line has no node
   at the position of the star.

   .. image:: /static/unseparated.png
      :align: center

7. Unclear bifurcation / *Unklare Bifurkation*
----------------------------------------------

   It has more than one upstream and more than one downstream node,
   but the number of upstream and downstream nodes are same.

   .. image:: /static/unclear_bifurcation.png
      :align: center

8. Distributary or Branch / *Verzweigung*
-----------------------------------------

   It has more downstream nodes than upstream nodes. The minimum number of upstream nodes is one.

   .. image:: /static/branch.png
      :align: center

9. Confluence / *Zusammenfluss*
-------------------------------

   It has more upstream nodes than downstream nodes. The minimum number of downstream nodes is one.

   .. image:: /static/confluence.png
      :align: center

10. Segment Centre / *Segmentmitte*
-----------------------------------

   Segment centre is the linear centre of a line.
   The tool finds the point in the line that is half way along the line.

   .. image:: /static/segment_center.png
      :align: center

11. Self Intersection / *Selbstkreuzung*
----------------------------------------

    Same as intersection (crossing), but this time the line intersects with itself.

    .. image:: /static/self_intersection.png
       :align: center
