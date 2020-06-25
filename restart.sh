#!/bin/bash
docker exec -it ha s6-svc -h /var/run/s6/services/home-assistant
