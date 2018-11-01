#!/bin/bash
set -e
latest_tag=`./get_tags.sh | tail -1`
docker pull homeassistant/home-assistant:$latest_tag
# Graceful stop
docker stop ha
docker rm ha
./run.sh $latest_tag
