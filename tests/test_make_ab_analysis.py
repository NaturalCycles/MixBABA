from unittest import TestCase
from mixbaba.mixbaba_utils import make_ab_analysis

class TestMake_ab_analysis(TestCase):
    convs_1 = 100
    imps_1 = 10000
    convs_2 = 120
    imps_2 = 10000

    def test_make_ab_analysis_diff(self):
        """
        Checks that the results for a controlled experiment are the one expected
        """
        uplift, prob = make_ab_analysis(self.imps_1, self.convs_1, self.imps_2, self.convs_2)
        self.assertAlmostEqual(uplift, 0.19801980)
        self.assertAlmostEqual(prob, 0.91201253)

    def test_make_ab_analysis_same(self):
        uplift2, prob2 = make_ab_analysis(self.imps_1, self.convs_1, self.imps_1, self.convs_1)
        self.assertAlmostEqual(uplift2, 0.0)
        self.assertAlmostEqual(prob2, 0.5)
