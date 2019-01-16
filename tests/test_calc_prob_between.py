from unittest import TestCase
from scipy.stats import beta
from mixbaba.mixbaba_utils import calc_prob_between
import numpy as np

class TestCalc_prob_between(TestCase):
    """
    For details on the results of the following tests check:
    https://towardsdatascience.com/bayesian-a-b-testing-with-python-the-easy-guide-d638f89e0b8a
    """
    def test_calc_prob_same(self):
        """
        This test checks that the probability for a beta distribution to be bigger than itself is 50%
        """
        beta_ = beta(10, 1000)
        result = calc_prob_between(beta_, beta_)  # result should be 0.5

        self.assertTrue(np.allclose(result, 0.5))

    def test_calc_prob_diff(self):
        """
        This test checks that beta_1 is worse than beta_2
        """
        beta_1 = beta(40, 1000)
        beta_2 = beta(80, 300)
        result = calc_prob_between(beta_1, beta_2)  # result should be almost zero
        self.assertGreater(result, 0.)
        self.assertTrue(np.allclose(result, 0.))
