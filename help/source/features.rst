.. _node_documentation:

Feature Definitions
===================

This document describes the logic used for determining what type (if any) of
feature each node represents.

1. Crossing / *Kreuzung*
------------------------

   When two lines cross each other.

   .. image:: /_static/crossing.png
      :align: center

2. Pseudo node / *Pseudonode*
-----------------------------

   A node that has one upstream and one downstream node. The node is
   superflous as it can be represented by one line instead of two.

   .. image:: /_static/pseudo_node.png
      :align: center

3. Well / *Quelle*
------------------

   A node that has 1 upstream node and 0 downstream nodes.

   .. image:: /_static/well.png
      :align: center

4. Sink / *Senke*
-----------------

   A node that has no upstream node and 1 or more downstream nodes.

   .. image:: /_static/sink.png
      :align: center

5. Watershed / *Top*
--------------------

   A node that has more than one upstream node and 0 downstream nodes.

   .. image:: /_static/watershed.png
      :align: center

6. Unseparated / *Ungetrennter*
-------------------------------

   Only 1 upstream node or only 1 downstream node and intersects with
   one or more other lines. Note that in the lines below, there is only one
   node under the star, the other line has no node at the position of the
   star.

   .. image:: /_static/unseparated.png
      :align: center

7. Unclear bifurcation / *Unklare Bifurkation*
---------------------------------------------

   It has more than one upstream and more than one downstream node,
   but the number of upstream and downstream nodes are same.

   .. image:: /_static/unclear_bifurcation.png
      :align: center

8. Tributary, Branch / *Verzweigung*
------------------------------------

   It has more upstream nodes than downstream nodes. The minimum number of
   downstream nodes is one.

   .. image:: /_static/branch.png
      :align: center

9. Confluence / *Zusammenfluss*
-------------------------------

   It has more downstream nodes than upstream nodes. The minimum number of
   upstream nodes is one.

   .. image:: /_static/confluence.png
      :align: center

10. Segment Center / *Segmentmitte*
-----------------------------------

   Segment center is the linear center of a line. The tool finds the point
   in the line that has distance half of the length of the line.

   .. image:: /_static/segment_center.png
      :align: center

11. Self Intersection / *Selbstkreuzung*
--------------------------------------

    Same with intersection, but this time the line intersects with itself.

    .. image:: /_static/self_intersection.png
       :align: center
