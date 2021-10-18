#!/usr/bin/env bash

QGIS_IMAGE_V_3_16=samtwesa/qgis-testing-environment-docker:release-3_16

IMAGES=($QGIS_IMAGE_V_3_16)


for IMAGE in "${IMAGES[@]}"
do
    echo "Running tests for $IMAGE"

    docker run -d --name qgis-testing-environment \
    -v ${PWD}:/tests_directory \
    -e WITH_PYTHON_PEP=false \
    -e ON_TRAVIS=false \
    -e MUTE_LOGS=true \
    -v /tmp/.X11-unix:/tmp/.X11-unix  \
    -e DISPLAY=:99 \
    ${IMAGE}

    sleep 10

    docker exec -t qgis-testing-environment sh -c "qgis_setup.sh stream_feature_extractor"

    # FIX default installation because the sources must be in "stream_feature_extractor" parent folder
    docker exec -t qgis-testing-environment sh -c "rm -f  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/stream_feature_extractor"
    docker exec -t qgis-testing-environment sh -c "ln -s /tests_directory/ /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/stream_feature_extractor"

    # Run the real test
    time docker exec -t qgis-testing-environment sh -c "qgis_testrunner.sh test_suite.test_package"

    docker stop qgis-testing-environment
    docker rm qgis-testing-environment

done
