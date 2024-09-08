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

from math import sqrt

__doc__ = """
    The module consists of several functions which operate on
    Homogeneous coordinates to support 2D or 3D geometric
    calculations.

"""

__all__ = [
    "point", "vector", "posvector", "normalise", "dot", "cross",
    "premultiply", "maxpick", "minpick"
]


class Homogeneous(tuple):
    """
    This class implements homogeneous coordinates. A good textbook
    like `Hill and Kelley`_ will explain how these can be used to
    represent both points and vectors in graphical applications.

    The class acts like a standard Python tuple_. You need not create
    instances of this class directly; use the factory functions below
    instead.

    .. _Hill and Kelley: http://books.google.co.uk/books/about/\
Computer_graphics.html?id=ffkYAQAAIAAJ
    .. _tuple: https://docs.python.org/3/library/stdtypes.html#tuple

    """

    def __new__(cls, seq, point=None):
        """
        Class level constructor. Creates a tuple, but adds the phi
        coordinate if required.

        :param seq: contains the data for the array.
        :type seq: a sequence
        :param point: should be 0 for a vector, 1 for a point, or
            None to preserve the existing representation.
        :type point: an optional value
        :returns: a new object.
        :rtype: Homogeneous
        """
        if point is None:
            # copy constructor
            return tuple.__new__(Homogeneous, seq)
        else:
            # extra coordinate required
            try:
                typ = type(seq[0])
            except IndexError:
                # seq is empty
                typ = int
            return tuple.__new__(Homogeneous, seq + (typ(point), ))

    def __gt__(self, other):
        """ Performs comparison tournament """
        return (
            max([a > b for a, b in zip(self, other)]) and not
            max([b > a for a, b in zip(self, other)]))

    def __gte__(self, other):
        """ Performs comparison tournament """
        return (
            max([a >= b for a, b in zip(self, other)]) and not
            max([b > a for a, b in zip(self, other)]))

    def __lt__(self, other):
        """ Performs comparison tournament"""
        return (
            max([a < b for a, b in zip(self, other)]) and not
            max([b < a for a, b in zip(self, other)]))

    def __lte__(self, other):
        """ Performs comparison tournament"""
        return (
            max([a <= b for a, b in zip(self, other)]) and not
            max([b < a for a, b in zip(self, other)]))

    def __sub__(self, other):
        """ Performs comparison tournament"""
        return Homogeneous([a - b for a, b in zip(self, other)])

    def __rsub__(self, other):
        """ Performs comparison tournament"""
        return Homogeneous([a - b for a, b in zip(self, other)])

    def __add__(self, other):
        """ Performs element-wise addition """
        return Homogeneous([a + b for a, b in zip(self, other)])

    def __radd__(self, other):
        """ Performs element-wise addition for reversed arguments"""
        return Homogeneous([a + b for a, b in zip(self, other)])

    def __mul__(self, other):
        """ Performs scalar multiplication on vector only"""
        if not self[-1]:
            return Homogeneous([other * i for i in self])
        else:
            raise NotImplementedError

    def __rmul__(self, other):
        """ Performs scalar multiplication on vector only"""
        return self.__mul__(other)

    def __floordiv__(self, other):
        """ Performs scalar division on vector only"""
        if not self[-1]:
            return Homogeneous([i // other for i in self])
        else:
            raise NotImplementedError

    def __truediv__(self, other):
        """ Performs scalar division on vector only"""
        if not self[-1]:
            return Homogeneous([i / other for i in self])
        else:
            raise NotImplementedError

    @property
    def magnitude(self):
        """
        A property which gives the magnitude of a Homogeneous vector
        (position vector in the case of a point).

        :rtype: number.
        """
        return sqrt(sum([i ** 2 for i in self[:-1]]))


def point(*args):
    """
    Use this factory function to create homogeneous points.

    :param args: coordinates for the point.
    :returns: a new point object.
    :rtype: Homogeneous
    """
    return Homogeneous(args, point=1)


def vector(*args):
    """
    Use this factory function to create homogeneous vectors.

    :param args: coordinates for the vector.
    :returns: a new vector object.
    :rtype: Homogeneous
    """
    return Homogeneous(args, point=0)


def posvector(point):
    """
    Returns the position vector of a point.

    :param point: a point.
    :type point: Homogeneous
    :returns: a new vector object.
    :rtype: Homogeneous
    """
    return Homogeneous(point[:-1], point=0)


def normalise(vec):
    """
    Scales a vector so its magnitude is unity.

    :param vec: a vector.
    :type vec: Homogeneous
    :returns: a new vector object.
    :rtype: Homogeneous
    :requires: vec to be a vector.
    """
    m = vec.magnitude
    return vec / m


def dot(one, tother):
    """
    Calculates the dot product of two vectors.

    :param one: a vector.
    :type one: Homogeneous
    :param tother: a vector.
    :type tother: Homogeneous
    :returns: the scalar product.
    :rtype: number.
    """
    return sum((a * b for a, b in zip(one, tother)))


def cross(one, tother):
    """
    Calculates the cross product of two vectors. Works in 3D only.

    :param one: a vector.
    :type one: Homogeneous
    :param tother: a vector.
    :type tother: Homogeneous
    :returns: a vector.
    :rtype: Homogeneous.
    """
    try:
        i = one[1] * tother[2] - one[2] * tother[1]
        j = one[2] * tother[0] - one[0] * tother[2]
        k = one[0] * tother[1] - one[1] * tother[0]
        return vector(i, j, k)
    except IndexError:
        raise NotImplementedError


def premultiply(hom, *rows):
    """
    Performs a matrix transformation M{Mp} on a point or vector.
    The matrix is supplied as a number of tuples, each one being a row
    of the transformation matrix. The matrix must be properly sized to
    match a homogeneous array, ie: to transform a 3D (4-element) point,
    you need four rows each containing four values.

    :param hom: a point or vector.
    :type hom: Homogeneous
    :param rows: matrix data.
    :type rows: tuples
    :returns: a point or vector.
    :rtype: Homogeneous.
    :requires: there must be as many rows as there are elements in hom,
               and each must be the length of hom.
    """
    assert len(hom) == len(rows[0])
    return Homogeneous(
        [sum([p * e for p, e in zip(hom, r)]) for r in rows], None)


def maxpick(one, tother):
    """
    Performs elementwise comparison of two points or vectors and keeps
    the larger of each corresponding element.

    :param one: a point or vector.
    :type one: Homogeneous
    :param tother: a point or vector.
    :type tother: Homogeneous
    :returns: a point or vector.
    :rtype: Homogeneous.
    """
    return Homogeneous(
        [max(a, b) for a, b in zip(one, tother)], None)


def minpick(one, tother):
    """
    Performs elementwise comparison of two points or vectors and keeps
    the smaller of each corresponding element.

    :param one: a point or vector.
    :type one: Homogeneous
    :param tother: a point or vector.
    :type tother: Homogeneous
    :returns: a point or vector.
    :rtype: Homogeneous.
    """
    return Homogeneous(
        [min(a, b) for a, b in zip(one, tother)], None)
