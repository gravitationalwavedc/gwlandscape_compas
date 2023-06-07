import json
import numpy as np

from django.test import TestCase

from publications.utils.plotting_functions import (
    get_surrounding_bins,
    get_log_and_limits,
    split_histogram_by_count,
    histo2d_scatter_hybrid
)


class TestGetSurroundingBins(TestCase):
    def setUp(self):
        self.x_lim, self.y_lim = 10, 10
        self.x_mid, self.y_mid = self.x_lim // 2, self.y_lim // 2

    def test_0_0(self):
        self.assertSequenceEqual(
            get_surrounding_bins([0, 0], self.x_lim, self.y_lim).tolist(),
            np.array([
                [0, 0], [0, 1],
                [1, 0], [1, 1]
            ]).tolist()
        )

    def test_x_lim_0(self):
        self.assertSequenceEqual(
            get_surrounding_bins([self.x_lim, 0], self.x_lim, self.y_lim).tolist(),
            np.array([
                [self.x_lim-1, 0], [self.x_lim-1, 1],
                [self.x_lim, 0], [self.x_lim, 1]
            ]).tolist()
        )

    def test_0_y_lim(self):
        self.assertSequenceEqual(
            get_surrounding_bins([0, self.y_lim], self.x_lim, self.y_lim).tolist(),
            np.array([
                [0, self.y_lim-1], [0, self.y_lim],
                [1, self.y_lim-1], [1, self.y_lim]
            ]).tolist()
        )

    def test_x_lim_y_lim(self):
        self.assertSequenceEqual(
            get_surrounding_bins([self.x_lim, self.y_lim], self.x_lim, self.y_lim).tolist(),
            np.array([
                [self.x_lim-1, self.y_lim-1], [self.x_lim-1, self.y_lim],
                [self.x_lim, self.y_lim-1], [self.x_lim, self.y_lim]
            ]).tolist()
        )

    def test_0_y_mid(self):
        self.assertSequenceEqual(
            get_surrounding_bins([0, self.y_mid], self.x_lim, self.y_lim).tolist(),
            np.array([
                [0, self.y_mid-1], [0, self.y_mid], [0, self.y_mid+1],
                [1, self.y_mid-1], [1, self.y_mid], [1, self.y_mid+1]
            ]).tolist()
        )

    def test_x_lim_y_mid(self):
        self.assertSequenceEqual(
            get_surrounding_bins([self.x_lim, self.y_mid], self.x_lim, self.y_lim).tolist(),
            np.array([
                [self.x_lim-1, self.y_mid-1], [self.x_lim-1, self.y_mid], [self.x_lim-1, self.y_mid+1],
                [self.x_lim, self.y_mid-1], [self.x_lim, self.y_mid], [self.x_lim, self.y_mid+1]
            ]).tolist()
        )

    def test_x_mid_0(self):
        self.assertSequenceEqual(
            get_surrounding_bins([self.x_mid, 0], self.x_lim, self.y_lim).tolist(),
            np.array([
                [self.x_mid-1, 0], [self.x_mid-1, 1],
                [self.x_mid, 0], [self.x_mid, 1],
                [self.x_mid+1, 0], [self.x_mid+1, 1]
            ]).tolist()
        )

    def test_x_mid_y_lim(self):
        self.assertSequenceEqual(
            get_surrounding_bins([self.x_mid, self.y_lim], self.x_lim, self.y_lim).tolist(),
            np.array([
                [self.x_mid-1, self.y_lim-1], [self.x_mid-1, self.y_lim],
                [self.x_mid, self.y_lim-1], [self.x_mid, self.y_lim],
                [self.x_mid+1, self.y_lim-1], [self.x_mid+1, self.y_lim]
            ]).tolist()
        )

    def test_x_mid_y_mid(self):
        self.assertSequenceEqual(
            get_surrounding_bins([self.x_mid, self.y_mid], self.x_lim, self.y_lim).tolist(),
            np.array([
                [self.x_mid-1, self.y_mid-1], [self.x_mid-1, self.y_mid], [self.x_mid-1, self.y_mid+1],
                [self.x_mid, self.y_mid-1], [self.x_mid, self.y_mid], [self.x_mid, self.y_mid+1],
                [self.x_mid+1, self.y_mid-1], [self.x_mid+1, self.y_mid], [self.x_mid+1, self.y_mid+1],
            ]).tolist()
        )


