import logging
from tests.parallel_test.reserve_and_test import perform_experiment

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    perform_experiment(
        list_nb_components=[1, 3],
        list_nb_parallel_transitions=[1, 5, 10, 20],
        nb_repeats=5,
        working_directory="small_exp_ssh",
        ssh_test=True
    )
