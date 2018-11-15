#!/usr/bin/python3

import csv, sys
import deploy_seq_up


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("*** Error: missing parameters!\n")
        print("time_deploy_par_up.py <max number of user components> <step>\n")
        sys.exit(-1)

    nb_comp = int(sys.argv[1])
    step = 1
    if len(sys.argv) >= 3:
        step = int(sys.argv[2])
    
    if nb_comp < 2:
        print("*** Warning: at least 2 components are deployed by this "
        "example. 2 components will be deployed.\n")
        nb_comp = 2
        
    fieldnames = ['nb_comp', 'time']
    writer = csv.DictWriter(sys.stderr, fieldnames=fieldnames)

    writer.writeheader()
    
    for c in range(2, nb_comp+1, step):
        time = deploy_seq_up.time_test(c)
        writer.writerow({'nb_comp': c, 'time': time})
