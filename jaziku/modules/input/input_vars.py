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

from ...utils import globals_vars
from ...utils import  console
from ...modules.input import input_validation

#==============================================================================
# INPUT DATA PROCESSING
# Read and validation dependent and independent variables from file


def read_var_D(station):
    """
    Read dependent variable from file define in station list
    and check and validate value by value.

    Return: values[] and dates[]
    """
    date_D = []
    var_D = []

    reader_csv = csv.reader(station.file_D, delimiter='\t')

    # check and validate if file D is defined as particular file with
    # particular range validation
    # below var D
    if station.range_below_D == "default":
        # validation type_D
        if station.type_D not in globals_vars.types_var_D:
            console.msg_error_line_stations(station,
                _("{0} is not valid type for dependence variable"
                  " if you defined LIMIT VAR D BELOW/ABOVE as \"default\".")
                .format(station.type_D))
    elif station.range_below_D == "none":
        station.range_below_D = None
    else:
        try:
            station.range_below_D = float(station.range_below_D.replace(',', '.'))
        except:
            console.msg_error_line_stations(station,
                (_("Problem with particular range validation for "
                   "dependent\nvariable: {0} this should be "
                   "a valid number, \"none\" or \"default\".").format(station.range_below_D,)))
        # above var D
    if station.range_above_D == "default":
        # validation type_D
        if station.type_D not in globals_vars.types_var_D:
            console.msg_error_line_stations(station,
                _("{0} is not valid type for dependence variable"
                  " if you defined LIMIT VAR D BELOW/ABOVE as \"default\".")
                .format(station.type_D))
    elif station.range_above_D == "none":
        station.range_above_D = None
    else:
        try:
            station.range_above_D = float(station.range_above_D.replace(',', '.'))
        except:
            console.msg_error_line_stations(station,
                (_("Problem with particular range validation for "
                   "dependent\nvariable: {0} this should be "
                   "a valid number, \"none\" or \"default\".").format(station.range_above_D,)))

    # reader_csv = csv.reader(fo, delimiter = '\t')
    # reader_csv.write(data.replace('\x00', ''))

    first = True
    # Read line to line file_D, validation and save var_D
    try:
        for row in reader_csv:

            # if row is null o empty, e.g. empty but with tabs or spaces
            if not row or not row[0].strip():
                continue

            # get values
            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')

            except Exception, e:
                console.msg_error(_(
                    "Reading from file \"{0}\" in line: {1}\n\n"
                    "this could be caused by wrong line or garbage "
                    "character,\nplease check manually, fix it and "
                    "run again.")
                .format(station.file_D.name, reader_csv.line_num))

            # check if var D is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.data_of_var_D = "daily"
                else:
                    station.data_of_var_D = "monthly"

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))

                if station.data_of_var_D == "daily":
                    day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                    # check if the values are continuous
                    if not first and date(year, month, day) + relativedelta(days= -1) != date_D[-1]:
                        missing_date = date_D[-1] + relativedelta(days= +1)
                        console.msg_error(_(
                            "Reading var D from file \"{0}\" in line: {1}\n\n"
                            "Jaziku detected missing value for date: {2}")
                        .format(station.file_D.name,
                            reader_csv.line_num,
                            missing_date))

                if station.data_of_var_D == "monthly":
                    day = 1
                    # check if the values are continuous
                    if not first and date(year, month, day) + relativedelta(months= -1) != date_D[-1]:
                        missing_date = date_D[-1] + relativedelta(months= +1)
                        console.msg_error(_(
                            "Reading var D from file \"{0}\" in line: {1}\n\n"
                            "Jaziku detected missing value for date: {2}-{3}")
                        .format(station.file_D.name,
                            reader_csv.line_num,
                            missing_date.year,
                            missing_date.month))
                value = float(row[1])
                # set date of dependent variable from file_D, column 1,
                # format: yyyy-mm-dd
                date_D.append(date(year, month, day))
                # set values of dependent variable
                var_D.append(input_validation.validation_var_D(station.type_D,
                    value,
                    date_D[-1],
                    station.data_of_var_D,
                    station.range_below_D,
                    station.range_above_D))

            except Exception, e:
                console.msg_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                .format(station.file_D.name, reader_csv.line_num, e))

            if first:
                first = False

    except csv.Error, e:
        # this except if when this file is created with Microsoft Office
        # in some case Microsoft Office when export put garbage in file,
        # this is invisible null byte but can't no process correctly, then
        # this exception in this case read and repair data and write in other
        # file finished with "_FIX" words.

        station.file_D.seek(0)
        file_D_fix = station.file_D.read()
        name_fix = station.file_D.name.split('.')[0] + "_FIX.txt"
        fo = open(name_fix, 'wb')
        fo.write(file_D_fix.replace('\x00', ''))
        fo.close()

        console.msg(_("\n\n > WARNING: Repairing file \"{0}\" of NULL"
                      " bytes garbage,\n   saving new file as: {1}")
                    .format(station.file_D.name, name_fix), color='yellow')

        reader_csv_fix = csv.reader(open(name_fix, 'rb'), delimiter='\t')

        first = False
        # Now read fix file
        for row in reader_csv_fix:

            # if row is null o empty, e.g. empty but with tabs or spaces
            if not row or not row[0].strip():
                continue

            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')

            except Exception, e:
                console.msg_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                                    "this could be caused by wrong line or garbage "
                                    "character,\nplease check manually, fix it and "
                                    "run again.")
                .format(station.file_D.name, reader_csv.line_num))

            # check if var D is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.data_of_var_D = "daily"
                else:
                    station.data_of_var_D = "monthly"
                first = False

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                if station.data_of_var_D == "daily":
                    day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                else:
                    day = 1
                value = float(row[1])
                # set date of dependent variable from file_D, column 1,
                # format: yyyy-mm
                date_D.append(date(year, month, day))
                # set values of dependent variable
                var_D.append(input_validation.validation_var_D(station.type_D,
                    value,
                    date_D[-1],
                    station.data_of_var_D,
                    station.range_below_D,
                    station.range_above_D))

            except Exception, e:
                console.msg_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                .format(station.file_D.name,
                    reader_csv_fix.line_num, e))

    station.var_D = var_D
    station.date_D = date_D

    return station


