#!/usr/bin/python3

import csv, sys
import deploy_par_up


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("*** Error: missing parameters!\n")
        print("time_deploy_par_up.py <max number of user components> <max number of "
              "transitions inside user components>\n")
        sys.exit(-1)

    nb_comp = int(sys.argv[1])
    nb_trans = int(sys.argv[2])
    
    if nb_comp < 1:
        print("*** Warning: at least 1 user component is deployed by "
                "this example. 1 component will be deployed.\n")
        nb_comp = 1
    if nb_trans < 1:
        print("*** Warning: at least 1 transition is needed inside the "
                "user components. 1 transition will be deployed.\n")
        nb_trans = 1
        
    fieldnames = ['nb_comp', 'nb_trans', 'time']
    writer = csv.DictWriter(sys.stderr, fieldnames=fieldnames)

    writer.writeheader()
    
    for c in range(1, nb_comp+1):
        for t in range(1, nb_trans+1):
            time = deploy_par_up.time_test(c,t)
            writer.writerow({'nb_comp': c, 'nb_trans': t, 'time': time})
