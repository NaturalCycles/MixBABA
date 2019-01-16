from unittest import TestCase
import json
from mixbaba.mixbaba_utils import aggregate_mix_data


class TestAggregate_mix_data(TestCase):
    def test_aggregate_mix_data(self):

        # `this_folder` is the folder where the present file exist.
        # This is needed to allow this test to be run from whatever position
        name_n_parents = __name__.split('.')
        if len(name_n_parents) > 1:
            only_parents = name_n_parents[:len(name_n_parents)-1]
            this_folder = ""
            for fold in only_parents:
                this_folder += fold
            this_folder += '/'
        else:
            this_folder = ''

        with open(this_folder + "mock_resp.json", 'r') as f:
            mock_resp = json.load(f)
        mock_aggregated = aggregate_mix_data(mock_resp['data'])
        with open(this_folder + "mock_aggregated.json", 'r') as f:
            mock_true_aggregated: dict = json.load(f)
        self.assertTrue(mock_aggregated == mock_true_aggregated)
