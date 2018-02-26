#!/bin/bash
set -e
latest_tag=`./get_tags.sh | tail -1`
docker pull homeassistant/home-assistant:$latest_tag
# Graceful sotp
docker stop ha
docker rm ha
./run.sh $latest_tag
