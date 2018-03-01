#!/bin/bash
docker exec -it ha python -m homeassistant --config /config --script check_config
