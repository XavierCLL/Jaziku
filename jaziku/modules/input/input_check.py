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

import sys
from datetime import date
from calendar import monthrange

from ...utils import globals_vars

def check_consistent_data(station, var):
    """
    Check if the data are consistent, this is that the amount of null value
    not exceed in 15% of the total number of values inside process period
    """

    # temporal var initialize start_date = start common_period + 1 year,
    # month=1, day=1
    start_date = date(station.process_period['start'], 1, 1)
    # temporal var initialize end_date = end common_period - 1 year,
    # month=12, day=31
    if (var == "D" and station.data_of_var_D == "daily") or\
       (var == "I" and station.data_of_var_I == "daily"):
        end_date = date(station.process_period['end'], 12, 31)
        if station.analysis_interval == "trimester":
            date_plus = monthrange(station.process_period['end'] + 1, 1)[1] +\
                        monthrange(station.process_period['end'] + 1, 2)[1]
            date_minus = 61
        else:
            date_plus = date_minus = station.analysis_interval_num_days * 2
    else:
        end_date = date(station.process_period['end'], 12, 1)
        date_plus = date_minus = 2

    if var == "D":
        values_in_common_period \
            = station.var_D[station.date_D.index(start_date):station.date_D.index(end_date) + date_plus + 1]
    if var == "I":
        values_in_common_period \
            = station.var_I[station.date_I.index(start_date) - date_minus:station.date_I.index(end_date) + date_plus + 1]

    null_counter = 0
    for value in values_in_common_period:
        if value in globals_vars.VALID_NULL:
            null_counter += 1

    sys.stdout.write(_("({0} null of {1})\t").format(null_counter, len(values_in_common_period)))
    sys.stdout.flush()

    if  null_counter / float(len(values_in_common_period)) >= 0.15:
        console.msg_error(_("the number of null values is greater than 15% of total\n"
                            "of values inside common period, therefore, for Jaziku\n"
                            "the data are not consistent for process."))
#    return len(values_in_common_period), null_counter
