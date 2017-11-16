#!/bin/bash
tag=$1
if [ -z $tag ]; then
    echo "No tag supplied, using 'latest'"
    tag=latest
fi

docker run \
    --name="home-assistant" \
    -d \
    --restart always \
    -v /srv/app/homeassistant:/config \
    -v /etc/localtime:/etc/localtime:ro \
    --net=host \
    homeassistant/home-assistant:$tag

    #-p 8123:8123 \
    #-p 1883:1883 \
