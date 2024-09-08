#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-
#
#   © 2008 Thuswise Ltd
#
#   This file is part of the Balladeer distribution.
#
#   Balladeer is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Balladeer is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Balladeer.  If not, see <http://www.gnu.org/licenses/>.

from decimal import Decimal
from math import sqrt, pi, cos, sin
import sys
import types

try:
    from types import FloatType
    from types import IntType
    from types import TupleType
except ImportError:
    FloatType = float
    IntType = int
    TupleType = tuple

import unittest

from balladeer.lite.homogeneous import cross
from balladeer.lite.homogeneous import dot
from balladeer.lite.homogeneous import Homogeneous
from balladeer.lite.homogeneous import maxpick
from balladeer.lite.homogeneous import minpick
from balladeer.lite.homogeneous import normalise
from balladeer.lite.homogeneous import point
from balladeer.lite.homogeneous import premultiply
from balladeer.lite.homogeneous import vector


class FactoryTester(unittest.TestCase):
    """
    Contains test cases for Homogeneous factory functions
    """

    def test_point_empty(self):
        obj = point()
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 1)
        self.assertEqual(obj, (1, ))
        self.assertEqual(type(obj[-1]), IntType)

    def test_point_int(self):
        obj = point(1, 2, 3)
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 4)
        self.assertEqual(obj, (1, 2, 3, 1))
        self.assertEqual(type(obj[-1]), IntType)

    def test_point_float(self):
        obj = point(1.1, 2.2, 3.3)
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 4)
        for a, b in zip(obj, (1.1, 2.2, 3.3, 1.0)):
            self.assertAlmostEqual(a, b)
        self.assertEqual(type(obj[-1]), FloatType)

    def test_point_decimal(self):
        obj = point(Decimal("1.1"), Decimal("2.2"), Decimal("3.3"))
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 4)
        self.assertEqual(obj[-1], Decimal("1.0"))
        self.assertEqual(type(obj[-1]), Decimal)

    def test_vector_empty(self):
        obj = vector()
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 1)
        self.assertEqual(obj, (0, ))
        self.assertEqual(type(obj[-1]), IntType)

    def test_vector_int(self):
        obj = vector(1, 2, 3)
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 4)
        self.assertEqual(obj, (1, 2, 3, 0))
        self.assertEqual(type(obj[-1]), IntType)

    def test_vector_float(self):
        obj = vector(1.1, 2.2, 3.3)
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 4)
        for a, b in zip(obj, (1.1, 2.2, 3.3, 0.0)):
            self.assertAlmostEqual(a, b)
        self.assertEqual(type(obj[-1]), FloatType)

    def test_vector_decimal(self):
        obj = vector(Decimal("1.1"), Decimal("2.2"), Decimal("3.3"))
        self.assertTrue(isinstance(obj, Homogeneous))
        self.assertTrue(isinstance(obj, TupleType))
        self.assertEqual(len(obj), 4)
        self.assertEqual(obj[-1], Decimal("0.0"))
        self.assertEqual(type(obj[-1]), Decimal)


