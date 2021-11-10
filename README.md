# Stream feature extractor

A QGIS plugin to extract stream features (wells, sinks, confluences etc.)
from a stream network. The easiest way to install this plugin is to use
the QGIS plugin manager to install it (just search for 'stream' in the
plugin manager).


Visit our [home page](https://github.com/kartoza/stream_feature_extractor) for more details.

This plugin is Free and Open Source Software and is released under the GPL V2.
See the LICENSE file included with the plugin (and in this repository) for
more information about this license.

# Feature definitions
There are 11 types of features which can be extracted from a stream network:

1. Crossing or Intersection: If two lines cross each other (without a node)

![crossing](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/crossing.png)

2. Pseudo node: A node that has one upstream and one downstream node. The node is superfluous as it can be represented by one line instead of two.

![pseudo_node](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/pseudo_node.png)

3. Well or Source: A node that has one downstream node and zero upstream nodes.

![well](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/well.png)

4. Sink: A node that has no downstream node and one or more upstream nodes.

![sink](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/sink.png)

5. Watershed: A node that has more than one downstream node and zero upstream nodes.

![watershed](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/watershed.png)

6. Separated: Only one upstream node or only one downstream node and intersects with one or more other lines. Note that in the lines below, there is only one node under the star, the other line has no node at the position of the star.

![unseparated](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/unseparated.png)

7. Unclear bifurcation: It has more than one upstream and more than one downstream node, but the number of upstream and downstream nodes are same.

![unclear_bifurcation](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/unclear_bifurcation.png)

8. Distributary or Branch: It has more downstream nodes than upstream nodes. The minimum number of upstream nodes is one.

![branch](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/branch.png)

9. Tributary or Confluence: It has more upstream nodes than downstream nodes. The minimum number of downstream nodes is one.

![confluence](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/confluence.png)

10. Segment centre: Segment centre is the linear centre of a line. The tool finds the point in the line that is half way along the line.

![segment_center](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/segment_center.png)

11. Self Intersection: Same as intersection (crossing), but this time the line intersects with itself.

![self_intersection](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/self_intersection.png)

# Installation of the plugin
The easiest approach will be to install the plugin using the QGIS plugin manager:
1. In QGIS, go to Plugins > Manage and install plugins;
2. Select the All tab;
3. In the search bar, type 'stream feature extractor'; and
4. Select the plugin and click on the Install button.

![plugin_management](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/plugin_install.png)

# How to extract features
The plugin is user-friendly and extractions can be done as follows:
1. Load a vector line layer to QGIS;
2. Select the layer; and
3. Click on the stream feature extractor icon in the toolbar. The features will be extracted for the selected layer.

![icon](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/toolbar_icon.png)

4. (optional method) Vector > Stream feature extractor > Extract stream features from current layer.

# Available options
Possible parameters or settings for the plugin can be set. Go to Vector > Stream feature extractor > Options. The following can be set:
1. Search distance: This is the distance used to determine if nodes converged or not. Note: The distance is calculated in map units of your stream network;
2. Show intermediate node count layer: An intermediate layer which were used to extract the feature is loaded to QGIS; and
3. Enabling this will submit errors to the server for debugging.

![options](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/static/options_dialog.png)

# Testing plugin
The plugin or changes to the plugin can be tested using Github Actions (https://github.com/kartoza/stream_feature_extractor/actions).
Tests will be performed on each of the methods (e.g. feature extraction) by comparing the result to existing data in the ‘/test’ folder. The following QGIS versions are tested:
1. 3.10;
2. 3.12;
3. 3.14;
4. 3.16 LTR;
5. 3.18;
6. 3.20;
7. 3.22; and
8. latest version.

## Manual testing
Tests can manually be performed, but the action should execute automatically. Here is the steps for manual execution:
1. On the repository click on the Actions tab, and select the ‘Test’ worksflow (will execute .github/workflows/test.yml);
2. Click on the Run workflow drop-down and select the Branch you want to perform the test on;
3. Click Run workflow;

![actions](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/github_actions.png)

4. Processing might take a while, especially if the docker images needs to be pulled;
5. If processing is done, check if the one of the jobs succeeded or failed.

Failed:

![failed](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/failed.png)

Success:

![success](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/success.png)

### Failed
If the testing failed, the user needs to investigate the cause of the error. Here is a quick guide on how to do this:
1. Select the test which failed;
2. Select the job which failed (e.g. ‘test (release-3_16)’);
3. The user will be presented with the job steps. Select the job which failed (e.g. ‘Run test suite’);

![success](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/job_steps.png)

4. A list of print lines will be shown, with the error at the end; and

![error](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/error_msg.png)

5. Investigate the code to which the error relates to the method performed during that test. Having a look at the data used for the test may also be useful.

### Success
There should be no issue if the tests does not fail. The jobs will be similar to the following:

![jobs_success](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/jobs_success.png)

The plugin and any updates to the plugin should work with no issue for each of the QGIS versions in the above list.

## Adding additional QGIS versions for testing
The user may want to add more or newer versions (which were originally not included in the job list) to the job list for testing. First the qgis/qgis DockerHub needs to be checked for the tags. This can be done as follows:
1. Go to https://hub.docker.com/r/qgis/qgis/
2. Click on the Tags tab;

![qgis_repo](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/docker_qgis_repo.png)

3. The user will be presented with a page which lists all QGIS docker images with their associated tags (shown in red);
4. Copy the ‘release-version’ characters. ‘release-3_20’ for the QGIS version 3.20 in this example:

![tag](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/docker_tag.png)

Now the user can add the tag to the workflow:
1. Go to ‘.github/workflows/test.yml’;
2. Click on the edit button (highlighted in red):

![edit](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/edit_button.png)

3. Add the copied tag to the ‘qgis_version_tag’ list:

![tag_jobs](https://github.com/kartoza/stream_feature_extractor/blob/develop/help/source/examples/tag_jobs.png)

4. Save/commit the change; and
5. The testing will now be performed using the added QGIS version.

# Contributing

If you would like to contribute an enhancement, bug fix, translation etc. to
this plugin, please make a fork of the repository on Github at:

https://github.com/kartoza/stream_feature_extractor

Then make your improvements and make a Github pull request. Please follow
the existing coding conventions if you want us to include your changes.

## This plugin was implemented by:

**Kartoza (Pty) Ltd.**
https://kartoza.com/

**Tim Sutton**
tim@kartoza.com

## Under subcontract to:

**Terrestris**
http://www.terrestris.de/

## This plugin was sponsored by:

**Landesbetrieb fuer Hochwasserschutz und Wasserwirtschaft Sachsen-Anhalt,**
Otto-von-Guericke-Strasse 5,
39104
Magdeburg, Germany.
