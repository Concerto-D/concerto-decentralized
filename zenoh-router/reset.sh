#!/usr/bin/bash

STATUS_DOCKER_SERVICE=$(sudo service docker status)
if [ "$STATUS_DOCKER_SERVICE" = " * Docker is not running" ]; then
  sudo service docker start
  sleep 5
fi

./stop_routers.sh
./start_routers.sh 1