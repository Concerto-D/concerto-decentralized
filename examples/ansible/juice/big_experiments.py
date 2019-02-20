import logging

from reserve import perform_experiments

if __name__ == '__main__':
    #Testing
    logging.basicConfig(level=logging.DEBUG)
    perform_experiments(
        start_attempt=1,
        nb_attempts=15,
        nbs_nodes=[(3,10),(3,20),(20,0)]
    )
