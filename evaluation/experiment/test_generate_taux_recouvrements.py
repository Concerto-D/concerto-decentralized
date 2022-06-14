from evaluation.experiment import generate_taux_recouvrements
from unittest.mock import patch


@patch("random.uniform")
def test_nominal(mock_uniform):
    freqs_awake_list = [2]
    time_awakening = [3]
    nb_deps_list = [35]
    step_freq = 60
    mock_uniform.side_effect = [  # Each wakes up 2 times
        12, 25.7,    # OU1
        10.5, 14.2,  # OU2
        11.9, 25.7   # OU3
    ]
    uptimes_by_params = generate_taux_recouvrements.generate_uptimes_for_dependencies(
        freqs_awake_list, time_awakening, nb_deps_list, step_freq
    )
    print(uptimes_by_params)
    covering_by_params = generate_taux_recouvrements.compute_means_covering_by_params(uptimes_by_params)
    print(covering_by_params)
    global_means_coverage = generate_taux_recouvrements.compute_global_means_covering(covering_by_params)
    print(global_means_coverage)


if __name__ == '__main__':
    test_nominal()
