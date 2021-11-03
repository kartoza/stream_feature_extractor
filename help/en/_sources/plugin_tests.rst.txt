.. _plugin_tests-label:

Testing the plugin
==================

The plugin or changes to the plugin can be tested using Github Actions (https://github.com/kartoza/stream_feature_extractor/actions).
Tests will be performed on each of the methods (e.g. feature extraction) by comparing the result to existing
data in the '/test' folder. The following QGIS versions are tested:

    1. 3.10;
    2. 3.12;
    3. 3.14;
    4. 3.16 LTR;
    5. 3.18;
    6. 3.20;
    7. 3.22; and
    8. latest version.

Manual testing
--------------
Tests can manually be performed, but the action should execute automatically. Here is the steps for manual
execution:

1. On the repository click on the Actions tab, and select the 'Test' worksflow (will execute .github/workflows/test.yml);
2. Click on the Run workflow drop-down and select the Branch you want to perform the test on;
3. Click Run workflow;

   .. image:: /examples/github_actions.png
      :align: center

4. Processing might take a while, especially if the docker images needs to be pulled;
5. If processing is done, check if the one of the jobs succeeded or failed.

Failed:

   .. image:: /examples/failed.png
      :align: center

Success:

   .. image:: /examples/success.png
      :align: center

Failed
------
If the testing failed, the user needs to investigate the cause of the error. Here is a quick guide on how
to do this:

1. Select the test which failed;
2. Select the job which failed (e.g. 'test (release-3_16)');
3. The user will be presented with the job steps. Select the job which failed (e.g. 'Run test suite');

   .. image:: /examples/job_steps.png
      :align: center

4. A list of print lines will be shown, with the error at the end;

   .. image:: /examples/error_msg.png
      :align: center

5. Investigate the code to which the error relates to the method performed during that test. Having a look at the
data used for the test may also be useful.

Success
-------
There should be no issue if the tests does not fail. The jobs will be similar to the following:

   .. image:: /examples/jobs_success.png
      :align: center

The plugin and any updates to the plugin should work with no issue for each of the QGIS versions in the above list.

Adding additional QGIS versions for testing
-------------------------------------------
The user may want to add more or newer versions (which were originally not included in the job list)
to the job list for testing. First the qgis/qgis DockerHub needs to be checked for the tags. This can be done as follows:

1. Go to https://hub.docker.com/r/qgis/qgis/
2. Click on the Tags tab;

   .. image:: /examples/docker_qgis_repo.png
      :align: center

3. The user will be presented with a page which lists all QGIS docker images with their associated tags (shown in red);
4. Copy the 'release-version' characters. 'release-3_20' for the QGIS version 3.20 in this example:

   .. image:: /examples/docker_tag.png
      :align: center

Now the user can add the tag to the workflow:

1. Go to '.github/workflows/test.yml';
2. Click on the edit button (highlighted in red):

   .. image:: /examples/edit_button.png
      :align: center

3. Add the copied tag to the 'qgis_version_tag' list:

   .. image:: /examples/tag_jobs.png
      :align: center

4. Save/commit the change;
5. The testing will now be performed using the added QGIS version.
