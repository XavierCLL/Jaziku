#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2017 Xavier Corredor Ll. - IDEAM
#
# This file is part of Jaziku.
#
# Jaziku is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jaziku is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jaziku.  If not, see <http://www.gnu.org/licenses/>.


def column(matrix, i):
    """Return column i from matrix

    :param matrix:
    :type matrix: list
    :param i: column i
    :type i: int

    :return: column i of matrix
    :rtype: list
    """

    return [row[i] for row in matrix]


def transpose(matrix):
    """Return transpose of matrix

    :param matrix: matrix in 2d dimension
    :type matrix: list

    :return: transpose of matrix
    :rtype: list
    """

    return list(map(list, list(zip(*matrix))))
