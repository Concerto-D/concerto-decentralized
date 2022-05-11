#!/usr/bin/bash
RESULT_TO_WATCH=""
for ((i = 0 ; i < $1 ; i++)); do
  PR=$((8000+$i))
  ROUTER_PID=$(curl localhost:$PR/@/router/local | jq -r '.[0].value.pid')
  RESULT_TO_WATCH="${RESULT_TO_WATCH} echo 'ROUTER_PID: $ROUTER_PID'; echo 'HTTP_PORT: $PR'; curl localhost:$PR/**;"
done

watch $RESULT_TO_WATCH