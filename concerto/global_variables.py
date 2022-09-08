CONCERTO_D_SYNCHRONOUS = "synchronous"
CONCERTO_D_ASYNCHRONOUS = "asynchronous"

execution_expe_dir = None
concerto_d_version = None


def is_concerto_d_asynchronous():
    return concerto_d_version == CONCERTO_D_ASYNCHRONOUS
