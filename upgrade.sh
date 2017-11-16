#!/bin/bash
set -e
latest_tag=`./get_tags.sh | tail -1`
docker pull homeassistant/home-assistant:$latest_tag
docker rm -f home-assistant
./run.sh $latest_tag
