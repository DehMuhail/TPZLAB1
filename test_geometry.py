import unittest

from geometry import (
    line_from_general,
    line_from_point_normal,
    classify_pair,
    intersection_point,
    analyze_three,
    # CHANGED: added direct tests for unique_points.
    unique_points,
    validate_in_range,
)

LO = -146.0
HI = 146.0


class TestValidation(unittest.TestCase):
    def test_edges_ok(self):
        validate_in_range([LO, 0.0, HI], LO, HI)

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            validate_in_range([HI + 1e-6], LO, HI)

    # CHANGED: added missing lower-bound validation test.
    def test_below_range(self):
        with self.assertRaises(ValueError):
            validate_in_range([LO - 1e-6], LO, HI)


class TestLineCreation(unittest.TestCase):
    def test_general_invalid(self):
        with self.assertRaises(ValueError):
            line_from_general(0.0, 0.0, 1.0)

    def test_form6_invalid_normal(self):
        with self.assertRaises(ValueError):
            line_from_point_normal(0.0, 0.0, 0.0, 0.0)

    def test_form6_build(self):
        l = line_from_point_normal(2.0, 3.0, 1.0, 0.0)
        self.assertAlmostEqual(l.A, 1.0, places=9)
        self.assertAlmostEqual(l.B, 0.0, places=9)
        self.assertAlmostEqual(l.C, -2.0, places=9)


class TestPair(unittest.TestCase):
    def test_parallel(self):
        l1 = line_from_general(0.0, 1.0, 0.0)
        l2 = line_from_general(0.0, 1.0, -1.0)
        self.assertEqual(classify_pair(l1, l2), "parallel")
        self.assertIsNone(intersection_point(l1, l2))

    def test_coincident(self):
        l1 = line_from_general(2.0, 2.0, 2.0)
        l2 = line_from_general(1.0, 1.0, 1.0)
        self.assertEqual(classify_pair(l1, l2), "coincident")

    def test_intersect(self):
        l1 = line_from_general(1.0, 0.0, 0.0)
        l2 = line_from_general(0.0, 1.0, 0.0)
        p = intersection_point(l1, l2)
        self.assertIsNotNone(p)
        self.assertAlmostEqual(p[0], 0.0, places=7)
        self.assertAlmostEqual(p[1], 0.0, places=7)
    
    # CHANGED: renamed test to better describe the scenario.
    def test_axis_aligned_intersection(self):
        l_y2 = line_from_general(0.0, 1.0, -2.0)
        l_x3 = line_from_general(1.0, 0.0, -3.0)
        p = intersection_point(l_y2, l_x3)
        self.assertIsNotNone(p)
        self.assertAlmostEqual(p[0], 3.0, places=7)
        self.assertAlmostEqual(p[1], 2.0, places=7)

# CHANGED: added dedicated tests for unique_points.
class TestUniquePoints(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(unique_points([]), [])

    def test_duplicates(self):
        pts = [(1.0, 2.0), (1.0, 2.0), (3.0, 4.0)]
        self.assertEqual(unique_points(pts), [(1.0, 2.0), (3.0, 4.0)])


class TestThree(unittest.TestCase):
    def test_three_points(self):
        L0 = line_from_general(1.0, 1.0, -1.0)
        L1 = line_from_general(0.0, 1.0, 0.0)
        L2 = line_from_general(1.0, 0.0, 0.0)
        res = analyze_three(L0, L1, L2)
        self.assertIsNone(res["special"])
        self.assertEqual(len(res["unique_points"]), 3)

    def test_two_points(self):
        L0 = line_from_general(0.0, 1.0, 0.0)
        L1 = line_from_general(0.0, 1.0, -1.0)
        L2 = line_from_general(1.0, 0.0, 0.0)
        res = analyze_three(L0, L1, L2)
        self.assertIsNone(res["special"])
        self.assertEqual(len(res["unique_points"]), 2)

    def test_all_coincident(self):
        L0 = line_from_general(1.0, 1.0, 1.0)
        L1 = line_from_general(2.0, 2.0, 2.0)
        L2 = line_from_general(-3.0, -3.0, -3.0)
        res = analyze_three(L0, L1, L2)
        self.assertEqual(res["special"], "all_three_coincident")

    def test_two_coincident_third_parallel(self):
        L0 = line_from_general(0.0, 1.0, 0.0)
        L1 = line_from_general(0.0, 2.0, 0.0)
        L2 = line_from_general(0.0, 1.0, -1.0)
        res = analyze_three(L0, L1, L2)
        self.assertEqual(res["special"], "two_coincident_third_parallel")

    def test_two_coincident_third_intersects(self):
        L0 = line_from_general(1.0, 1.0, 1.0)
        L1 = line_from_general(2.0, 2.0, 2.0)
        L2 = line_from_general(1.0, -1.0, 0.0)
        res = analyze_three(L0, L1, L2)
        self.assertEqual(res["special"], "two_coincident_third_intersects")
        self.assertEqual(len(res["unique_points"]), 1)

    # CHANGED: added missing case of three parallel non-coincident lines.
    def test_three_parallel_lines(self):
        L0 = line_from_general(0.0, 1.0, 0.0)
        L1 = line_from_general(0.0, 1.0, -1.0)
        L2 = line_from_general(0.0, 1.0, -2.0)
        res = analyze_three(L0, L1, L2)
        self.assertIsNone(res["special"])
        self.assertEqual(res["unique_points"], [])


if __name__ == "__main__":
    unittest.main()