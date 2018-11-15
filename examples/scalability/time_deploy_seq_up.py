#!/usr/bin/python3

import csv, sys
import deploy_seq_up


def sample_name(id : int) -> str:
    return "sample%d"%(i+1)


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("*** Error: missing parameters!\n")
        print("time_deploy_par_up.py <max number of user components> (<step> (<samples>))\n")
        sys.exit(-1)

    nb_comp = int(sys.argv[1])
    step = 1
    if len(sys.argv) >= 3:
        step = int(sys.argv[2])
    nb_samples = 1
    if len(sys.argv) >= 4:
        nb_samples = int(sys.argv[3])
    
    if nb_comp < 2:
        print("*** Warning: nb_comp too low. Set to 2.\n")
        nb_comp = 2
    
    if step < 1:
        print("*** Warning: step too low. Set to 1.\n")
        step = 1
        
    if nb_samples < 1:
        print("*** Warning: nb_samples too low. Set to 1.\n")
        nb_samples = 1
        
    fieldnames = ['nb_comp', 'average', 'nb_samples']
    for i in range(nb_samples):
        fieldnames.append(sample_name(i))
    writer = csv.DictWriter(sys.stderr, fieldnames=fieldnames)

    writer.writeheader()
    
    for c in range(2, nb_comp+1, step):
        print("%d/%d"%(c,nb_comp))
        row_dict = {
            'nb_comp': c,
            'nb_samples': nb_samples
        }
        times_sum : float = 0.0
        for i in range(nb_samples):
            time = deploy_seq_up.time_test(c)
            row_dict[sample_name(i)] = time
            times_sum += time
        row_dict['average'] = times_sum/nb_samples
        writer.writerow(row_dict)
