#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2012 IDEAM
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

import globals_vars

def mean(values):
    """
    Return the mean from all values, ignoring valid null values.
    """

    sums = 0
    count = 0
    for value in values:
        if int(value) not in globals_vars.VALID_NULL:
            sums += value
            count += 1.0

    if count == 0:
        return globals_vars.VALID_NULL[1]

    return sums / count