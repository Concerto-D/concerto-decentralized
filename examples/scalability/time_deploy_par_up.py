#!/usr/bin/python3

import csv, sys
import deploy_par_up


def sample_name(id : int) -> str:
    return "sample%d"%(id+1)


def test_and_print_csv(comp_range, trans_range, nb_samples):
        
    fieldnames = ['nb_comp', 'nb_trans', 'average', 'nb_samples']
    for i in range(nb_samples):
        fieldnames.append(sample_name(i))
    writer = csv.DictWriter(sys.stderr, fieldnames=fieldnames)

    writer.writeheader()
    
    for c in comp_range:
        for t in trans_range:
            print("c: %d, t: %d"%(c,t))
            row_dict = {
                'nb_comp': c,
                'nb_trans': t,
                'nb_samples': nb_samples
            }
            times_sum : float = 0.0
            for i in range(nb_samples):
                time = deploy_par_up.time_test(c,t)
                row_dict[sample_name(i)] = time
                times_sum += time
            row_dict['average'] = times_sum/nb_samples
            writer.writerow(row_dict)


if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 6:
        print("*** Error: missing parameters!\n")
        print("time_deploy_par_up.py <max number of user components> <max number of "
              "transitions inside user components> (<step nb components> (<step nb transitions> (<samples>)))\n")
        sys.exit(-1)

    nb_comp = int(sys.argv[1])
    nb_trans = int(sys.argv[2])
    step_comp = 1
    if len(sys.argv) >= 4:
        step_comp = int(sys.argv[3])
    step_trans = 1
    if len(sys.argv) >= 5:
        step_trans = int(sys.argv[4])
    nb_samples = 1
    if len(sys.argv) >= 6:
        nb_samples = int(sys.argv[5])
    
    if nb_comp < 1:
        print("*** Warning: at least 1 user component is deployed by "
                "this example. 1 component will be deployed.\n")
        nb_comp = 1
    if nb_trans < 1:
        print("*** Warning: at least 1 transition is needed inside the "
                "user components. 1 transition will be deployed.\n")
        nb_trans = 1
    
    test_and_print_csv(range(1, nb_comp+1, step_comp), range(1, nb_trans+1, step_trans), nb_samples)
