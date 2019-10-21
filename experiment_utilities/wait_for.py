import time
import socket


def wait_for_port(port, host='localhost', sleep=1., timeout=300):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as e:
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Timeout (%f s) waiting for port %d on host %s.'%(timeout,port,host)) from e
            time.sleep(sleep)
