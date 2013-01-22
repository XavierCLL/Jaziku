#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2013 IDEAM
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

    if len(values) == 0:
        return float('nan')
    else:
        # test if there is a nan value in list
        for value in values:
            if isnan(value):
                values = clean(values)
                return max(values)

        return max(values)

def minimum(values):
    """
    min function for Jaziku with special behavior
    """

    if len(values) == 0:
        return float('nan')
    else:
        # test if there is a nan value in list
        for value in values:
            if isnan(value):
                values = clean(values)
                return min(values)

        return min(values)

def clean(values):
    """
    Clean the list of empty elements and valid nulls
    """

    # delete empty elements in row
    values = [e for e in values if e]

    # delete all valid nulls
    values = [ value for value in values if not globals_vars.is_valid_null(value) ]

    return values