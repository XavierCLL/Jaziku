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

import numpy


def dms2dd(dms):
    """Convert degrees:minutes:seconds to decimal degrees.

    :param dms: May be a string of the form "DDD:MM:SS".  Actually, DDD,
    MM, and SS may be separated by any non-digit except ".", "+",
    or "-".  Alternatively, it may be a tuple/list/array of the
    form [ddd, mm, ss].  In either case, if any element is < 0,
    then the result will be negative.  The numeric value -0 is not
    < 0, but this function will treat the string value "-0" as < 0.
    :type dms: str

    :examples: dms2dd("87:35:06")

    based on script in mskpy written by Michael S. Kelley, UMD, Dec 2009
    """
    if (type(dms) in [list, tuple, numpy.ndarray]) and isinstance(dms[0], str):
        return numpy.array([dms2dd(x) for x in dms])

    def a2space(c):
        if c.isdigit() or c in ['.', '+', '-']:
            return c
        else:
            return " "

    if isinstance(dms, str):
        # sometimes we specifiy negative angles with -00:12:34.  If a
        # minus sign appears anywhere in dms, set the sign of all
        # values to negative
        if dms.find('-') >= 0:
            s = -1.0
        else:
            s = 1.0

        dms = ''.join(map(a2space, dms)).split(" ")
        # there shouldn't be more than three sets of numbers
        dms = s * numpy.array(dms[:3], dtype=float)
    else:
        dms = numpy.array(dms, dtype=float)

    # If any value is < 0, the final result should be < 0
    if (numpy.sign(dms) < 0).any():
        s = -1.0
    else:
        s = 1.0
    dms = numpy.abs(dms)

    dd = dms[0]
    if len(dms) > 1: dd += dms[1] / 60.0
    if len(dms) > 2: dd += dms[2] / 3600.0
    return s * dd
