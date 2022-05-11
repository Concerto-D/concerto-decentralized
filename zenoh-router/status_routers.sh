#!/usr/bin/bash

# On récupère le nombre de containers runnings
ND=$(sudo docker ps -q)
N=$(echo $ND | grep -o " " | wc -l)
N=$(($N+1))

# On boucle sur les ports de 8000 à 8000+$N
RESULT_TO_WATCH=""
for ((i = 0 ; i < $N ; i++)); do
  PR=$((8000+$i))
  ROUTER_PID=$(curl localhost:$PR/@/router/local | jq -r '.[0].value.pid')
  echo "ROUTER_PID: $ROUTER_PID" # Affiche le PID du routeur
  echo "HTTP_PORT: $PR"          # Affiche le port HTTP sur lequel l'API REST est accessible
  curl localhost:$PR/**          # Affiche les données insérées dans le router ayant pour clé /**
done

