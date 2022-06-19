from evaluation.experiment import generate_taux_recouvrements
from unittest.mock import patch


def test_compute_covering_time_dep():
    freq = 2
    time_awoken = 3
    uptimes_list = (((12, 3), (25.7, 3)), ((10.5, 3), (14.3, 3)), ((11.9, 3), (25.7, 3)))
    expected_overlaps = [
        (1.5+0.7)/(time_awoken*freq),  # OU1/OU2
        (2.9+3)/(time_awoken*freq)     # OU1/OU3
    ]
    overlaps_list = generate_taux_recouvrements.compute_covering_time_dep(0, freq, time_awoken, uptimes_list)
    print(overlaps_list, expected_overlaps)

    expected_overlaps = [
        (1.5+0.7)/(time_awoken*freq),  # OU2/OU1
        (1.6+0.6)/(time_awoken*freq)   # OU2/OU3
    ]
    overlaps_list = generate_taux_recouvrements.compute_covering_time_dep(1, freq, time_awoken, uptimes_list)
    print(overlaps_list, expected_overlaps)

    expected_overlaps = [
        (2.9+3)/(time_awoken*freq),    # OU3/OU1
        (1.6+0.6)/(time_awoken*freq)   # OU3/OU2
    ]
    overlaps_list = generate_taux_recouvrements.compute_covering_time_dep(2, freq, time_awoken, uptimes_list)
    print(overlaps_list, expected_overlaps)


if __name__ == '__main__':
    test_compute_covering_time_dep()
