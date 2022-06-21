from evaluation.experiment import concerto_d_g5k


def main():
    controller_role, networks = concerto_d_g5k.reserve_node_for_controller("econome")
    concerto_d_g5k.initiate_concerto_d_dir(controller_role["controller"])


if __name__ == '__main__':
    main()
