from evaluation.experiment import concerto_d_g5k


def main():
    # TODO: mettre à jour le python-grid5000 avec verify_ssl pour autoriser les réservations depuis le front-end
    # Mettre à jour python-grid5000 n'a pas l'air d'être une bonne solution car la version d'enoslib utilise une
    # version specific de python-grid5000
    # TODO: à signaler: même avec verify_ssl ça ne suffit pas il faut mettre le user et le mdp sur le front-end
    controller_role, networks = concerto_d_g5k.reserve_node_for_controller("econome")
    concerto_d_g5k.initiate_concerto_d_dir(controller_role["controller"])

    uptimes_dir_path = "evaluation/experiment/generated_covering_taux/2022-06-21_12-41-23"
    uptimes_file_name = "uptimes.json"
    concerto_d_g5k.put_uptimes_file(controller_role["controller"], uptimes_dir_path, uptimes_file_name)


if __name__ == '__main__':
    main()
