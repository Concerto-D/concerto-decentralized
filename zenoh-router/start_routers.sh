#!/usr/bin/bash
# sudo service docker start
for ((i = 0 ; i < $1 ; i++)); do
  PT=$((7447+$i))
  PR=$((8000+$i))
  sudo docker run --init -p $PT:7447/tcp -p $PR:8000/tcp -e RUST_LOG=error eclipse/zenoh &
done
sleep 5
for ((i = 0 ; i < $1 ; i++)); do
  PR=$((8000+$i))
  curl -X PUT -H 'content-type:application/properties' -d 'path_expr=/**' http://localhost:$PR/@/router/local/plugin/storages/backend/memory/storage/my-storage
done
