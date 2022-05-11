#!/usr/bin/bash

containers_ids=$(sudo docker ps -q)
for container_id in $(echo $containers_ids | tr " " "\n"); do
  port_string=$(sudo docker container port $container_id | grep :::80)
  port=${port_string//8000\/tcp -> :::/}
  # Récupération du PID du routeur
  router_pid=$(curl --no-progress-meter localhost:$port/@/router/local | jq -r '.[0].value.pid')
  echo "container id: $container_id"
  echo "router pid: $router_pid"               # Affiche le PID du routeur
  echo "http port: $port"                      # Affiche le port HTTP sur lequel l'API REST est accessible
  curl --no-progress-meter localhost:$port/**   # Affiche les données insérées dans le router ayant pour clé /**
  echo ""
  echo ""
done