class TestGetLogAndLimits(TestCase):
    def test_min_below_zero(self):
        test_array = np.array([-10, 0, 10])
        returned_array, log_check, min_max = get_log_and_limits(test_array)
        self.assertSequenceEqual(test_array.tolist(), returned_array.tolist())
        self.assertFalse(log_check)
        self.assertCountEqual(min_max, [-10, 10])

    def test_uniform_array_inside_bounds(self):
        test_array = np.array([10, 10, 10])
        returned_array, log_check, min_max = get_log_and_limits(test_array, max_cond=15, min_cond=5)
        self.assertSequenceEqual(test_array.tolist(), returned_array.tolist())
        self.assertFalse(log_check)
        self.assertCountEqual(min_max, [9.5, 10.5])

    def test_uniform_array_outside_bounds(self):
        test_array = np.array([10, 10, 10])
        returned_array, log_check, min_max = get_log_and_limits(test_array, max_cond=7.5, min_cond=5)
        self.assertSequenceEqual(np.log10(test_array).tolist(), returned_array.tolist())
        self.assertTrue(log_check)
        self.assertCountEqual(min_max, [0.5, 1.5])

        returned_array, log_check, min_max = get_log_and_limits(test_array, max_cond=15, min_cond=12.5)
        self.assertSequenceEqual(np.log10(test_array).tolist(), returned_array.tolist())
        self.assertTrue(log_check)
        self.assertCountEqual(min_max, [0.5, 1.5])

    def test_array_inside_bounds(self):
        test_array = np.array([10, 50, 100])
        returned_array, log_check, min_max = get_log_and_limits(test_array, max_cond=500, min_cond=5)
        self.assertSequenceEqual(test_array.tolist(), returned_array.tolist())
        self.assertFalse(log_check)
        self.assertCountEqual(min_max, [10, 100])

    def test_array_outside_bounds(self):
        test_array = np.array([10, 50, 100])
        returned_array, log_check, min_max = get_log_and_limits(test_array, max_cond=50, min_cond=5)
        self.assertSequenceEqual(np.log10(test_array).tolist(), returned_array.tolist())
        self.assertTrue(log_check)
        self.assertCountEqual(min_max, [1, 2])

        test_array = np.array([10, 50, 100])
        returned_array, log_check, min_max = get_log_and_limits(test_array, max_cond=500, min_cond=50)
        self.assertSequenceEqual(np.log10(test_array).tolist(), returned_array.tolist())
        self.assertTrue(log_check)
        self.assertCountEqual(min_max, [1, 2])


class TestSplitHistogramByCount(TestCase):
    def setUp(self):
        self.hist_data = np.array([
            [2, 0, 1, 1, 2],
            [0, 1, 0, 0, 1],
            [1, 0, 2, 0, 1],
            [1, 1, 2, 1, 0],
            [2, 0, 0, 0, 1],
        ])

    def test_split_histogram_by_count(self):
        self.assertSequenceEqual(
            split_histogram_by_count(self.hist_data, 1)[0].tolist(),
            np.array([
                [0, 0], [0, 3], [0, 4],
                [1, 1], [1, 4],
                [2, 2],
                [3, 0], [3, 1], [3, 2], [3, 3],
                [4, 0],
            ]).tolist()
        )
        self.assertSequenceEqual(
            split_histogram_by_count(self.hist_data, 1)[1].tolist(),
            np.array([
                [0, 2],
                [2, 0], [2, 4],
                [4, 4]
            ]).tolist()
        )


class TestHisto2DScatterHybrid(TestCase):
    def setUp(self):
        # 1 0 0 0 1
        # 0 1 2 1 0
        # 0 2 2 2 0
        # 0 1 2 1 0
        # 1 0 0 0 1
        self.x_array = np.array([1, 5, 1, 5, 2, 4, 2, 4, 3, 3, 3, 3, 3, 3, 2, 2, 4, 4])
        self.y_array = np.array([1, 1, 5, 5, 2, 2, 4, 4, 3, 3, 2, 2, 4, 4, 3, 3, 3, 3])

    def test_histo2d_scatter_hybrid(self):
        plot_data = histo2d_scatter_hybrid(self.x_array, self.y_array, min_count=1, bins=5)
        self.assertEqual(plot_data['sides'], [0.812, 0.812])
        self.assertCountEqual(json.loads(plot_data['hist_data']), [
            {"x": 2.208, "y": 2.208, "counts": 1.0},
            {"x": 2.208, "y": 3.02, "counts": 2.0},
            {"x": 2.208, "y": 3.832, "counts": 1.0},
            {"x": 3.02, "y": 2.208, "counts": 2.0},
            {"x": 3.02, "y": 3.02, "counts": 2.0},
            {"x": 3.02, "y": 3.832, "counts": 2.0},
            {"x": 3.832, "y": 2.208, "counts": 1.0},
            {"x": 3.832, "y": 3.02, "counts": 2.0},
            {"x": 3.832, "y": 3.832, "counts": 1.0}
        ])
        self.assertCountEqual(json.loads(plot_data['scatter_data']), [
            {"x": 1.0, "y": 1.0},
            {"x": 5.0, "y": 1.0},
            {"x": 1.0, "y": 5.0},
            {"x": 5.0, "y": 5.0}
        ])
