import subprocess

from evaluation.experiment import concerto_d_g5k


def main():
    cluster = "econome"
    concerto_d_g5k.reserve_node_for_controller(cluster)
    # subprocess.Popen("evaluation/experiment/test.sh")
    return


if __name__ == '__main__':
    main()
