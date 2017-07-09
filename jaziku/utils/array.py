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

from math import isnan
from jaziku import env

from jaziku.env import globals_vars


def mean(values):
    """
    Return the mean from all values, ignoring valid null values.
    """

    # check if 'values' is only one number
    if isinstance(values, (int, float)):
        return values

    sums = 0
    count = 0
    for value in values:
        if not globals_vars.is_valid_null(value):
            sums += value
            count += 1.0

    if count == 0:
        return float('nan')

    return sums / count


def maximum(values):
    """
    max function for Jaziku with special behavior
    """

    values_cleaned = clean(values)
    if len(values_cleaned) == 0:
        return float('nan')
    else:
        return max(values_cleaned)


def minimum(values):
    """
    min function for Jaziku with special behavior
    """

    values_cleaned = clean(values)
    if len(values_cleaned) == 0:
        return float('nan')
    else:
        return min(values_cleaned)


def clean(values):
    """Clean the list of empty elements and valid nulls

    :param values: values to clean
    :type values: list

    :rtype: list
    """

    # delete empty elements in row, but not elements with zeros
    values = [e for e in values if e or e == 0]

    # delete all valid nulls
    values = [value for value in values if not globals_vars.is_valid_null(value)]

    return values


def check_nulls(values):
    """Return the number and percentage of valid null values inside array.

    :param values: values to check the nulls
    :type values: list

    :ivar number_of_nulls: number of nulls
    :ivar percentage_of_nulls: percentage of nulls inside values (0-100)
    :rtype: (int, float)
    """

    if len(values) == 0:
        return float('nan'), float('nan')

    number_of_nulls = 0
    for value in values:
        if env.globals_vars.is_valid_null(value):
            number_of_nulls += 1

    percentage_of_nulls = round((number_of_nulls / float((len(values)))) * 100, 1)

    return number_of_nulls, percentage_of_nulls
