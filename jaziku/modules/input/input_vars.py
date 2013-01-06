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

import os
import csv
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from pylab import size

from jaziku.utils import globals_vars
from jaziku.utils import  console
from jaziku.modules.input import input_validation

#==============================================================================
# INPUT DATA PROCESSING
# Read and validation dependent and independent variables from file


def read_var_D(station):
    """
    Read dependent variable from file define in station list
    and check and validate value by value.

    :return:
        STATION.var_D.data
        STATION.var_D.date
    """
    date_D = []
    var_D = []

    # The series accept three delimiters: spaces (' '), tabulation ('\t') or semi-colon (';')
    # this check which delimiter is using this file
    test_line = station.file_D.readline()
    if len(test_line.split(globals_vars.INPUT_CSV_DELIMITER)) >= 2:
        delimiter = globals_vars.INPUT_CSV_DELIMITER
    if len(test_line.split(' ')) >= 2:
        delimiter = ' '
    if len(test_line.split('\t')) >= 2:
        delimiter = '\t'
    if len(test_line.split(';')) >= 2:
        delimiter = ';'
    station.file_D.seek(0)

    csv_file_D = csv.reader(station.file_D, delimiter=delimiter)

    # csv_file_D = csv.reader(fo, delimiter = '\t')
    # csv_file_D.write(data.replace('\x00', ''))

    first = True
    # Read line to line file_D, validation and save var_D
    for row in csv_file_D:

        # if row is null o empty, e.g. empty but with tabs or spaces
        if not row or not row[0].strip():
            continue

        # delete empty elements in row
        row = [e for e in row if e]

        # get values
        try:
            row[0] = row[0].replace('/', '-')
            row[1] = row[1].replace(',', '.')

        except Exception, e:
            console.msg_error(_(
                "Reading from file '{0}' in line: {1}\n\n"
                "this could be caused by wrong line or garbage "
                "character,\nplease check manually, fix it and "
                "run again.")
            .format(station.file_D.name, csv_file_D.line_num), False)

        # check if var D is daily or month
        if first:
            if size(row[0].split("-")) == 3:
                station.var_D.frequency_data= "daily"
            else:
                station.var_D.frequency_data= "monthly"

        try:
            # delete garbage characters and convert format
            year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
            month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))

            if station.var_D.frequency_data== "daily":
                day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(days= -1) != date_D[-1]:
                    missing_date = date_D[-1] + relativedelta(days= +1)
                    console.msg_error(_(
                        "Reading var D from file '{0}' in line: {1}\n\n"
                        "Jaziku detected missing value for date: {2}")
                    .format(station.file_D.name,
                        csv_file_D.line_num,
                        missing_date))

            if station.var_D.frequency_data== "monthly":
                day = 1
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(months= -1) != date_D[-1]:
                    missing_date = date_D[-1] + relativedelta(months= +1)
                    console.msg_error(_(
                        "Reading var D from file '{0}' in line: {1}\n\n"
                        "Jaziku detected missing value for date: {2}-{3}")
                    .format(station.file_D.name,
                        csv_file_D.line_num,
                        missing_date.year,
                        missing_date.month))
            value = float(row[1])
            if globals_vars.is_valid_null(value):  # TODO: deprecated valid null
                value = float('nan')
            # set date of dependent variable from file_D, column 1,
            # format: yyyy-mm-dd
            date_D.append(date(year, month, day))
            # set values of dependent variable
            var_D.append(input_validation.validation_var_D(station.type_D,
                value,
                date_D[-1],
                station.var_D.frequency_data))

        except Exception, e:
            console.msg_error(_("Reading from file '{0}' in line: {1}\n\n{2}")
            .format(station.file_D.name, csv_file_D.line_num, e), False)

        if first:
            first = False

    del csv_file_D

    station.var_D.data = var_D
    station.var_D.date = date_D

    #return station


def read_var_I(station):
    """
    Read independent variable from file define in station list
    and check and validate value by value.

    :return:
        STATION.var_I.data
        STATION.var_I.date
    """
    date_I = []
    var_I = []

    # read from internal variable independent files of Jaziku, check
    # and notify if Jaziku are using the independent variable inside
    # located in plugins/var_I/
    if globals_vars.config_run["path_to_file_var_I"] == "internal":
        internal_file_I_name = globals_vars.internal_var_I_files[globals_vars.config_run["type_var_I"]]
        internal_file_I_dir = os.path.join(globals_vars.ROOT_DIR, 'data', 'var_I', internal_file_I_name)
        open_file_I = open(internal_file_I_dir, 'r')
    else:
        open_file_I = open(globals_vars.config_run["path_to_file_var_I"], 'r')

    # The series accept three delimiters: spaces (' '), tabulation ('\t') or semi-colon (';')
    # this check which delimiter is using this file
    test_line = open_file_I.readline()
    if len(test_line.split(' ')) >= 2:
        delimiter = ' '
    if len(test_line.split('\t')) >= 2:
        delimiter = '\t'
    if len(test_line.split(';')) >= 2:
        delimiter = ';'
    open_file_I.seek(0)

    csv_file_I = csv.reader(open_file_I, delimiter=delimiter)
    first = True
    # Read line to line file_I, validation and save var_I
    for row in csv_file_I:

        # if row is null o empty, e.g. empty but with tabs or spaces
        if not row or not row[0].strip():
            continue

        # delete empty elements in row
        row = [e for e in row if e]

        # get values
        try:
            row[0] = row[0].replace('/', '-')
            row[1] = row[1].replace(',', '.')
        except Exception, e:
            console.msg_error(_(
                "Reading from file '{0}' in line: {1}\n\n"
                "this could be caused by wrong line or garbage "
                "character,\nplease check manually, fix it and "
                "run again.")
            .format(open_file_I.name, csv_file_I.line_num), False)

        # check if var I is daily or month
        if first:
            if size(row[0].split("-")) == 3:
                station.var_I.frequency_data = "daily"
            else:
                station.var_I.frequency_data = "monthly"

        try:
            # delete garbage characters and convert format
            year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
            month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))

            if station.var_I.frequency_data == "daily":
                day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(days= -1) != date_I[-1]:
                    missing_date = date_I[-1] + relativedelta(days= +1)
                    console.msg_error(_(
                        "Reading var I from file '{0}' in line: {1}\n\n"
                        "Jaziku detected missing value for date: {2}")
                    .format(open_file_I.name,
                        csv_file_I.line_num,
                        missing_date))

            if station.var_I.frequency_data == "monthly":
                day = 1
                # check if the values are continuous
                if not first and date(year, month, day) + relativedelta(months= -1) != date_I[-1]:
                    missing_date = date_I[-1] + relativedelta(months= +1)
                    console.msg_error(_(
                        "Reading var I from file '{0}' in line: {1}\n\n"
                        "Jaziku detected missing value for date: {2}-{3}")
                    .format(open_file_I.name,
                        csv_file_I.line_num,
                        missing_date.year,
                        missing_date.month))
            value = float(row[1])
            if globals_vars.is_valid_null(value):  # TODO: deprecated valid null
                value = float('nan')
            # set date of independent variable from file_I, column 1,
            # format: yyyy-mm
            date_I.append(date(year, month, day))
            # set values of independent variable
            var_I.append(input_validation.validation_var_I(station.type_I, value))

        except Exception, e:
            console.msg_error(_("Reading from file '{0}' in line: {1}\n\n{2}")
            .format(open_file_I.name, csv_file_I.line_num, e), False)

        if first:
            first = False

    open_file_I.close()
    del csv_file_I

    station.var_I.data = var_I
    station.var_I.date = date_I

    #return station
