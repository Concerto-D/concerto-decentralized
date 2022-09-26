CONCERTO_D_SYNCHRONOUS = "synchronous"
CONCERTO_D_ASYNCHRONOUS = "asynchronous"

execution_expe_dir = None
concerto_d_version = None
reconfiguration_name = ""

current_nb_instructions_done = 0


def is_concerto_d_asynchronous():
    return concerto_d_version == CONCERTO_D_ASYNCHRONOUS
