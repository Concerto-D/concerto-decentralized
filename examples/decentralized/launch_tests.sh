#!/usr/bin/bash

# Lancement concurrent des tests
timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 1' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 2' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 3' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 4' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 5' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 6' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 7' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 8' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 9' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 10' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 11' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 12' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 13' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 14' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 15' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 16' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 17' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 18' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 19' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 20' &
#timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_clients.py 21' &
timeout 30s bash -c 'python3 examples/decentralized/test_decentralized_server.py 1' &
