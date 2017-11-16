#!/bin/bash
curl -s https://registry.hub.docker.com/v1/repositories/homeassistant/home-assistant/tags | grep -oP "\d+\.\d+(\.\d+)?" | sort -n | tail -10
