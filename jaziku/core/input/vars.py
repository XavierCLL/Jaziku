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

import os
import csv
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from pylab import size

from jaziku import env
from jaziku.core.input import validation
from jaziku.utils import  console


#==============================================================================
# INPUT DATA PROCESSING
# Read and validation dependent and independent variables from file


def read_variable(station, variable):
    """Read dependent or independent variable for get and check date and
    data from the raw file. Accept daily, monthly and bimonthly frequency
    data. The check data is a process that validate value by value within
    limits defined in runfile as 'limits_var_X'.

    For data bimonthly, this need defined inside metadata file as follow:
    FREQ:BIMONTHLY

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
              "(to runfile) or absolute.").format(station.code, station.name, variable.file_path, variable.type))

    # Check is file is not empty
    if os.path.getsize(variable.file_path) == 0:
        console.msg_error(
            _("Reading the station: {0} - {1}\n"
              "The file '{2}' is empty").format(station.code, station.name, variable.file_path))

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

    csv_file = csv.reader(open_file, delimiter=delimiter)

    # csv_file = csv.reader(fo, delimiter = '\t')
    # csv_file.write(data.replace('\x00', ''))

    first = True
    # Read line to line csv_file, validation and save variable
    for row in csv_file:

        # if row is null o empty, e.g. empty but with tabs or spaces
        if not row or not row[0].strip():
            continue

        # delete empty elements in row
        row = [e for e in row if e]

        # get values
        try:
            row[0] = row[0].replace('/', '-')
            row[1] = row[1].replace(',', '.')

        except Exception:
            console.msg_error(_(
                "Reading from file '{0}' in line: {1}\n\n"
                "this could be caused by wrong line or garbage "
                "character,\nplease check manually, fix it and "
                "run again.")
            .format(variable.file_name, csv_file.line_num), False)

        # check if variable is daily or month
        if first:
            try:
                if size(row[0].split("-")) == 3:
                    env.var_[variable.type].set_FREQUENCY_DATA("daily")
                else:
                    env.var_[variable.type].set_FREQUENCY_DATA("monthly")
            except ValueError as error:
                console.msg_error(_("Problems settings the frequency data for the station\n"
                                    "with code '{0}' and name '{1}':\n\n").format( station.code, station.name) + str(error))

        try:
            # delete garbage characters and convert format
            year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
            month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))

            if env.var_[variable.type].is_daily():
                day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(days= -1) != var_date[-1]:
                    missing_date = var_date[-1] + relativedelta(days= +1)
                    console.msg_error(_(
                        "Reading var {0} from file '{1}' in line: {2}\n\n"
                        "Jaziku detected missing value for date: {3}")
                    .format(variable.type, variable.file_name, csv_file.line_num, missing_date))

            if env.var_[variable.type].is_monthly():
                day = 1
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(months= -1) != var_date[-1]:
                    missing_date = var_date[-1] + relativedelta(months= +1)
                    console.msg_error(_(
                        "Reading var {0} from file '{1}' in line: {2}\n\n"
                        "Jaziku detected missing value for date: {3}-{4}")
                    .format(variable.type, variable.file_name, csv_file.line_num, missing_date.year, missing_date.month))

            value = float(row[1])
            if env.globals_vars.is_valid_null(value):  # TODO: deprecated valid null
                value = float('nan')
            # set date of dependent variable from file, column 1,
            # format: yyyy-mm-dd
            var_date.append(date(year, month, day))
            # check variable if is within limits
            if validation.is_the_value_within_limits(value, variable):
                # set values of dependent variable
                var_data.append(value)

        except Exception as error:
            console.msg_error(_("Reading from file '{0}' in line: {1}\n\n{2}")
            .format(variable.file_name, csv_file.line_num, error))

        if first:
            first = False

    open_file.close()
    del csv_file

    variable.data = var_data
    variable.date = var_date
