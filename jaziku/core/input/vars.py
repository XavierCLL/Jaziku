#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 IDEAM
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

import os
import csv
import re
from datetime import date
from dateutil.relativedelta import relativedelta

from jaziku import env
from jaziku.core.input import validation
from jaziku.utils import console, input, output


# ==============================================================================
# INPUT DATA PROCESSING
# Read and validation dependent and independent variables from file


def read_variable(variable):
    """Read dependent or independent variable for get and check date and
    data from the raw file. Accept daily, monthly, bimonthly and trimonthly
    frequency data. The check data is a process that validate value by
    value within limits defined in runfile as 'limits_var_X'.

    For data bimonthly and trimonthly, this need defined each date with
    characters, e.g. jfm = january-february-march

    :param station: station instance
    :type station: class Station
    :param variable: station.var_D or station.var_I to read the variable of
    the station for get and check date and data from the file.
    :type variable: class Variable

    Return by reference:

    :ivar STATION.var_X.data: data read from raw file
    :ivar STATION.var_X.date: date read from raw file
    """
    var_date = []
    var_data = []

    # check first if file exist
    if not os.path.isfile(variable.file_path):
        console.msg_error(
            _("Reading the station: {0} - {1}\n"
              "Can't open file '{2}' for var {3}, \nplease check filename and check that its path is relative\n"
              "(to runfile) or absolute.").format(variable.station.code, variable.station.name, variable.file_path,
                                                  variable.type))

    # Check is file is not empty
    if os.path.getsize(variable.file_path) == 0:
        console.msg_error(
            _("Reading the station: {0} - {1}\n"
              "The file '{2}' is empty").format(variable.station.code, variable.station.name, variable.file_path))

    open_file = open(variable.file_path, 'rU')

    # The series accept three delimiters: spaces (' '), tabulation ('\t') or semi-colon (';')
    # this check which delimiter is using this file
    test_line = open_file.readline()
    if len(test_line.split(env.globals_vars.INPUT_CSV_DELIMITER)) >= 2:
        delimiter = env.globals_vars.INPUT_CSV_DELIMITER
    if len(test_line.split(' ')) >= 2:
        delimiter = ' '
    if len(test_line.split('\t')) >= 2:
        delimiter = '\t'
    if len(test_line.split(';')) >= 2:
        delimiter = ';'
    open_file.seek(0)

    time_series_file = csv.reader(open_file, delimiter=delimiter)

    # time_series_file = csv.reader(fo, delimiter = '\t')
    # time_series_file.write(data.replace('\x00', ''))

    first = True
    # Read line to line time_series_file, validation and save variable
    for row in time_series_file:

        # if row is null o empty, e.g. empty but with tabs or spaces
        if not row or not row[0].strip():
            continue

        # delete empty elements in row
        row = [e for e in row if e]

        # get values
        try:
            date_value = row[0].replace('/', '-').split("-")
            value = row[1].replace(',', '.')
        except Exception:
            console.msg_error(_(
                "Reading from file '{0}' in line: {1}\n\n"
                "this could be caused by wrong line or strange character,\n"
                "fix it manually or run 'normalize_format {0}'")
                              .format(variable.file_name, time_series_file.line_num))

        # check if variable is daily or month
        if first:
            try:
                if len(date_value) == 3:
                    env.var_[variable.type].set_FREQUENCY_DATA("daily")
                else:
                    month = re.sub(r'[^\w]', '', date_value[1])
                    if month.isdigit():
                        env.var_[variable.type].set_FREQUENCY_DATA("monthly")
                    elif len(month) == 2:
                        env.var_[variable.type].set_FREQUENCY_DATA("bimonthly")
                    elif len(month) == 3:
                        env.var_[variable.type].set_FREQUENCY_DATA("trimonthly")
                    else:
                        raise ValueError(_('date unknown: ') + '-'.join(date_value))
            except ValueError as error:
                console.msg_error(_("Problems settings the frequency data for the station\n"
                                    "with code '{0}' and name '{1}':\n\n").format(variable.station.code,
                                                                                  variable.station.name) + str(error))

        try:
            # delete strange characters and convert format
            year = int(re.sub(r'[^\w]', '', date_value[0]))
            month = re.sub(r'[^\w]', '', date_value[1])

            if env.var_[variable.type].is_daily():
                month = int(month)
                day = int(re.sub(r'[^\w]', '', date_value[2]))
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(days=-1) != var_date[-1]:
                    missing_date = var_date[-1] + relativedelta(days=+1)
                    console.msg_error(_(
                        "Reading var {0} from file '{1}' in line: {2}\n\n"
                        "Jaziku detected missing value for date: {3}\n\n"
                        "fix it manually or run 'normalize_format {1}'")
                                      .format(variable.type, variable.file_name, time_series_file.line_num,
                                              missing_date))

            if env.var_[variable.type].is_monthly():
                month = int(month)
                day = 1
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(months=-1) != var_date[-1]:
                    missing_date = var_date[-1] + relativedelta(months=+1)
                    console.msg_error(_(
                        "Reading var {0} from file '{1}' in line: {2}\n\n"
                        "Jaziku detected missing value for date: {3}-{4}\n\n"
                        "fix it manually or run 'normalize_format {1}'")
                                      .format(variable.type, variable.file_name, time_series_file.line_num,
                                              missing_date.year, missing_date.month))

            if env.var_[variable.type].is_bimonthly():
                month = input.bimonthly_char2int(month)
                day = 1
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(months=-1) != var_date[-1]:
                    missing_date = var_date[-1] + relativedelta(months=+1)
                    console.msg_error(_(
                        "Reading var {0} from file '{1}' in line: {2}\n\n"
                        "Jaziku detected missing value for date: {3}-{4}\n\n"
                        "fix it manually or run 'normalize_format {1}'")
                                      .format(variable.type, variable.file_name, time_series_file.line_num,
                                              missing_date.year,
                                              output.bimonthly_int2char(missing_date.month)))

            if env.var_[variable.type].is_trimonthly():
                month = input.trimonthly_char2int(month)
                day = 1
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(months=-1) != var_date[-1]:
                    missing_date = var_date[-1] + relativedelta(months=+1)
                    console.msg_error(_(
                        "Reading var {0} from file '{1}' in line: {2}\n\n"
                        "Jaziku detected missing value for date: {3}-{4}\n\n"
                        "fix it manually or run 'normalize_format {1}'")
                                      .format(variable.type, variable.file_name, time_series_file.line_num,
                                              missing_date.year,
                                              output.trimonthly_int2char(missing_date.month)))

            value = float(value)
            if env.globals_vars.is_valid_null(value):  # TODO: deprecated valid null
                value = float('nan')
            # set date of dependent variable from file, column 1,
            # format: yyyy-mm-dd
            var_date.append(date(year, month, day))
            # check variable if is within limits
            if validation.is_the_value_within_limits(value, variable):
                # save value
                var_data.append(value)

        except Exception as error:
            console.msg_error(_("Reading from file '{0}' in line: {1}\n\n{2}")
                              .format(variable.file_name, time_series_file.line_num, error))

        if first:
            first = False

    open_file.close()
    del time_series_file

    variable.data = var_data
    variable.date = var_date
