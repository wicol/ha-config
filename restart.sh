#!/bin/bash
docker exec -it ha s6-svc -h /var/run/s6/legacy-services/home-assistant
