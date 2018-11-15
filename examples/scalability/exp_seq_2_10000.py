#!/usr/bin/python3
from itertools import chain
from time_deploy_seq_up import test_and_print_csv

if __name__ == '__main__':
    exp_range = chain(range(2,20), range(20, 200, 10), range(200, 2000, 100), range(2000, 10001, 500))
    nb_samples = 5
    test_and_print_csv(exp_range, nb_samples)
    
