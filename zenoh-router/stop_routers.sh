#!/usr/bin/bash
for c in $(sudo docker ps -q); do
  sudo docker stop $c
done