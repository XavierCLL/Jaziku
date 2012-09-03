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

import globals_vars

def calculate_common_period(station):
    """
    Calculate common period (interception) in years of dates from
    dependent and independent variable.

    Return: common_period[[  date ,  var_D ,  var_I ],... ]
    """
    # interceptions values of date_D and date_I (python set functions wuau!!)
    common_date = list(set(station.date_D) & set(station.date_I))
    # sort common date
    common_date.sort()

    # initialized variable common_period
    # format list: [[  date ,  var_D ,  var_I ],... ]
    if globals_vars.config_run['process_period']:
        if (globals_vars.config_run['process_period']['start'] < common_date[0].year + 1 or
            globals_vars.config_run['process_period']['end'] > common_date[-1].year - 1):
            sys.stdout.write(_("Calculating the process period ................ "))
            sys.stdout.flush()
            console.msg_error(_(
                "The period defined in argument {0}-{1} is outside in the\n"
                "maximum possible period for this station: {2}-{3}.")
            .format(globals_vars.config_run['process_period']['start'],
                globals_vars.config_run['process_period']['end'],
                common_date[0].year + 1, common_date[-1].year - 1))

        common_date = common_date[common_date.index(date(globals_vars.config_run['process_period']['start'] - 1, 1, 1)):
        common_date.index(date(globals_vars.config_run['process_period']['end'] + 1, 12, 1)) + 1]

    common_period = []
    # set values matrix for common_period
    for date_period in common_date:
        # common_period format list: [[  date ,  var_D ,  var_I ],... ]
        common_period.append([date_period,
                              station.var_D[station.date_D.index(date_period)],
                              station.var_I[station.date_I.index(date_period)]])

    # check if the common period at least 3 years
    # because the data process is:
    #     common-period-start + 1 to common-period-end - 1
    if len(common_date) < 36:
        sys.stdout.write(_("Calculating the common period ................. "))
        sys.stdout.flush()

        console.msg_error(_("The common period calculated {0}-{1} has not at "
                            "least 3 years.").format(common_date[0].year,
            common_date[-1].year))

    return common_period

