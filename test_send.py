import sys

import zenoh

z = zenoh.Zenoh({})


w = z.workspace()
for i in range(10):
    print(w.get(f"test{sys.argv[1]}{i}"))