def read_var_I(station):
    """
    Read independent variable from file define in station list
    and check and validate value by value.

    Return: values[] and dates[]
    """
    date_I = []
    var_I = []

    # read from internal variable independent files of Jaziku,
    # check and notify if Jaziku are using the independent variable inside
    # located in plugins/var_I/
    if station.file_I == "default":
        if station.type_I in globals_vars.internal_var_I_types:
            internal_file_I_name = globals_vars.internal_var_I_files[station.type_I]
            internal_file_I_dir =\
            os.path.join(globals_vars.ROOT_DIR, 'data', 'var_I', internal_file_I_name)
            station.file_I = open(internal_file_I_dir, 'r')

            split_internal_var_I = internal_file_I_name.split(".")[0].split("_")
            console.msg(
                _("\n > You are using internal files for independent\n"
                  "   variable defined as {0} which has data from\n"
                  "   {1} to {2} and the source of data was\n"
                  "   obtained in {3}.\n"
                  "   url: {4} ...................")
                .format(split_internal_var_I[0], split_internal_var_I[1],
                    split_internal_var_I[2], ' '.join(split_internal_var_I[3::]),
                    globals_vars.internal_var_I_urls[station.type_I]), color='yellow', newline=False)

        else:
            console.msg_error(_(
                "you defined that Jaziku get data of independent variable\n"
                "from internal files but the file for the type of\n"
                "independent variable \"{0}\" don't exist").format(station.type_I))
    else:
        #noinspection PyTypeChecker
        station.file_I = open(station.file_I, 'r')

    # check and validate if file I is defined as particular file with
    # particular range validation
    # below var I
    if station.range_below_I == "default":
        # validation type_I
        if station.type_I not in globals_vars.types_var_I:
            console.msg_error_line_stations(station,
                _("{0} is not valid type for independence variable"
                  " if you defined LIMIT VAR I BELOW/ABOVE as \"default\".")
                .format(station.type_I))
    elif station.range_below_I == "none":
        station.range_below_I = None
    else:
        try:
            station.range_below_I = float(station.range_below_I.replace(',', '.'))
        except:
            console.msg_error_line_stations(station,
                (_("Problem with particular range validation for "
                   "dependent\nvariable: {0} this should be "
                   "a valid number, \"none\" or \"default\".").format(station.range_below_I,)))
        # above var I
    if station.range_above_I == "default":
        # validation type_I
        if station.type_I not in globals_vars.types_var_I:
            console.msg_error_line_stations(station,
                _("{0} is not valid type for independence variable"
                  " if you defined LIMIT VAR I BELOW/ABOVE as \"default\".")
                .format(station.type_I))
    elif station.range_above_I == "none":
        station.range_above_I = None
    else:
        try:
            station.range_above_I = float(station.range_above_I.replace(',', '.'))
        except:
            console.msg_error_line_stations(station,
                (_("Problem with particular range validation for "
                   "dependent\nvariable: {0} this should be "
                   "a valid number, \"none\" or \"default\".").format(station.range_above_I,)))

    reader_csv = csv.reader(station.file_I, delimiter='\t')
    first = True
    # Read line to line file_I, validation and save var_I
    try:
        for row in reader_csv:

            # if row is null o empty, e.g. empty but with tabs or spaces
            if not row or not row[0].strip():
                continue

            # get values
            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')
            except Exception, e:
                console.msg_error(_(
                    "Reading from file \"{0}\" in line: {1}\n\n"
                    "this could be caused by wrong line or garbage "
                    "character,\nplease check manually, fix it and "
                    "run again.")
                .format(station.file_I.name, reader_csv.line_num))

            # check if var I is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.data_of_var_I = "daily"
                else:
                    station.data_of_var_I = "monthly"

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))

                if station.data_of_var_I == "daily":
                    day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                    # check if the values are continuous
                    if not first and date(year, month, day) + relativedelta(days= -1) != date_I[-1]:
                        missing_date = date_I[-1] + relativedelta(days= +1)
                        console.msg_error(_(
                            "Reading var I from file \"{0}\" in line: {1}\n\n"
                            "Jaziku detected missing value for date: {2}")
                        .format(station.file_I.name,
                            reader_csv.line_num,
                            missing_date))

                if station.data_of_var_I == "monthly":
                    day = 1
                    # check if the values are continuous
                    if not first and date(year, month, day) + relativedelta(months= -1) != date_I[-1]:
                        missing_date = date_I[-1] + relativedelta(months= +1)
                        console.msg_error(_(
                            "Reading var I from file \"{0}\" in line: {1}\n\n"
                            "Jaziku detected missing value for date: {2}-{3}")
                        .format(station.file_I.name,
                            reader_csv.line_num,
                            missing_date.year,
                            missing_date.month))
                value = float(row[1])
                # set date of independent variable from file_I, column 1,
                # format: yyyy-mm
                date_I.append(date(year, month, day))
                # set values of independent variable
                var_I.append(input_validation.validation_var_I(station.type_I,
                    value,
                    station.range_below_I,
                    station.range_above_I))

            except Exception, e:
                console.msg_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                .format(station.file_I.name, reader_csv.line_num, e))

            if first:
                first = False

    except csv.Error, e:
        # this except if when this file is created with Microsoft Office
        # in some case Microsoft Office when export put garbage in file,
        # this is invisible null byte but can't no process correctly, then
        # this exception in this case read and repair data and write in other
        # file finished with "_FIX" words.

        station.file_I.seek(0)
        file_I_fix = station.file_I.read()
        name_fix = station.file_I.name.split('.')[0] + "_FIX.txt"
        fo = open(name_fix, 'wb')
        fo.write(file_I_fix.replace('\x00', ''))
        fo.close()

        console.msg(_("\n\n > WARNING: Repairing file \"{0}\" of NULL"
                      " bytes garbage,\n   saving new file as: {1}")
                    .format(station.file_I.name, name_fix), color='yellow')

        reader_csv_fix = csv.reader(open(name_fix, 'rb'), delimiter='\t')

        first = False
        # Now read fix file
        for row in reader_csv_fix:

            # if row is null o empty, e.g. empty but with tabs or spaces
            if not row or not row[0].strip():
                continue

            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')

            except Exception, e:
                console.msg_error(_(
                    "Reading from file \"{0}\" in line: {1}\n\n"
                    "this could be caused by wrong line or garbage "
                    "character,\nplease check manually, fix it and "
                    "run again.")
                .format(station.file_I.name, reader_csv.line_num))

            # check if var I is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.data_of_var_I = "daily"
                else:
                    station.data_of_var_I = "monthly"
                first = False

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                if station.data_of_var_I == "daily":
                    day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                else:
                    day = 1
                value = float(row[1])
                # set date of independent variable from file_I, column 1,
                # format: yyyy-mm
                date_I.append(date(year, month, day))
                # set values of independent variable
                var_I.append(input_validation.validation_var_I(station.type_I,
                    value,
                    station.range_below_I,
                    station.range_above_I))

            except Exception, e:
                console.msg_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                .format(station.file_I.name,
                    reader_csv_fix.line_num, e))

    station.var_I = var_I
    station.date_I = date_I

    return station
