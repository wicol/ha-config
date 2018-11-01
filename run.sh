#!/bin/bash
tag=$1
if [ -z $tag ]; then
    echo "No tag supplied, using 'latest'"
    tag=latest
fi

docker run \
    --name="ha" \
    -d \
    --restart always \
    --device /dev/zwave \
    -v /srv/app/homeassistant:/config \
    -v /etc/localtime:/etc/localtime:ro \
    --net=host \
    homeassistant/home-assistant:$tag

# -v /srv/code/homeassistant/src:/usr/src/app \