class ArithmeticTester(unittest.TestCase):
    """
    Contains test cases for arithmetical operations on Homogeneous
    objects
    """

    def test_sub_vectors(self):
        x = vector(1.1, 2.2, 3.3)
        y = vector(0.5, 0.6, 0.7)
        z = x - y
        for a, b in zip(z, (0.6, 1.6, 2.6, 0.0)):
            self.assertAlmostEqual(a, b)

    def test_sub_points(self):
        x = point(1.1, 2.2, 3.3)
        y = point(0.5, 0.6, 0.7)
        z = x - y
        for a, b in zip(z, (0.6, 1.6, 2.6, 0.0)):
            self.assertAlmostEqual(a, b)

    def test_sub_mixed(self):
        x = point(1.1, 2.2, 3.3)
        y = vector(0.5, 0.6, 0.7)
        z = x - y
        for a, b in zip(z, (0.6, 1.6, 2.6, 1.0)):
            self.assertAlmostEqual(a, b)

    def test_add_vectors(self):
        x = vector(1.1, 2.2, 3.3)
        y = vector(0.5, 0.6, 0.7)
        z = x + y
        for a, b in zip(z, (1.6, 2.8, 4.0, 0.0)):
            self.assertAlmostEqual(a, b)

    def test_add_mixed(self):
        x = point(1.1, 2.2, 3.3)
        y = vector(0.5, 0.6, 0.7)
        z = x + y
        for a, b in zip(z, (1.6, 2.8, 4.0, 1.0)):
            self.assertAlmostEqual(a, b)

    def test_mult_vector_by_int(self):
        z = vector(1.1, 2.2, 3.3) * 3
        for a, b in zip(z, vector(3.3, 6.6, 9.9)):
            self.assertAlmostEqual(a, b)

    def test_mult_vector_by_float(self):
        z = 3.3 * vector(1, 2, 3)
        for a, b in zip(z, vector(3.3, 6.6, 9.9)):
            self.assertAlmostEqual(a, b)

    def test_div_vectors(self):
        z = vector(3.3, 6.6, 9.9) / 3
        for a, b in zip(z, vector(1.1, 2.2, 3.3)):
            self.assertAlmostEqual(a, b)

    def test_mult_points(self):
        p = point(1.1, 2.2, 3.3)
        self.assertRaises(
            NotImplementedError,
            p.__mul__, 3)

    def test_dot_int(self):
        """ Hill and Kelley 3rd Ed., example 4.3.1 """
        self.assertEqual(
            dot(vector(2, 3, 1), vector(0, 4, -1)),
            11
        )
        self.assertEqual(
            dot(vector(22, 2, 7), vector(12, -9, 11)),
            323
        )

    def test_dot_float(self):
        """ Hill and Kelley 3rd Ed., example 4.3.1 """
        self.assertEqual(
            dot(vector(2, 2, 2, 2), vector(4, 1, 2, 1.1)),
            16.2
        )
        self.assertEqual(
            dot(vector(169, 0, 43), vector(0, -375.3, 0)),
            0
        )

    def test_cross_int(self):
        """ Hill and Kelley 3rd Ed., example 4.4.3 """
        self.assertEqual(
            cross(vector(1, 3, -2), vector(0, 2, 2)),
            vector(10, -2, 2)
        )

    def test_gt_of_points(self):
        """ Test component-wise greater-than """
        self.assertTrue(point(1, 0, 0) > point(0, 0, 0))
        self.assertTrue(point(0, 1, 0) > point(0, 0, 0))
        self.assertTrue(point(0, 0, 1) > point(0, 0, 0))
        self.assertTrue(point(0, 0, 0) > point(-1, 0, 0))
        self.assertTrue(point(0, 0, 0) > point(0, -1, 0))
        self.assertTrue(point(0, 0, 0) > point(0, 0, -1))

    def test_lt_of_points(self):
        """ Test component-wise less-than """
        self.assertTrue(point(0, 0, 0) < point(1, 0, 0))
        self.assertTrue(point(0, 0, 0) < point(0, 1, 0))
        self.assertTrue(point(0, 0, 0) < point(0, 0, 1))
        self.assertTrue(point(-1, 0, 0) < point(0, 0, 0))
        self.assertTrue(point(0, -1, 0) < point(0, 0, 0))
        self.assertTrue(point(0, 0, -1) < point(0, 0, 0))

    def test_max_of_points(self):
        """ Test component-wise maximum """
        self.assertEqual(
            max(point(1, 0, 0), point(0, 0, 0)),
            point(1, 0, 0)
        )
        self.assertEqual(
            max(point(0, -1, 0), point(0, 0, 0)),
            point(0, 0, 0)
        )

    def test_min_of_points(self):
        """ Test component-wise minimum """
        self.assertEqual(
            min(point(0, 0, 0), point(1, 0, 0)),
            point(0, 0, 0)
        )
        self.assertEqual(
            min(point(0, -1, 0), point(0, 0, 0)),
            point(0, -1, 0)
        )

    def test_maxpick_of_points(self):
        """ Test component-wise maximum """
        self.assertEqual(
            maxpick(point(1, 0, 0), point(0, 1, 0)),
            point(1, 1, 0)
        )
        self.assertEqual(
            maxpick(point(0, -1, 1), point(0, 0, 0)),
            point(0, 0, 1)
        )

    def test_minpick_of_points(self):
        """ Test component-wise minimum """
        self.assertEqual(
            minpick(point(0, 0, -1), point(1, 0, 0)),
            point(0, 0, -1)
        )
        self.assertEqual(
            minpick(point(0, -1, 1), point(0, 0, 0)),
            point(0, -1, 0))

    def test_magnitude_of_vectors(self):
        """ Test calculation of vector magnitudes """
        self.assertAlmostEqual(vector(1, 1).magnitude, sqrt(2))
        self.assertAlmostEqual(vector(1, sqrt(3)).magnitude, 2)
        self.assertAlmostEqual(vector(3, 4).magnitude, 5)

    def test_magnitude_of_points(self):
        """ Test calculation of point vector magnitudes """
        self.assertAlmostEqual(point(1, 1).magnitude, sqrt(2))
        self.assertAlmostEqual(point(1, sqrt(3)).magnitude, 2)
        self.assertAlmostEqual(point(3, 4).magnitude, 5)

    def test_normalise_of_vector(self):
        """ Test normalisation of vectors """
        self.assertAlmostEqual(normalise(vector(1, 1)).magnitude, 1)
        self.assertAlmostEqual(
            normalise(vector(1, sqrt(3))).magnitude,
            1)
        self.assertAlmostEqual(normalise(vector(3, 4)).magnitude, 1)

    def test_premultiply_of_short_tuple(self):
        """ Check behaviour when premultiply is passed a tuple, rather
        than a Homogeneous object """
        # from Hill and Kelley 3rd Ed., ex 5.3.2
        c, s = 0.866, 0.5
        self.assertRaises(
            AssertionError,
            premultiply,
            (3, 1, 4), (c, 0, s, 0), (0, 1, 0, 0),
            (-s, 0, c, 0), (0, 0, 0, 1)
        )

    def test_premultiply_of_full_tuple(self):
        """ Check behaviour when premultiply is passed a tuple, rather
        than a Homogeneous object """
        # from Hill and Kelley 3rd Ed., ex 5.3.2
        c, s = 0.866, 0.5
        result = premultiply(
            (3, 1, 4, 1), (c, 0, s, 0), (0, 1, 0, 0),
            (-s, 0, c, 0), (0, 0, 0, 1))
        self.assertEqual(len(result), 4)
        self.assertAlmostEqual(result[0], 4.6, 2)
        self.assertAlmostEqual(result[1], 1.0, 2)
        self.assertAlmostEqual(result[2], 1.964, 2)
        self.assertAlmostEqual(result[3], 1.0, 2)
        self.assertEqual(type(result), Homogeneous)

    def test_premultiply_of_point(self):
        """ Check behaviour when premultiply is passed a point """
        # from Hill and Kelley 3rd Ed., ex 5.3.2
        c, s = 0.866, 0.5
        result = premultiply(
            point(3, 1, 4), (c, 0, s, 0), (0, 1, 0, 0),
            (-s, 0, c, 0), (0, 0, 0, 1)
        )
        self.assertEqual(len(result), 4)
        self.assertAlmostEqual(result[0], 4.6, 2)
        self.assertAlmostEqual(result[1], 1.0, 2)
        self.assertAlmostEqual(result[2], 1.964, 2)
        self.assertAlmostEqual(result[3], 1.0, 2)
        self.assertEqual(type(result), Homogeneous)

    def test_premultiply_of_vector(self):
        """ Check behaviour when premultiply is passed a vector """
        # from Hill and Kelley 3rd Ed., ex 5.3.2
        c, s = 0.866, 0.5
        result = premultiply(
            vector(3, 1, 4), (c, 0, s, 0), (0, 1, 0, 0),
            (-s, 0, c, 0), (0, 0, 0, 1)
        )
        self.assertEqual(len(result), 4)
        self.assertAlmostEqual(result[0], 4.6, 2)
        self.assertAlmostEqual(result[1], 1.0, 2)
        self.assertAlmostEqual(result[2], 1.964, 2)
        self.assertAlmostEqual(result[3], 0.0, 2)
        self.assertEqual(type(result), Homogeneous)
