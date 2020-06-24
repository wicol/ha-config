#!/bin/bash
curl -s https://registry.hub.docker.com/v1/repositories/homeassistant/home-assistant/tags | jq -r ".[].name" | grep "[0-9]" | sort -V | grep -v dev | tail -10
