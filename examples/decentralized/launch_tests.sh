#!/usr/bin/bash

# Lancement concurrent des tests
timeout 60s bash -c 'python3 examples/decentralized/test_decentralized_clients.py' &
timeout 60s bash -c 'python3 examples/decentralized/test_decentralized_server.py' &
