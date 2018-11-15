#!/usr/bin/python3
from itertools import chain
from time_deploy_par_up import test_and_print_csv

if __name__ == '__main__':
    comp_range = chain(range(1,20), range(20, 200, 10), range(200, 2000, 50), range(2000, 10001, 100))
    trans_range = [5]
    nb_samples = 5
    test_and_print_csv(comp_range, trans_range, nb_samples)
    
