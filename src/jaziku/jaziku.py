#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#==============================================================================
# Copyright © 2011-2012 IDEAM
# Instituto de Hidrología, Meteorología y Estudios Ambientales
# Carrera 10 No. 20-30
# Bogotá, Colombia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Developers:
# Ines Sánchez Rodriguez < incsanchezro (a) gmail.com >
# Xavier Corredor Llano < xcorredorl (a) ideam.gov.co >
#==============================================================================

doc = '''
PROGRAM:
    Jaziku

ABOUT NAME:
    Jaziku is a word in huitoto mean jungle, forest.

DEVELOPERS:
    Ines Sánchez Rodriguez < incsanchezro (a) gmail.com >
    Xavier Corredor Llano < xcorredorl (a) ideam.gov.co >

DESCRIPTION:
    Jaziku is a software for the implementation of composite analysis
    metodology between the major indices of climate variability and major
    meteorological variables in puntual scale.

    According to IDEAM’s commitment to promote and guide scientiﬁc research
    about weather forecasting and climate, "Jazikü" is a program designed to
    evaluate teleconnections between meteorological variables with the main
    indices of climate variability aﬀecting climate in Colombia.

    Jaziku, follows the composite methodology analysis proposed by The
    University Corporation for Atmospheric Research (UCAR)), National Oceanic
    and Atmospheric Administration (NOAA) & U.S. Department of Commerce
    (DOC)[1][1, 2][1, 2, 3][1, 2, 3] and can produce probability scenarios
    under which it is expected precipitation or any other variable for speciﬁc
    sites or areas interpolated to behave, as a function of the probability
    values predicted for each climate variability and the history of
    involvement in the quarterly average level. Such scenarios become a
    powerful tool for decision making by the national meteorological services

    [1] National Oceanic and Atmospheric Administration (NOAA) , University
    Corporation for Atmospheric Research (UCAR)). Creating a Local Climate
    Product Using Composite Analysis - Print Version of Webcast -(En Linea).
    1997-2010:COMET Website at http://meted.ucar.edu/, 1997.
    [2] A. Leetmaa Barnston, A. G. NCEP Forecasts of the El Niño of 1997 1998
    and Its U.S. Impacts. Bull. Amer. Met. Soc, 80:1829 – 1852, 1999.
    [3] M. B. Richman Montroy, D.L. Observed Nonlinearities of Monthly
    Teleconnections between Tropical Paciﬁc Sea Surface Temperature Anomalies
    and Central and Eastern North American Precipitation. Journal of Climate,
    11:1812 – 1835, 1998.

SYNOPSIS RUN:
    jaziku [-h] -stations STATIONS [-p_below P_BELOW] [-p_normal P_NORMAL]
           [-p_above P_ABOVE] [-c] [-f] [-period PERIOD] [-ra] [-l LANG]

EXAMPLE:
    jaziku -stations station.csv -c -f

    jaziku -stations station.csv -p_below "Debajo" -p_normal "Normal" -p_above
    "Encima" -c -f -period 1980-2009 -ra -l es

Copyright © 2011-2012 IDEAM
Instituto de Hidrología, Meteorología y Estudios Ambientales
Carrera 10 No. 20-30
Bogotá, Colombia
'''

#==============================================================================
# IMPORT MODULES

import sys
import os.path
import argparse  # http://docs.python.org/py3k/library/argparse.html
import csv
from calendar import monthrange
from datetime import date
# http://labix.org/python-dateutil
# and if this required setuptools install:
# http://pypi.python.org/pypi/distribute
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import numpy as np  # http://www.scipy.org/Numpy_Example_List
from scipy import stats  # http://docs.scipy.org/doc/scipy/reference/stats.html
from Image import open as img_open
from pylab import *
import re
# color text console  #http://pypi.python.org/pypi/clint/
from clint.textui import colored

# internationalization:
import gettext
import locale
TRANSLATION_DOMAIN = "jaziku"
LOCALE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locale") # 'locale'
gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR)

# import funtions in plugins
import plugins.globals as globals
import plugins.input_validation as input_validation
import plugins.input_arg as input_arg
import plugins.contingency_test as ct
import plugins.significance_corr as sc


#==============================================================================
# PRINT FUCTIONS


def print_error(text_error):
    '''
    Print error generic function, this is called on any error occurred in
    Jaziku
    '''

    print colored.red(_('fail\n\nERROR:\n{0}\n\n').format(text_error))
    print _("For more help run program with argument: -h")
    exit()


def print_error_line_stations(station, text_error):

    print_error(_("Reading stations from file \"{0}\" in line {1}:\n")
                  .format(args.stations.name, station.line_num) +
                  ';'.join(station.line_station) + "\n\n" + text_error)


def print_number(num):
    '''
    Print number to csv file acording to accuracy and fix decimal character
    '''
    return str(round(float(num), globals.ACCURACY)).replace('.', ',')


def print_number_accuracy(num, accuracy):
    '''
    Print number to csv file acording to define accuracy and fix decimal
    character
    '''
    return str(round(float(num), accuracy)).replace('.', ',')


#==============================================================================
# INPUT DATA PROCESSING
# Read and validation dependent and independent variables from file


def read_var_D(station):
    '''
    Read dependent variable from file define in station list
    and check and validate value by value.

    Return: values[] and dates[]
    '''
    date_D = []
    var_D = []

    file_D = station.file_D
    reader_csv = csv.reader(file_D, delimiter='\t')

    # validation type_D
    if station.type_D not in input_arg.types_var_D:
        raise Exception(_("{0} is not valid type for dependence variable")
                        .format(station.type_D))

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
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_D.name, reader_csv.line_num))

            # check if var D is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.is_var_D_daily = True
                else:
                    station.is_var_D_daily = False
                first = False

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                if station.is_var_D_daily:
                    day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                else:
                    day = 1
                value = float(row[1])
                # set date of dependent variable from file_D, column 1,
                # format: yyyy-mm-dd
                date_D.append(date(year, month, day))
                # set values of dependent variable
                var_D.append(input_validation.validation_var_D(station.type_D,
                                                               value,
                                                               date_D[-1]))

            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                             .format(station.file_D.name,
                                     reader_csv.line_num, e))
    except csv.Error, e:
        # this except if when this file is created with Microsoft Office
        # in some case Microsoft Office when export put garbage in file,
        # this is invisible null byte but can't no process correctly, then
        # this exception in this case read and repair data and write in other
        # file finished with "_FIX" words.

        file_D.seek(0)
        file_D_fix = file_D.read()
        name_fix = station.file_D.name.split('.')[0] + "_FIX.txt"
        fo = open(name_fix, 'wb')
        fo.write(file_D_fix.replace('\x00', ''))
        fo.close()

        print colored.yellow(_("\n\n\tWarning: Repairing file \"{0}\" of NULL"\
                               " bytes garbage,\n\tsaving new file as: {1}")
                               .format(station.file_D.name, name_fix))

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
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_D.name, reader_csv.line_num))

            # check if var D is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.is_var_D_daily = True
                else:
                    station.is_var_D_daily = False
                first = False

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                if station.is_var_D_daily:
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
                                                               date_D[-1]))

            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                            .format(station.file_D.name,
                                    reader_csv_fix.line_num, e))

    station.var_D = var_D
    station.date_D = date_D

    return station


def read_var_I(station):
    '''
    Read independent variable from file define in station list
    and check and validate value by value.

    Return: values[] and dates[]
    '''
    date_I = []
    var_I = []

    # read from internal variable independent files of Jaziku,
    # check and notify if Jaziku are using the independent variable inside
    # located in plugins/var_I/
    if station.file_I == "default":
        if station.type_I in globals.internal_var_I_types:
            internal_file_I_name = globals.internal_var_I_files[station.type_I]
            internal_file_I_dir = \
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "plugins", "var_I", internal_file_I_name)
            file_I = open(internal_file_I_dir, 'r')

            split_internal_var_I = internal_file_I_name.split(".")[0].split("_")
            print colored.yellow(
                    _("\n   You are using internal files for independent variable\n"
                      "   defined as {0} which has data from {1} to {2} and\n"
                      "   the source of data obtained in {3}\n"
                      "   url: {4} .....................")
                      .format(split_internal_var_I[0], split_internal_var_I[1],
                              split_internal_var_I[2], ' '.join(split_internal_var_I[3::]),
                              globals.internal_var_I_urls[station.type_I])),

        else:
            print_error(_("you defined that Jaziku get data of independent variable\n"
                         "from internal files but the file for the type of\n"
                         "independent variable \"{0}\" don't exist").format(station.type_I))
    else:
        file_I = open(station.file_I, 'r')

    # check and validate if file I is defined as particular file with
    # particular range validation
    if station.range_below_I != "none" and station.range_above_I != "none":
        try:
            station.range_below_I = float(station.range_below_I.replace(',', '.'))
            station.range_above_I = float(station.range_above_I.replace(',', '.'))
        except:
            raise Exception(_("Problem with particular range validation for "
                              "independent\nvariable: {0};{1} this should be "
                              "a valid number or \"none\".").format(station.range_below_I,
                                                  station.range_above_I))
    else:
        # validation type_I
        if station.type_I not in input_arg.types_var_I:
            raise Exception(_("{0} is not valid type for independence variable")
                            .format(station.type_I))
        station.range_below_I = "None"
        station.range_above_I = "None"


    reader_csv = csv.reader(file_I, delimiter='\t')
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
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_I.name, reader_csv.line_num))

            # check if var I is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.is_var_I_daily = True
                else:
                    station.is_var_I_daily = False
                first = False

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                if station.is_var_I_daily:
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
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                            .format(file_I.name, reader_csv.line_num, e))

    except csv.Error, e:
        # this except if when this file is created with Microsoft Office
        # in some case Microsoft Office when export put garbage in file,
        # this is invisible null byte but can't no process correctly, then
        # this exception in this case read and repair data and write in other
        # file finished with "_FIX" words.

        file_I.seek(0)
        file_I_fix = file_I.read()
        name_fix = station.file_I.name.split('.')[0] + "_FIX.txt"
        fo = open(name_fix, 'wb')
        fo.write(file_I_fix.replace('\x00', ''))
        fo.close()

        print colored.yellow(_("\n\n\tWarning: Repairing file \"{0}\" of NULL"\
                               " bytes garbage,\n\tsaving new file as: {1}")
                               .format(station.file_I.name, name_fix))

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
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_I.name, reader_csv.line_num))

            # check if var I is daily or month
            if first:
                if size(row[0].split("-")) == 3:
                    station.is_var_I_daily = True
                else:
                    station.is_var_I_daily = False
                first = False

            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                if station.is_var_I_daily:
                    day = int(re.sub(r'[^\w]', '', row[0].split("-")[2]))
                else:
                    day = 1
                value = float(row[1])
                # set date of independent variable from file_I, column 1,
                # format: yyyy-mm
                date_I.append(date(year, month, day))
                # set values of independent variable
                var_I.append(input_validation.validation_var_I(station.type_I,
                                                               value))

            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                            .format(station.file_I.name,
                                    reader_csv_fix.line_num, e))

    station.var_I = var_I
    station.date_I = date_I

    return station


#==============================================================================
# UTILITIES FUCTIONS


def calculate_common_period(station):
    '''
    Calculate common period (interception) in years of dates from
    dependent and independent variable.

    Return: common_period[[  date ,  var_D ,  var_I ],... ]
    '''
    # interceptions values of date_D and date_I (python set fuctions wuau!!)
    common_date = list(set(station.date_D) & set(station.date_I))
    # sort common date
    common_date.sort()

    # initialized variable common_period
    # format list: [[  date ,  var_D ,  var_I ],... ]
    if args.period:
        if (args_period_start < common_date[0].year + 1 or
            args_period_end > common_date[-1].year - 1):
            sys.stdout.write(_("Calculating the process period .................. "))
            sys.stdout.flush()
            print_error(_("The period defined in argument {0}-{1} is outside in the\n"
                          "maximum process period for this station: {2}-{3}.")
                        .format(args_period_start, args_period_end, common_date[0].year + 1,
                                common_date[-1].year - 1))

        common_date = common_date[common_date.index(date(args_period_start - 1, 1, 1)):
                                  common_date.index(date(args_period_end + 1, 12, 1)) + 1]

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
        sys.stdout.write(_("Calculating the common period ................... "))
        sys.stdout.flush()
        if args.period:  # FIXME: realy necessary?
            print_error(_("The period defined in argument must be at least 3 "
                          "years for process."))
        else:
            print_error(_("The common period calculated {0}-{1} has not at "
                          "least 3 years.").format(common_date[0].year,
                                                   common_date[-1].year))

    return common_period


def column(matrix, i):
    '''Return column i from matrix'''

    return [row[i] for row in matrix]


def get_lag_values(station, var, lag, month, day=None):
    '''
    Return all values of var_D, var_I or date
    of specific lag, month and/or day.
    '''

    var_select = {'date': 0, 'var_D': 1, 'var_I': 2}
    lag_select = {0: station.Lag_0, 1: station.Lag_1, 2: station.Lag_2}
    temp_list = []
    for line in lag_select[lag]:
        if day:
            if month == line[0].month and day == line[0].day:
                temp_list.append(line)
        else:
            if month == line[0].month:
                temp_list.append(line)
    return [row[var_select[var]] for row in temp_list]


def mean(values):
    '''
    Return the mean from all values, ignoring valid null values.
    '''

    mean = 0
    count = 0
    for value in values:
        if int(value) not in globals.VALID_NULL:
            mean += value
            count += 1.0

    if count == 0:
        return globals.VALID_NULL[1]

    return mean / count


def check_consistent_data(station, var):
    '''
    Check if the data are consistent, this is that the amount of null value
    not exceed in 15% of the total number of values inside common period
    '''

    # temporal var initialize iter_date = start common_period + 1 year,
    # month=1, day=1
    iter_date = date(station.process_period['start'], 1, 1)  # FIXME:
    # temporal var initialize end_date = end common_period - 1 year,
    # month=12, day=31
    end_date = date(station.process_period['end'], 12, 1)  # FIXME:

    if var == "D":
        values_in_common_period = station.var_D[station.date_D.index(iter_date):station.date_D.index(end_date) + 3]
    if var == "I":
        values_in_common_period = station.var_I[station.date_I.index(iter_date) - 2:station.date_I.index(end_date) + 3]

    null_counter = 0
    for value in values_in_common_period:
        if value in globals.VALID_NULL:
            null_counter += 1

    sys.stdout.write(_("({0} null of {1}) .... ").format(null_counter, len(values_in_common_period)))
    sys.stdout.flush()

    if  null_counter / float(len(values_in_common_period)) >= 0.15:
        print_error(_("the number of null values is greater than 15% of total\n"
                    "of values inside common period, therefore, for Jaziku\n"
                    "the data are not consistent for process."))
#    return len(values_in_common_period), null_counter


def calculate_lags(station):
    '''
    Calculate and return lags 0, 1 and 2 of specific stations
    and save csv file of time series for each lag and trimester,
    the lags are calculated based in: +1 year below of start
    commond period and -1 year above of end commond period.

    Return:
    station with: Lag_0, Lag_1, Lag_2 and range_analysis_interval
    '''

    # initialized Lag_X
    # format list: [trim, [ date, mean_var_D, mean_var_I ]], ...
    Lag_0 = []
    Lag_1 = []
    Lag_2 = []

    # directories to save lags
    dir_lag = [os.path.join(station.climate_dir, _('time_series'), _('lag_0')),
               os.path.join(station.climate_dir, _('time_series'), _('lag_1')),
               os.path.join(station.climate_dir, _('time_series'), _('lag_2'))]

    # range based on analysis interval
    range_analysis_interval = None
    if station.analysis_interval_num_days == 5:
        range_analysis_interval = [1, 6, 11, 16, 21, 26]
    if station.analysis_interval_num_days == 10:
        range_analysis_interval = [1, 11, 21]
    if station.analysis_interval_num_days == 15:
        range_analysis_interval = [1, 16]

    def get_var_D_values():
        var_D_values = []
        if station.is_var_D_daily:
            # clone range for add the last day (32) for calculate interval_day_var_D
            rai_plus = list(range_analysis_interval)
            rai_plus.append(32)
            # from day to next iterator based on analysis interval
            # e.g. [0,1,2,3,4] for first iteration for 5 days
            interval_day_var_D = \
                range(day - 1, rai_plus[rai_plus.index(day) + 1] - 1)

            for iter_day in interval_day_var_D:
                now = date(iter_year, month, 1) + relativedelta(days=iter_day)
                # check if continues with the same month
                if now.month == month:
                    index_var_D = station.date_D.index(now)
                    var_D_values.append(station.var_D[index_var_D])
        else:
            # get the three values for var_D in this month
            for iter_month in range(3):
                var_D_values.append(station.var_D[station.date_D.index(
                    date(iter_year, month, 1) + relativedelta(months=iter_month))])

        return var_D_values

    def get_var_I_values():
        var_I_values = []
        if station.is_var_I_daily:  # TODO: need test!!
            # from day to next iterator based on analysis interval
            interval_day_var_I = range(day - 1 - range_analysis_interval[1] * lag,
                                       day - 1 - range_analysis_interval[1] * (lag - 1))

            for iter_day in interval_day_var_I:
                now = date(iter_year, month, 1) + relativedelta(days=iter_day)
                # check if continues with the same month
                if now.month == month:
                    index_var_I = station.date_I.index(now)
                    var_I_values.append(station.var_I[index_var_I])
        else:
            # get the three values for var_I in this month
            for iter_month in range(3):
                var_I_values.append(station.var_I[station.date_I.index(
                    date(iter_year, month, 1) + relativedelta(months=iter_month - lag))])

        return var_I_values


    if station.state_of_data == 1:

        for lag in lags:

            if not os.path.isdir(dir_lag[lag]):
                os.makedirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                csv_name = os.path.join(dir_lag[lag],
                                        _('Mean_lag_{0}_trim_{1}_{2}_{3}_{4}_{5}_'
                                          '({6}-{7}).csv')
                                        .format(lag, month, station.code,
                                                station.name, station.type_D,
                                                station.type_I,
                                                station.process_period['start'],
                                                station.process_period['end']))

                # output write file:
                # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                csv_file_write = csv.writer(open(csv_name, 'w'), delimiter=';')

                iter_year = station.process_period['start']

                # iteration for years from first-year +1 to end-year -1 inside
                # range common_period
                while iter_year <= station.process_period['end']:

                    # get values and calculate mean_var_D
                    mean_var_D = mean(get_var_D_values())

                    # get values and calculate mean_var_I
                    mean_var_I = mean(get_var_I_values())

                    # add line in list: Lag_X
                    vars()['Lag_' + str(lag)].append([date(iter_year, month, 1),
                                                     mean_var_D,
                                                     mean_var_I])

                    # add line output file csv_file_write
                    csv_file_write.writerow([str(iter_year) + "/" + str(month),
                                                 print_number(mean_var_D),
                                                 print_number(mean_var_I)])
                    # next year
                    iter_year += 1

    if station.state_of_data in [2, 3, 4]:

        for lag in lags:

            if not os.path.isdir(dir_lag[lag]):
                os.makedirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                csv_name = os.path.join(dir_lag[lag],
                                        _('Mean_lag_{0}_{1}days_month_{2}_{3}_'
                                          '{4}_{5}_{6}_({7}-{8}).csv')
                                        .format(lag, station.analysis_interval_num_days,
                                                month, station.code,
                                                station.name, station.type_D,
                                                station.type_I,
                                                station.process_period['start'],
                                                station.process_period['end']))

                # output write file:
                # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                csv_file_write = csv.writer(open(csv_name, 'w'), delimiter=';')

                #days_for_this_month = monthrange(iter_year, month)[1]

                for day in range_analysis_interval:

                    iter_year = station.process_period['start']

                    # iteration for years from first-year +1 to end-year -1 inside
                    # range common_period
                    while iter_year <= station.process_period['end']:

                        # test if day exist in month and year
                        if day > monthrange(iter_year, month)[1]:
                            iter_year += relativedelta(years= +1)
                            continue

                        # get values and calculate mean_var_D
                        mean_var_D = mean(get_var_D_values())

                        # get values and calculate mean_var_I
                        mean_var_I = mean(get_var_I_values())

                        # add line in list: Lag_X
                        vars()['Lag_' + str(lag)].append([date(iter_year, month, day),
                                                         mean_var_D,
                                                         mean_var_I])

                        # add line output file csv_file_write
                        csv_file_write.writerow([str(iter_year) + "/" + str(month)
                                                     + "/" + str(day),
                                                     print_number(mean_var_D),
                                                     print_number(mean_var_I)])
                        # next year
                        iter_year += 1

    station.range_analysis_interval = range_analysis_interval
    station.Lag_0, station.Lag_1, station.Lag_2 = Lag_0, Lag_1, Lag_2

    return station


def get_thresholds_var_I(station):
    '''
    Calculate and return threshold by below and above
    of independent variable, the type of threshold as
    defined by the user in station file, these may be:
    "default", "pNN" (percentile NN), "sdN" (standard
    deviation N) and particular value.
    '''

    # Calculate percentile "below" and "above"
    def percentiles(below, above):

        threshold_below_var_I = stats.scoreatpercentile(station.var_I_values, below)
        threshold_above_var_I = stats.scoreatpercentile(station.var_I_values, above)
        return threshold_below_var_I, threshold_above_var_I

    # thresholds by below and by above of var I by default
    def thresholds_by_default():

        # validation for Oceanic Nino Index
        def if_var_I_is_ONI():
            return -0.5, 0.5

        # validation for Index of the Southern Oscillation NOAA
        def if_var_I_is_SOI():
            return -1.2, 0.9

        # validation for Multivariate ENSO index
        def if_var_I_is_MEI():
            return percentiles(33, 66)

        # validation for Radiation wavelength Long tropical
        def if_var_I_is_OLR():
            return -1.1, 0.9

        # validation for Index of wind anomaly
        def if_var_I_is_W200():
            return percentiles(33, 66)

        # validation for Sea surface temperature
        def if_var_I_is_SST():
            return percentiles(33, 66)

        # validation for % Amazon relative humidity
        def if_var_I_is_ARH():
            return percentiles(33, 66)

        # validation for quasibienal oscillation index
        def if_var_I_is_QBO():
            return percentiles(33, 66)

        # validation for North atlantic oscillation index
        def if_var_I_is_NAO():
            return 0, 0

        # switch validation
        select_threshold_var_I = {
          "ONI": if_var_I_is_ONI,
          "SOI": if_var_I_is_SOI,
          "MEI": if_var_I_is_MEI,
          "OLR": if_var_I_is_OLR,
          "W200": if_var_I_is_W200,
          "SST": if_var_I_is_SST,
          "ARH": if_var_I_is_ARH,
          "QBO": if_var_I_is_QBO,
          "NAO": if_var_I_is_NAO
        }

        if station.type_I not in select_threshold_var_I:
            print_error("the threshoulds can't be define as \"default\" if the\n"
                        "type of independent variable is a particular value.")
        threshold_below_var_I, \
        threshold_above_var_I = select_threshold_var_I[station.type_I]()
        return threshold_below_var_I, threshold_above_var_I

    # thresholds by below and by above of var I with standard deviation
    def thresholds_with_std_deviation(below, above):

        def func_standard_deviation(values):
            avg = float((sum(values))) / len(values)
            sums = 0
            for i in values:
                sums += (i - avg) ** 2
            return (sums / (len(values) - 1)) ** 0.5

        if below not in [1, 2, 3] or above not in [1, 2, 3]:
            print_error(_("thresholds of independent variable were defined as "
                          "N standard desviation\n but are outside of range, "
                          "this values should be 1, 2 or 3:\nsd{0} sd{1}")
                        .format(below, above))
        avg = float((sum(station.var_I_values))) / len(station.var_I_values)
        std_desv = func_standard_deviation(station.var_I_values)

        return avg - below * std_desv, avg + above * std_desv

    # thresholds by below and by above of var I with particular values,
    # these values validation with type of var I
    def thresholds_with_particular_values(below, above):

        try:
            below = float(below)
            above = float(above)
        except:
            print_error(_("threshoulds could not were identified:\n{0} - {1}")
                        .format(below, above))

        if below > above:
            print_error(_("threshold below of independent variable can't be "
                          "greater than threshold above:\n{0} - {1}")
                        .format(below, above))
        try:
            threshold_below_var_I = input_validation.validation_var_I(station.type_I, below)
            threshold_above_var_I = input_validation.validation_var_I(station.type_I, above)
            return threshold_below_var_I, threshold_above_var_I
        except Exception, e:
            print_error(_("Problem with thresholds of independent "
                          "variable:\n\n{0}").format(e))


    ## now analisys threshold input in arguments
    # if are define as default
    if (station.threshold_below_var_I == "default" and
        station.threshold_above_var_I == "default"):
        return thresholds_by_default()

    # if are define as percentile
    if (''.join(list(station.threshold_below_var_I)[0:1]) == "p" and
       ''.join(list(station.threshold_above_var_I)[0:1]) == "p"):
        below = float(''.join(list(station.threshold_below_var_I)[1::]))
        above = float(''.join(list(station.threshold_above_var_I)[1::]))
        if not (0 <= below <= 100) or not (0 <= above <= 100):
            print_error(_("thresholds of independent variable were defined as "
                          "percentile\nbut are outside of range 0-100:\n{0} - {1}")
                        .format(below, above))
        if below > above:
            print_error(_("threshold below of independent variable can't be "
                          "greater than threshold above:\n{0} - {1}")
                        .format(below, above))
        return percentiles(below, above)

    # if are define as standard deviation
    if (''.join(list(station.threshold_below_var_I)[0:2]) == "sd" and
       ''.join(list(station.threshold_above_var_I)[0:2]) == "sd"):
        below = int(''.join(list(station.threshold_below_var_I)[2::]))
        above = int(''.join(list(station.threshold_above_var_I)[2::]))
        return thresholds_with_std_deviation(below, above)

    # if are define as particular values
    return thresholds_with_particular_values(station.threshold_below_var_I,
                                             station.threshold_above_var_I)


#==============================================================================
# MAIN CALCULATIONS
# Contingency table and result table


def get_contingency_table(station, lag, month, day=None):
    '''
    Calculate and return the contingency table in absolute values,
    values in percent, values to print and thresholds by below and
    above of dependent and independent variable.
    '''

    if day is None:
        # get all values of var D and var I based on this lag and month
        station.var_D_values = get_lag_values(station, 'var_D', lag, month)
        station.var_I_values = get_lag_values(station, 'var_I', lag, month)

    if day is not None:
        # get all values of var D and var I based on this lag and month
        station.var_D_values = get_lag_values(station, 'var_D', lag, month, day)
        station.var_I_values = get_lag_values(station, 'var_I', lag, month, day)

    # the thresholds of dependent variable are: percentile 33 and 66
    p33_D = stats.scoreatpercentile(station.var_D_values, 33)
    p66_D = stats.scoreatpercentile(station.var_D_values, 66)

    # calculate thresholds as defined by the user in station file
    threshold_below_var_I, threshold_above_var_I = get_thresholds_var_I(station)

    # this is to print later in contingency table
    thresholds_var_D_var_I = [print_number(p33_D), print_number(p66_D),
                              print_number(threshold_below_var_I),
                              print_number(threshold_above_var_I)]


    ## Calculating contingency table with absolute values
    contingency_table = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for index, var_I in enumerate(station.var_I_values):
        if var_I <= threshold_below_var_I:
            if station.var_D_values[index] <= p33_D:
                contingency_table[0][0] += 1
            if p33_D < station.var_D_values[index] < p66_D:
                contingency_table[0][1] += 1
            if station.var_D_values[index] >= p66_D:
                contingency_table[0][2] += 1
        if threshold_below_var_I < var_I < threshold_above_var_I:
            if station.var_D_values[index] <= p33_D:
                contingency_table[1][0] += 1
            if p33_D < station.var_D_values[index] < p66_D:
                contingency_table[1][1] += 1
            if station.var_D_values[index] >= p66_D:
                contingency_table[1][2] += 1
        if var_I >= threshold_above_var_I:
            if station.var_D_values[index] <= p33_D:
                contingency_table[2][0] += 1
            if p33_D < station.var_D_values[index] < p66_D:
                contingency_table[2][1] += 1
            if station.var_D_values[index] >= p66_D:
                contingency_table[2][2] += 1

    ## Calculating contingency table with values in percent
    tertile_size = station.size_time_series / 3.0
    contingency_table_percent = np.matrix(contingency_table) * tertile_size

    sum_per_column_percent = contingency_table_percent.sum(axis=1)

    # threshold_problem is global variable for detect problem with
    # threshold of independent variable, if a problem is detected
    # show message and print "nan" (this mean null value for
    # division by cero) in contingency tabla percent in result
    # table, jaziku continue but the graphics will not be created
    # because "nan"  character could not be calculate.
    global threshold_problem

    # if threshold by below of independent variable is wrong
    if float(sum_per_column_percent[0]) == 0 and not threshold_problem[0]:
        print colored.yellow(
            _(u'\n\nWarning:\nThe thresholds selected \"{0}\" and \"{1}\" '
              u'are not suitable for\ncompound analysis of variable \"{2}\" '
              u'with relation to \"{3}\"\ninside category \"{4}\". Therefore,'
              u' the graphics will not be created.')
              .format(station.threshold_below_var_I, station.threshold_above_var_I,
                      station.type_D, station.type_I, globals.phenomenon_below))
        threshold_problem[0] = True

    # if threshold by below or above calculating normal phenomenon of independent variable is wrong
    if float(sum_per_column_percent[1]) == 0 and not threshold_problem[1]:
        print colored.yellow(
            _(u'\n\nWarning:\nThe thresholds selected \"{0}\" and \"{1}\" '
              u'are not suitable for\ncompound analysis of variable \"{2}\" '
              u'with relation to \"{3}\"\ninside category \"{4}\". Therefore,'
              u' the graphics will not be created.')
              .format(station.threshold_below_var_I, station.threshold_above_var_I,
                      station.type_D, station.type_I, globals.phenomenon_normal))
        threshold_problem[1] = True

    # if threshold by above of independent variable is wrong
    if float(sum_per_column_percent[2]) == 0 and not threshold_problem[2]:
        print colored.yellow(
            _(u'\n\nWarning:\nThe thresholds selected \"{0}\" and \"{1}\" '
              u'are not suitable for\ncompound analysis of variable \"{2}\" '
              u'with relation to \"{3}\"\ninside category \"{4}\". Therefore,'
              u' the graphics will not be created.')
              .format(station.threshold_below_var_I, station.threshold_above_var_I,
                      station.type_D, station.type_I, globals.phenomenon_above))
        threshold_problem[2] = True

    try:
        # not shows error if there are any problem with threshold
        sys.stderr = open(os.devnull, 'w')
        # Calculating contingency table percent
        contingency_table_percent = \
            [(contingency_table_percent[0] * 100 / float(sum_per_column_percent[0])).tolist()[0],
             (contingency_table_percent[1] * 100 / float(sum_per_column_percent[1])).tolist()[0],
             (contingency_table_percent[2] * 100 / float(sum_per_column_percent[2])).tolist()[0]]
    except:
        pass

    # Contingency table percent to print in result table and graphics (reduce the number of decimals)
    contingency_table_percent_print = []
    for row in contingency_table_percent:
        contingency_table_percent_print.append([print_number_accuracy(row[0], 1),
                                                print_number_accuracy(row[1], 1),
                                                print_number_accuracy(row[2], 1)])

    return contingency_table, contingency_table_percent, \
           contingency_table_percent_print, thresholds_var_D_var_I


def contingency_table(station):
    '''
    Print the contingency table for each trimester and each lag
    '''

    # [lag][month][phenomenon][data(0,1,2)]
    # [lag][month][day][phenomenon][data(0,1,2)]
    contingencies_tables_percent = []

    for lag in lags:

        tmp_month_list = []
        # all months in year 1->12
        for month in range(1, 13):
            if station.state_of_data in [1, 3]:
                contingency_table, \
                contingency_table_percent, \
                contingency_table_percent_print, \
                thresholds_var_D_var_I = get_contingency_table(station, lag, month)

                tmp_month_list.append(contingency_table_percent)

            if station.state_of_data in [2, 4]:
                tmp_day_list = []
                for day in station.range_analysis_interval:
                    contingency_table, \
                    contingency_table_percent, \
                    contingency_table_percent_print, \
                    thresholds_var_D_var_I = get_contingency_table(station, lag,
                                                                   month, day)
                    tmp_day_list.append(contingency_table_percent)

                tmp_month_list.append(tmp_day_list)

        contingencies_tables_percent.append(tmp_month_list)

    return contingencies_tables_percent


def result_table_CA(station):
    '''
    Calculate and print the result table for composite analisys (CA) in csv
    file, this file contein several variables of previous calculations and
    different tests.
    '''

    pearson_list = []
    is_sig_risk_analysis = []

    def result_table_CA_main_process():
        # test:
        # is significance risk analysis?

        pearson = None
        is_sig_risk_analysis_list = []

        contingency_table_matrix = np.matrix(contingency_table)
        sum_per_row = contingency_table_matrix.sum(axis=0).tolist()[0]
        sum_per_column = contingency_table_matrix.sum(axis=1).tolist()
        sum_contingency_table = contingency_table_matrix.sum()

        for c, column_table in enumerate(contingency_table):
            for r, Xi in enumerate(column_table):
                M = sum_per_column[c]
                n = sum_per_row[r]
                N = sum_contingency_table
                X = stats.hypergeom.cdf(Xi, N, M, n)
                Y = stats.hypergeom.sf(Xi, N, M, n, loc=1)
                if X <= 0.1 or Y <= 0.1:
                    is_sig_risk_analysis_list.append(_('yes'))
                else:
                    is_sig_risk_analysis_list.append(_('no'))

        # get values of var D and I from this lag and month
        var_D_values = get_lag_values(station, 'var_D', lag, month)

        var_I_values = get_lag_values(station, 'var_I', lag, month)

        # calculate pearson correlation of var_D and var_I
        pearson = stats.pearsonr(var_D_values, var_I_values)[0]

        # significance correlation
        singr, T_test, t_crit = \
            sc.corrtest(rho=0, r=pearson, n=len(station.common_period) + 1,
                        alpha=0.05, side=0)

        # contingency test
        Observed, Expected, test_stat, crit_value, df, p_value, alpha = \
            ct.contingency_test(contingency_table, None, 0.9, -1)

        # calculate the correlation of contingency table
        chi_cdf = 1 - p_value
        corr_CT = ((chi_cdf ** 2) / (station.size_time_series * 2.0)) ** (0.5)

        # test:
        # Is significant the contingency table?
        if test_stat > crit_value:
            is_significant_CT = _('yes')
        else:
            is_significant_CT = _('no')

        # test:
        # Is significant the singr variable?
        if (1 - singr) >= 0.05:
            is_significant_singr = _('yes')
        else:
            is_significant_singr = _('no')

        #===============================================================================
        # result table (csv file), add one line of this trimester and lag

        # add new line in csv_file_write
        csv_result_table.writerow([
             var_D_text, var_I_text,
             print_number(pearson), print_number(singr), is_significant_singr,
             thresholds_var_D_var_I[0], thresholds_var_D_var_I[1],
             thresholds_var_D_var_I[2], thresholds_var_D_var_I[3],
             contingency_table[0][0], contingency_table[0][1],
             contingency_table[0][2], contingency_table[1][0],
             contingency_table[1][1], contingency_table[1][2],
             contingency_table[2][0], contingency_table[2][1],
             contingency_table[2][2],
             contingency_table_percent_print[0][0],
             contingency_table_percent_print[0][1],
             contingency_table_percent_print[0][2],
             contingency_table_percent_print[1][0],
             contingency_table_percent_print[1][1],
             contingency_table_percent_print[1][2],
             contingency_table_percent_print[2][0],
             contingency_table_percent_print[2][1],
             contingency_table_percent_print[2][2],
             is_sig_risk_analysis_list[0], is_sig_risk_analysis_list[1],
             is_sig_risk_analysis_list[2], is_sig_risk_analysis_list[3],
             is_sig_risk_analysis_list[4], is_sig_risk_analysis_list[5],
             is_sig_risk_analysis_list[6], is_sig_risk_analysis_list[7],
             is_sig_risk_analysis_list[8],
             print_number(test_stat), print_number(crit_value),
             is_significant_CT, print_number_accuracy(corr_CT, 4)])

        return pearson, is_sig_risk_analysis_list

    for lag in lags:

        # dir and name to save the result table
        csv_name = \
        os.path.join(station.climate_dir, _('Result_Table_CA_lag_{0}_{1}_{2}_{3}_{4}_({5}-{6}).csv')
                    .format(lag, station.name, station.code, station.type_D, station.type_I,
                            station.process_period['start'], station.process_period['end']))

        csv_result_table = csv.writer(open(csv_name, 'w'), delimiter=';')

        # print headers in result table
        csv_result_table.writerow([
             _('var_D'), _('var_I'), _('Pearson'), _('Sign Pearson'),
             _('Is sign \'Sign Pearson\'?'), _('threshold below (var D)'),
             _('threshold above (var D)'), _('threshold below (var I)'),
             _('threshold above (var I)'), _('Contingency Table (CT)'),
             '', '', '', '', '', '', '', '', _('Contingency Table in %'),
             '', '', '', '', '', '', '', '', _('is sig risk analysis?'),
             '', '', '', '', '', '', '', '', _('Test Stat - Chi2'),
             _('Crit Value - Chi2'), _('Is sig CT?'), _('Correl CT')])

        # print division line between lags
        csv_result_table.writerow([
             '', '', '', '', '', '', '', '', '',
             globals.phenomenon_below, '', '',
             globals.phenomenon_normal, '', '',
             globals.phenomenon_above, '', '',
             globals.phenomenon_below, '', '',
             globals.phenomenon_normal, '', '',
             globals.phenomenon_above])

        csv_result_table.writerow([
             '', '', '', '', '', '', '', '', '',
             _('var D below'), _('var D normal'), _('var D above'),
             _('var D below'), _('var D normal'), _('var D above'),
             _('var D below'), _('var D normal'), _('var D above'),
             _('var D below'), _('var D normal'), _('var D above'),
             _('var D below'), _('var D normal'), _('var D above'),
             _('var D below'), _('var D normal'), _('var D above')])

        pearson_list_month = []
        is_sig_risk_analysis_month = []

        # all months in year 1->12
        for month in range(1, 13):

            if station.state_of_data in [1, 3]:
                # get the contingency tables and thresholds
                contingency_table, \
                contingency_table_percent, \
                contingency_table_percent_print, \
                thresholds_var_D_var_I = get_contingency_table(station, lag, month)

                # for print text date in result table
                var_D_text = trim_text[month - 1]
                var_I_text = trim_text[month - 1 - lag]

                pearson, is_sig_risk_analysis_list = result_table_CA_main_process()  # <-

                pearson_list_month.append(pearson)
                is_sig_risk_analysis_month.append(is_sig_risk_analysis_list)

            if station.state_of_data in [2, 4]:
                pearson_list_day = []
                is_sig_risk_analysis_list_day = []
                for day in station.range_analysis_interval:
                    # get the contingency tables and thresholds
                    contingency_table, \
                    contingency_table_percent, \
                    contingency_table_percent_print, \
                    thresholds_var_D_var_I = get_contingency_table(station, lag, month, day)

                    # this is for calculate date for print in result table
                    # this depend on range analysis interval and lags (var_I)
                    # the year no matter
                    date_now = date(2000, month, day)

                    # for print text date in result table
                    var_D_text = month_text[date_now.month - 1] + " " + str(day)
                    var_I_text = month_text[(date_now - relativedelta(days=(station.range_analysis_interval[1] - 1) * lag)).month - 1] + \
                        " " + str(station.range_analysis_interval[station.range_analysis_interval.index(day) - lag])

                    pearson, is_sig_risk_analysis_list = result_table_CA_main_process()  # <-

                    pearson_list_day.append(pearson)
                    is_sig_risk_analysis_list_day.append(is_sig_risk_analysis_list)

                pearson_list_month.append(pearson_list_day)
                is_sig_risk_analysis_month.append(is_sig_risk_analysis_list_day)



        pearson_list.append(pearson_list_month)
        is_sig_risk_analysis.append(is_sig_risk_analysis_month)

    station.pearson_list = pearson_list
    station.is_sig_risk_analysis = is_sig_risk_analysis

    return station


#===============================================================================
# GRAPHICS
# Generate bart graphics and mosaic for climate of pies for forecasting
# http://matplotlib.sourceforge.net/api/pyplot_api.html


def graphics_climate(station):
    '''
    Generate bart graphics and mosaic of probability for below, normal and
    above for independece variable for the composite analisys.
    '''

    # main directory for save graphics
    graphics_dir = _('graphics')

    # directory for save composite analisys graphics
    graphics_dir_ca = \
        os.path.join(station.climate_dir, graphics_dir, _('composite_analisys'))

    # create dir
    if not os.path.isdir(graphics_dir_ca):
        os.makedirs(graphics_dir_ca)

    def create_graphic():
        ## graphics options for plot:
        # the x locations for the groups
        ind = np.array([0, 0.8, 1.6])
        # the width of the bars
        width = 0.2

        plt.figure()

        # graphics title
        plt.title(unicode(_('Composite analisys - {0} ({1})\n{2} - {3} - '
                            'lag {6} - {7} - ({4}-{5})')
                            .format(station.name, station.code, station.type_I,
                                    station.type_D, station.process_period['start'],
                                    station.process_period['end'], lag,
                                    title_period), 'utf-8'))

        # label for axis Y 
        plt.ylabel(_('probability (%)'))
        #  adjust the max leaving min unchanged in Y
        plt.ylim(ymin=0, ymax=100)
        #  adjust the max leaving min unchanged in X
        plt.xlim(xmin= -0.1, xmax=2.3)
        # plt.xticks([0.3, 1.1, 1.9], ('var Ind Below', 'var Ind Normal', 'var Ind Above'),)
        plt.xticks([])
        # colors for paint bars and labels: below, normal , above
        colours = ['#DD4620', '#62AD29', '#6087F1']
        # assigning values for plot:
        var_D_below = plt.bar(ind, column(contingency_table_percent, 0),
                              width, color=colours[0])
        var_D_normal = plt.bar(ind + width, column(contingency_table_percent, 1),
                               width, color=colours[1])
        var_D_above = plt.bar(ind + 2 * width, column(contingency_table_percent, 2),
                              width, color=colours[2])

        # assing value for each bart
        def autolabel(rects):
            # attach some text labels
            temp = []
            for rect in rects:
                temp.append(rect.get_height())
            temp.sort(reverse=True)
            max_heigth = temp[0]

            for rect in rects:
                height = rect.get_height()
                plt.text(rect.get_x() + rect.get_width() / 2.0, 0.015 * max_heigth +
                         height, round(height, 1), ha='center', va='bottom')

        autolabel(var_D_below)
        autolabel(var_D_normal)
        autolabel(var_D_above)

        plt.subplots_adjust(bottom=0.15, left=0.22, right=0.97)
        # plt.legend((var_D_below[0], var_D_normal[0], var_D_above[0]), 
        #            ('var Dep Below', 'var Dep Normal', 'var Dep Above'),
        #             shadow = True, fancybox = True)

        # table in graphic
        colLabels = (globals.phenomenon_below, globals.phenomenon_normal,
                     globals.phenomenon_above)

        rowLabels = [_('var D below'), _('var D normal'), _('var D above')]

        contingency_table_percent_graph = [column(contingency_table_percent_print, 0),
                                           column(contingency_table_percent_print, 1),
                                           column(contingency_table_percent_print, 2)]

        # Add a table at the bottom of the axes
        plt.table(cellText=contingency_table_percent_graph,
                             rowLabels=rowLabels, rowColours=colours,
                             colLabels=colLabels, loc='bottom')
        ## Save image
        plt.subplot(111)
        image_dir_save = \
            os.path.join(graphics_dir_ca, _('lag_{0}').format(lag),
                         _('ca_lag_{0}_{1}_{2}_{3}_{4}_{5}_({6}-{7}).png')
                         .format(lag, filename_period, station.code, station.name, station.type_D,
                                 station.type_I, station.process_period['start'], station.process_period['end']))

        plt.savefig(image_dir_save, dpi=75)
        plt.clf()

        # save dir image for mosaic
        image_open_list.append(img_open(image_dir_save))

    for lag in lags:

        # create dir for lag
        if not os.path.isdir(os.path.join(graphics_dir_ca, _('lag_{0}').format(lag))):
            os.makedirs(os.path.join(graphics_dir_ca, _('lag_{0}').format(lag)))

        image_open_list = list()

        # all months in year 1->12
        for month in range(1, 13):

            if station.state_of_data in [1, 3]:
                contingency_table, \
                contingency_table_percent, \
                contingency_table_percent_print, \
                thresholds_var_D_var_I = get_contingency_table(station, lag, month)

                title_period = "trim {0} ({1})".format(month, trim_text[month - 1])
                filename_period = "trim_{0}".format(month)
                create_graphic()

            if station.state_of_data in [2, 4]:

                for day in station.range_analysis_interval:

                    contingency_table, \
                    contingency_table_percent, \
                    contingency_table_percent_print, \
                    thresholds_var_D_var_I = get_contingency_table(station, lag, month, day)

                    title_period = month_text[month - 1] + " " + str(day)
                    filename_period = month_text[month - 1] + "_" + str(day)

                    create_graphic()


        ## create mosaic
        # definition height and width of individual image
        image_height = 450
        image_width = 600
        mosaic_dir_save = \
            os.path.join(graphics_dir_ca, _('mosaic_lag_{0}_{1}_{2}_{3}_{4}_({5}-{6}).png')
                        .format(lag, station.code, station.name, station.type_D, station.type_I,
                                station.process_period['start'], station.process_period['end']))

        if station.state_of_data in [1, 3]:
            # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
            mosaic_plt = plt.figure(figsize=((image_width * 3) / 100, (image_height * 4) / 100))
            mosaic_plt.savefig(mosaic_dir_save, dpi=100)
            mosaic = img_open(mosaic_dir_save)
            i = 0
            # add image in mosaic based on trimester, vertical(v) and horizontal(h)
            for v in range(4):
                for h in range(3):
                    mosaic.paste(image_open_list[i], (image_width * h, image_height * v))
                    i += 1

        if station.state_of_data in [2, 4]:
            # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
            mosaic_plt = plt.figure(figsize=((image_width * len(station.range_analysis_interval))
                                / 100, (image_height * 12) / 100))
            mosaic_plt.savefig(mosaic_dir_save, dpi=100)
            mosaic = img_open(mosaic_dir_save)
            i = 0
            # add image in mosaic based on months(m) and days(d)
            for m in range(12):
                for d in range(len(station.range_analysis_interval)):
                    mosaic.paste(image_open_list[i], (image_width * d, image_height * m))
                    i += 1

        mosaic.save(mosaic_dir_save)
        del mosaic
        plt.clf()
        #del image_open_list #TODO:


def graphics_forecasting(station):
    '''
    Generate pie graphics and mosaic of probability for below, normal and
    above for independece variable for the composite analisys.
    '''

    # main directory for save graphics
    graphics_dir = _('graphics')

    # directory for save composite analisys graphics
    graphics_dir_corr = \
        os.path.join(station.climate_dir, graphics_dir, _('composite_analisys'))

    # create dir
    if not os.path.isdir(graphics_dir_corr):
        os.makedirs(graphics_dir_corr)

    image_open_list = []

    for lag in lags:

        if station.state_of_data in [1, 3]:
            forecasting_month = station.forecasting_date
            title_date_graphic = _("trim {0} ({1})").format(station.forecasting_date,
                                                       trim_text[forecasting_month - 1])
            filename_date_graphic = _("trim_{0}").format(forecasting_month)

        if station.state_of_data in [2, 4]:
            forecasting_month = station.forecasting_date[0]
            forecasting_day = station.forecasting_date[1]
            title_date_graphic = "{0} {1}".format(month_text[forecasting_month - 1],
                                                     forecasting_day)
            filename_date_graphic = "{0}_{1}".format(month_text[forecasting_month - 1],
                                                     forecasting_day)

        ## Options for graphics pie
        # make a square figure and axes
        plt.figure(figsize=(5, 5))
        # colors for paint pie: below, normal , above
        colours = ['#DD4620', '#62AD29', '#6087F1']

        labels = (_('Decrease'), _('Normal'), _('Exceed'))
        values_pie = [station.prob_decrease_var_D[lag],
                      station.prob_normal_var_D[lag],
                      station.prob_exceed_var_D[lag]]
        explode = (0.03, 0.03, 0.03)

        # assing value for piece of pie
        def autopct_funt(pct):
            total = sum(values_pie)
            val = pct * total / 100.0
            return '{p:1.1f}%\n({v:1.2f})'.format(p=pct, v=val)

        plt.pie(values_pie, colors=colours, explode=explode, labels=labels,
                autopct='%1.1f%%', shadow=True)  #'%1.1f%%'

        plt.title(unicode(_('Probability forecasted of {0} - {1}\n{2} - lag {3} - {4} - ({5}-{6})')
                          .format(station.type_D, station.name, station.type_I, lag, title_date_graphic,
                          station.process_period['start'], station.process_period['end']),
                          'utf-8'), fontsize=13)

        ## Save image
        # plt.subplot(111)
        image_dir_save = \
            os.path.join(station.forecasting_dir, _('prob_of_{0}_lag_{1}_{2}_({3}-{4}).png')
                         .format(station.type_D, lag, filename_date_graphic,
                                 station.process_period['start'], station.process_period['end']))
        plt.savefig(image_dir_save, dpi=75)
        plt.clf()

        # save dir image for mosaic
        image_open_list.append(img_open(image_dir_save))

    ## Create mosaic
    # definition height and width of individual image
    # image_height = 375
    image_width = 375
    mosaic_dir_save = \
        os.path.join(station.forecasting_dir, _('mosaic_prob_of_{0}_{1}_({3}-{4}).png')
                     .format(station.type_D, lag, filename_date_graphic,
                             station.process_period['start'], station.process_period['end']))
    # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
    plt.figure(figsize=(11.25, 3.75))  # http://www.classical-webdesigns.co.uk/resources/pixelinchconvert.html
    plt.savefig(mosaic_dir_save, dpi=100)
    mosaic = img_open(mosaic_dir_save)
    mosaic.paste(image_open_list[0], (0, 0))
    mosaic.paste(image_open_list[1], (image_width, 0))
    mosaic.paste(image_open_list[2], (image_width * 2, 0))
    mosaic.save(mosaic_dir_save)
    plt.clf()


#==============================================================================
# PLOTTING MAPS
# create file for ploting
# TODO: generate maps from previus file, plot all index from all stations


def maps_climate(station):
    '''
    Create maps data csv file for ploting for each trimester, phenomenon and lag,
    each file contain all stations processed.
    '''

    # -------------------------------------------------------------------------
    # create maps plots files for climate process, only once

    if globals.maps_files_climate[station.analysis_interval] is None:

        # create and define csv output file for maps climate
        phenomenon = {0:globals.phenomenon_below, 1:globals.phenomenon_normal, 2:globals.phenomenon_above}
        globals.maps_files_climate[station.analysis_interval] = [] # [lag][month][phenomenon]

        # define maps data files and directories
        for lag in lags:

            maps_dir = os.path.join(climate_dir, _('maps'))
            maps_data_lag = os.path.join(maps_dir, _('maps_data'),
                                         station.analysis_interval,
                                         _('lag_{0}').format(lag))

            if not os.path.isdir(maps_data_lag):
                os.makedirs(maps_data_lag)
            # all months in year 1->12
            month_list = []
            for month in range(1, 13):
                if station.state_of_data in [1, 3]:
                    categories_list = []
                    for category in phenomenon:
                        maps_data_phenom = os.path.join(maps_data_lag, phenomenon[category])

                        if not os.path.isdir(maps_data_phenom):
                            os.makedirs(maps_data_phenom)

                        csv_name = \
                            os.path.join(maps_data_phenom, _(u'Map_Data_lag_{0}_trim_{1}_{2}.csv')
                                         .format(lag, month, phenomenon[category]))
                        csv_file = csv.writer(open(csv_name, 'w'), delimiter=';')
                        csv_file.writerow([_('code'), _('lat'), _('lon'), _('pearson'),
                                           _('var_below'), _('var_normal'), _('var_above'),
                                           _('p_index'), _('sum')])
                        categories_list.append(csv_file)

                    month_list.append(categories_list)
                if station.state_of_data in [2, 4]:
                    day_list = []
                    for day in station.range_analysis_interval:
                        categories_list = []
                        for category in phenomenon:
                            maps_data_phenom = os.path.join(maps_data_lag, phenomenon[category])

                            if not os.path.isdir(maps_data_phenom):
                                os.makedirs(maps_data_phenom)

                            csv_name = \
                                os.path.join(maps_data_phenom, _(u'Map_Data_lag_{0}_{1}_{2}.csv')
                                             .format(lag,
                                                     month_text[month - 1] + "_" + str(day),
                                                     phenomenon[category]))
                            csv_file = csv.writer(open(csv_name, 'w'), delimiter=';')
                            csv_file.writerow([_('code'), _('lat'), _('lon'), _('pearson'),
                                               _('var_below'), _('var_normal'), _('var_above'),
                                               _('p_index'), _('sum')])
                            categories_list.append(csv_file)
                        day_list.append(categories_list)

                    month_list.append(day_list)

            globals.maps_files_climate[station.analysis_interval].append(month_list)

    def calculate_index():
        # select index
        if var_below > var_normal:
            if var_below > var_above:
                return -var_below
            elif var_above > var_normal:
                return var_above
            elif var_below == var_normal:
                return 0
            else:
                return var_below
        else:
            if var_normal == var_above:
                return 0
            elif var_normal > var_above:
                return 0
            else:
                return var_above

    for lag in lags:

        # all months in year 1->12
        for month in range(1, 13):

            if station.state_of_data in [1, 3]:
                for phenomenon in [0, 1, 2]:
                    var_below = station.contingencies_tables_percent[lag][month - 1][phenomenon][0]
                    var_normal = station.contingencies_tables_percent[lag][month - 1][phenomenon][1]
                    var_above = station.contingencies_tables_percent[lag][month - 1][phenomenon][2]

                    p_index = calculate_index()

                    globals.maps_files_climate[lag][month - 1][phenomenon]\
                        .writerow([station.code, station.lat, station.lon,
                                   print_number(station.pearson_list[lag][month - 1]),
                                   print_number(var_below), print_number(var_normal),
                                   print_number(var_above), print_number(p_index),
                                   print_number(sum([float(var_below),
                                                     float(var_normal),
                                                     float(var_above)]))])

            if station.state_of_data in [2, 4]:
                for day in range(len(station.range_analysis_interval)):
                    for phenomenon in [0, 1, 2]:
                        var_below = station.contingencies_tables_percent[lag][month - 1][day][phenomenon][0]
                        var_normal = station.contingencies_tables_percent[lag][month - 1][day][phenomenon][1]
                        var_above = station.contingencies_tables_percent[lag][month - 1][day][phenomenon][2]

                        p_index = calculate_index()

                        globals.maps_files_climate[station.analysis_interval][lag][month - 1][day][phenomenon]\
                            .writerow([station.code, station.lat, station.lon,
                                       print_number(station.pearson_list[lag][month - 1][day]),
                                       print_number(var_below), print_number(var_normal),
                                       print_number(var_above), print_number(p_index),
                                       print_number(sum([float(var_below),
                                                         float(var_normal),
                                                         float(var_above)]))])


def maps_forecasting(station):
    '''
    Create maps data csv file for ploting for each trimester, phenomenon and
    lag, each file contain all stations processed.
    '''
    # -------------------------------------------------------------------------
    # create maps plots files for forecasting process, only once

    if globals.maps_files_forecasting[station.analysis_interval] is None:
        globals.maps_files_forecasting[station.analysis_interval] = []
        # define maps data files and directories
        for lag in lags:

                maps_dir = os.path.join(forecasting_dir, _('maps'),
                                        _('maps_data'),
                                        station.analysis_interval)

                if not os.path.isdir(maps_dir):
                    os.makedirs(maps_dir)

                csv_name = os.path.join(maps_dir, _(u'Map_Data_lag_{0}.csv')
                                        .format(lag))
                csv_file = csv.writer(open(csv_name, 'w'), delimiter=';')
                csv_file.writerow([_('code'), _('lat'), _('lon'),
                                   _('forecasting_date'), _('prob_decrease_var_D'),
                                   _('prob_normal_var_D'), _('prob_exceed_var_D'),
                                   _('index'), _('sum')])

                globals.maps_files_forecasting[station.analysis_interval].append(csv_file)


    def calculate_index():
        # select index
        if station.prob_decrease_var_D[lag] > station.prob_normal_var_D[lag]:
            if station.prob_decrease_var_D[lag] > station.prob_exceed_var_D[lag]:
                p_index = -station.prob_decrease_var_D[lag]
            elif station.prob_exceed_var_D[lag] > station.prob_normal_var_D[lag]:
                p_index = station.prob_exceed_var_D[lag]
            elif station.prob_decrease_var_D[lag] == station.prob_normal_var_D[lag]:
                p_index = 0
            else:
                p_index = station.prob_decrease_var_D[lag]
        else:
            if station.prob_normal_var_D[lag] == station.prob_exceed_var_D[lag]:
                p_index = 0
            elif station.prob_normal_var_D[lag] > station.prob_exceed_var_D[lag]:
                p_index = 0
            else:
                p_index = station.prob_exceed_var_D[lag]

        return p_index

    # select text for forecasting date
    if station.state_of_data in [1, 3]:
        forecasting_date_text = month_text[station.forecasting_date - 1]
    if station.state_of_data in [2, 4]:
        month = station.forecasting_date[0]
        day = station.forecasting_date[1]
        forecasting_date_text = month_text[month - 1] + "-" + str(day)


    for lag in lags:

        p_index = calculate_index()

        globals.maps_files_forecasting[station.analysis_interval][lag]\
            .writerow([station.code,
                       print_number_accuracy(station.lat, 4),
                       print_number_accuracy(station.lon, 4),
                       forecasting_date_text,
                       print_number(station.prob_decrease_var_D[lag]),
                       print_number(station.prob_normal_var_D[lag]),
                       print_number(station.prob_exceed_var_D[lag]),
                       print_number(p_index),
                       print_number(sum([station.prob_decrease_var_D[lag],
                                         station.prob_normal_var_D[lag],
                                         station.prob_exceed_var_D[lag]]))])


#==============================================================================
# PRE-PROCESS: READ, VALIDATED AND CHECK DATA

def pre_process(station):
    '''
    Read var I and varD from files, validated and check consistent
    '''

    # -------------------------------------------------------------------------
    # Reading the variables from files and check based on range validation

    # var D
    sys.stdout.write(_("Read and check(range validation) var D .......... "))
    sys.stdout.flush()
    station = read_var_D(station)  # <--
    print colored.green(_("done"))

    if station.is_var_D_daily:
        print colored.cyan(_(" ↳the dependent variable has data daily"))
    else:
        print colored.cyan(_(" ↳the dependent variable has data monthly"))

    # var I
    sys.stdout.write(_("Read and check(range validation) var I .......... "))
    sys.stdout.flush()
    station = read_var_I(station)  # <--
    print colored.green(_("done"))

    if station.is_var_I_daily:
        print colored.cyan(_(" ↳the independent variable has data daily"))
    else:
        print colored.cyan(_(" ↳the independent variable has data monthly"))

    # -------------------------------------------------------------------------
    # Calculating common period and process period
    station.common_period = calculate_common_period(station)

    station.process_period = {'start': station.common_period[0][0].year + 1,
                              'end': station.common_period[-1][0].year - 1}

    # -------------------------------------------------------------------------
    # check if the data are consistent for var D
    sys.stdout.write(_("Check if var_D are consistent "))
    sys.stdout.flush()

    check_consistent_data(station, "D")

    print colored.green(_("done"))

    # -------------------------------------------------------------------------
    # check if the data are consistent for var I
    sys.stdout.write(_("Check if var_I are consistent "))
    sys.stdout.flush()

    check_consistent_data(station, "I")

    print colored.green(_("done"))

    return station

#==============================================================================
# PROCESS:


def process(station):


    # -------------------------------------------------------------------------
    # State of the data for process, calculate and write output based on type
    # of data (daily or monthly) of dependent and independent variable
    #
    # | state |  var D  |  var I  |
    # |   1   | monthly | monthly |
    # |   2   |  daily  | monthly |
    # |   3   | monthly |  daily  |
    # |   4   |  daily  |  daily  |

    if not station.is_var_D_daily and not station.is_var_I_daily:
        station.state_of_data = 1
    if station.is_var_D_daily and not station.is_var_I_daily:
        station.state_of_data = 2
    if not station.is_var_D_daily and station.is_var_I_daily:
        station.state_of_data = 3
    if station.is_var_D_daily and station.is_var_I_daily:
        station.state_of_data = 4

    if station.state_of_data in [1, 3]:
        print colored.cyan(_(" Results will be made by trimester"))
    if station.state_of_data in [2, 4]:
        print colored.cyan(_(" Results will be made every {} days").format(station.analysis_interval_num_days))

    # run process (climate, forecasting) from input arguments
    if not args.climate and not args.forecasting:
        print_error(_("Neither process (climate, forecasting) were executed, "
                      "\nplease enable this process in arguments: \n'-c, "
                      "--climate' for climate and/or '-f, --forecasting' "
                      "for forecasting."))
    if args.climate:
        station = climate(station)

    if args.forecasting:
        # TODO: run forecasting without climate
        if not args.climate:
            print_error(_("sorry, Jaziku can't run forecasting process "
                          "without climate, this issue has not been implemented "
                          "yet, \nplease run again with the option \"-c\""))
        forecasting(station)


    return station

#==============================================================================
# CLIMATE AND FORECASTING MAIN PROCESS


def climate(station):
    '''
    Main process for climate
    '''

    # console message
    sys.stdout.write(_("Processing climate"))
    sys.stdout.flush()

    # create directory for output files
    if not os.path.isdir(climate_dir):
        os.makedirs(climate_dir)

    station.climate_dir = \
        os.path.join(climate_dir, station.code + '_' + station.name)   # 'results'
    if not os.path.isdir(station.climate_dir):
        os.makedirs(station.climate_dir)

    sys.stdout.write(" ({0}-{1}) .................. ".format(station.process_period['start'],
                                                   station.process_period['end']))
    sys.stdout.flush()

    station = calculate_lags(station)

    station.size_time_series = (len(station.common_period) / 12) - 2

    station.contingencies_tables_percent = contingency_table(station)

    station = result_table_CA(station)

    if not threshold_problem[0] and not threshold_problem[1] and not threshold_problem[2]:
        graphics_climate(station)

    maps_climate(station)

    print colored.green(_("done"))

    return station


def forecasting(station):
    '''
    Main process for forecasting
    '''

    # console message
    sys.stdout.write(_("Processing forecasting ({0}-{1}) .............. ")
                     .format(station.process_period['start'], station.process_period['end']))
    sys.stdout.flush()

    # get and set date for calculate forecasting based on this
    if station.state_of_data in [1, 3]:
        try:
            station.forecasting_date = int(station.forecasting_date)
        except:
            print_error_line_stations(station,
                _("Trimester forecasting \"{0}\" is invalid, "
                  "should be integer number").format(station.forecasting_date))
        if not (1 <= station.forecasting_date <= 12):
            print_error_line_stations(station,
                _("Trimester forecasting \"{0}\" is invalid, "
                  "should be a month valid number (1-12)")
                  .format(station.forecasting_date))
    if station.state_of_data in [2, 4]:
        try:
            forecasting_date_original = station.forecasting_date
            station.forecasting_date = station.forecasting_date.replace('-', '/')
            station.forecasting_date = station.forecasting_date.split('/')
            station.forecasting_date[0] = int(station.forecasting_date[0])
            station.forecasting_date[1] = int(station.forecasting_date[1])
        except:
            print_error_line_stations(station,
                _("Month or day for calculate forecasting \"{0}\" is invalid, \n"
                  "should be month/day or month-day (e.g. 03/11)")
                  .format(forecasting_date_original))
        if not (1 <= station.forecasting_date[0] <= 12):
            print_error_line_stations(station,
                _("Month for forecasting process \"{0}\" is invalid, \n"
                  "should be a month valid number (1-12)")
                  .format(station.forecasting_date[0]))
        if station.forecasting_date[1] not in station.range_analysis_interval:
            print_error_line_stations(station,
                _("Start day for forecasting process \"{0}\" is invalid,\n"
                  "should be a valid start day based on range analysis\n"
                  "interval, these are for this station: {1}")
                  .format(station.forecasting_date[1], station.range_analysis_interval))

    # create directory for output files
    if not os.path.isdir(forecasting_dir):
        os.makedirs(forecasting_dir)

    station.forecasting_dir = \
        os.path.join(forecasting_dir, station.code + '_' + station.name)   # 'results'
    if not os.path.isdir(station.forecasting_dir):
        os.makedirs(station.forecasting_dir)

    prob_decrease_var_D = []
    prob_normal_var_D = []
    prob_exceed_var_D = []
    for lag in lags:

        items_CT = {'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 'f':0, 'g':0, 'h':0, 'i':0}

        if station.state_of_data in [1, 3]:
            _iter = 0
            for column in range(3):
                for row in range(3):
                    if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.forecasting_date - 1][_iter] == _('yes'):
                        vars()[items_CT[_iter]] = \
                            station.contingencies_tables_percent[lag][station.forecasting_date - 1][column][row] / 100.0
                        _iter += 1

        if station.state_of_data in [2, 4]:
            month = station.forecasting_date[0]
            day = station.range_analysis_interval.index(station.forecasting_date[1])
            _iter = 0
            for column in range(3):
                for row in range(3):
                    if not args.risk_analysis or station.is_sig_risk_analysis[lag][month - 1][day][_iter] == _('yes'):
                        items_CT[items_CT.keys()[_iter]] = \
                            station.contingencies_tables_percent[lag][month - 1][day][column][row] / 100.0
                        _iter += 1

        prob_decrease_var_D.append((items_CT['a'] * station.f_var_I_B[lag]) +
                                   (items_CT['d'] * station.f_var_I_N[lag]) +
                                   (items_CT['g'] * station.f_var_I_A[lag]))

        prob_normal_var_D.append((items_CT['b'] * station.f_var_I_B[lag]) +
                                 (items_CT['e'] * station.f_var_I_N[lag]) +
                                 (items_CT['h'] * station.f_var_I_A[lag]))

        prob_exceed_var_D.append((items_CT['c'] * station.f_var_I_B[lag]) +
                                 (items_CT['f'] * station.f_var_I_N[lag]) +
                                 (items_CT['i'] * station.f_var_I_A[lag]))

    station.prob_decrease_var_D = prob_decrease_var_D
    station.prob_normal_var_D = prob_normal_var_D
    station.prob_exceed_var_D = prob_exceed_var_D

    if not threshold_problem[0] and not threshold_problem[1] and not threshold_problem[2]:
        graphics_forecasting(station)

    maps_forecasting(station)

    print colored.green(_("done"))


#==============================================================================
# STATION CLASS
# for storage several variables of each station


class Station:
    '''
    Generic station class
    '''

    # counter stations processed
    stations_processed = 0

    def __init__(self):
        Station.stations_processed += 1


#==============================================================================
# MAIN PROCESS


def main():
    '''
    Main process of Jaziku
    '''

    # check python version
    if sys.version_info[0] != 2 and sys.version_info[1] < 6:
        print_error(_("You version of python is {0}, please use Jaziku with "
                      "python v2.6 or higher.").format(sys.version_info[0:2]))

    # set encoding to utf-8
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # Parser and check arguments
    global args
    args = input_arg.arguments.parse_args()


    if args.l:
        if args.l == "en" or args.l == "EN" or args.l == "En":
            lang = gettext.NullTranslations()
        else:
            try:
                lang = gettext.translation(TRANSLATION_DOMAIN, LOCALE_DIR,
                                           languages=[args.l],
                                           codeset="utf-8")
            except:
                print_error(_("\"{0}\" language not available.").format(args.l))

        if 'lang' in locals():
            lang.install()
            settings_language = colored.green(args.l)
    else:
        # Setting language based on locale language system,
        # when not defined language in arguments
        try:
            locale_languaje = locale.getdefaultlocale()[0][0:2]
            settings_language = colored.green(locale_languaje) + _(" (locale system)")
            try:
                if locale_languaje != "en":
                    lang = gettext.translation(TRANSLATION_DOMAIN, LOCALE_DIR,
                                               languages=[locale_languaje],
                                               codeset="utf-8")
            except:
                settings_language = colored.green("en") + _(" (language \'{0}\' has not was translated yet)").format(locale_languaje)
                lang = gettext.NullTranslations()
                lang.install()
        except:
            settings_language = colored.green("en") + _(" (other languages were not detected)")
            lang = gettext.NullTranslations()
            lang.install()


    # set settings default
    settings = {"climate": _("disabled"), "forecasting": _("disabled"),
                "p_below": "-", "p_normal": "-", "p_above": "-", "period": "-",
                "risk-analysis": _("disabled"),
                "language": settings_language}


    # console message
    print _("\n########################### JAZIKU ###########################\n"
            "## Jaziku is a software for the implementation of composite ##\n"
            "## analysis metodology between the major indices of climate ##\n"
            "## variability and major meteorological variables in        ##\n"
            "## puntual scale.                                           ##\n"
            "##                                                          ##\n"
            "## Version {0} - {1}\t                            ##\n"
            "## Copyright 2011-2012 IDEAM - Colombia                     ##\n"
            "##############################################################") \
            .format(globals.VERSION, globals.COMPILE_DATE)

    # set period for process if is defined as argument
    if args.period:
        global args_period_start, args_period_end
        try:
            args_period_start = int(args.period.split('-')[0])
            args_period_end = int(args.period.split('-')[1])
            settings["period"] = colored.green("{0}-{1}".format(args_period_start, args_period_end))
        except Exception, e:
            print_error(_('the period must be: year_start-year_end (ie. 1980-2008)\n\n{0}').format(e))

    # number of lags
    global lags
    lags = [0, 1, 2]

    # trimester text for print
    global trim_text
    trim_text = {-2:_('ndj'), -1:_('djf'), 0:_('jfm'), 1:_('fma'), 2:_('mam'),
                 3:_('amj'), 4:_('mjj'), 5:_('jja'), 6:_('jas'), 7:_('aso'),
                 8:_('son'), 9:_('ond'), 10:_('ndj'), 11:_('djf')}

    # month text for print
    global month_text
    month_text = {-2:_('nov'), -1:_('dec'), 0:_('jan'), 1:_('feb'), 2:_('mar'),
                 3:_('apr'), 4:_('may'), 5:_('jun'), 6:_('jul'), 7:_('aug'),
                 8:_('sep'), 9:_('oct'), 10:_('nov'), 11:_('dec')}

    # if phenomenon below is defined inside arguments, else default value
    if args.p_below:
        globals.phenomenon_below = unicode(args.p_below, 'utf-8')
        settings["p_below"] = colored.green(args.p_below)
    # if phenomenon normal is defined inside arguments, else default value
    if args.p_normal:
        globals.phenomenon_normal = unicode(args.p_normal, 'utf-8')
        settings["p_normal"] = colored.green(args.p_normal)
    # if phenomenon above is defined inside arguments, else default value
    if args.p_above:
        globals.phenomenon_above = unicode(args.p_above, 'utf-8')
        settings["p_above"] = colored.green(args.p_above)

    # set settings for process
    if args.climate:
        settings["climate"] = colored.green(_("enabled"))
    if args.forecasting:
        settings["forecasting"] = colored.green(_("enabled"))
    if args.risk_analysis:
        settings["risk_analysis"] = colored.green(_("enabled"))

    # print settings
    print _("\nConfiguration run:")
    print "   {0} -------- {1}".format("climate", settings["climate"])
    print "   {0} ---- {1}".format("forecasting", settings["forecasting"])
    print "   {0} -------- {1}".format("p_below", settings["p_below"])
    print "   {0} ------- {1}".format("p_normal", settings["p_normal"])
    print "   {0} -------- {1}".format("p_above", settings["p_above"])
    print "   {0} --------- {1}".format("period", settings["period"])
    print "   {0} -- {1}".format("risk-analysis", settings["risk-analysis"])
    print "   {0} ------- {1}".format("language", settings["language"])

    # -------------------------------------------------------------------------
    # globals.maps_files_climate
    if args.climate:
        # climate dir output result
        global climate_dir
        climate_dir = \
            os.path.join(os.path.splitext(args.stations.name)[0], _('Jaziku_Climate'))   # 'results'

        print _("\nSaving the result for climate in:\n -> {0}").format(climate_dir)

        if os.path.isdir(climate_dir):
            print colored.yellow(\
                _("\n   Warning: the output director for climate process\n" \
                  "   is already exist, Jaziku continue but the results\n" \
                  "   could be mixed or replaced of old output."))


    # -------------------------------------------------------------------------
    # globals.maps_files_forecasting
    if args.forecasting:
        # forecasting dir output result
        global forecasting_dir
        forecasting_dir = \
            os.path.join(os.path.splitext(args.stations.name)[0], _('Jaziku_Forecasting'))   # 'results'

        print _("\nSaving the result for forecasting in:\n -> {0}").format(forecasting_dir)

        if os.path.isdir(forecasting_dir):
            print colored.yellow(\
                _("\n   Warning: the output director for forecasting process\n" \
                  "   is already exist, Jaziku continue but the results\n" \
                  "   could be mixed or replaced of old output."))


    # -------------------------------------------------------------------------
    # read all stations from stations list inside stations file 
    # (-station arguments) and process station by station
    stations = csv.reader(args.stations, delimiter=';')
    for line_station in stations:

        # trim all items in line_station
        line_station = [i.strip() for i in line_station]

        # if line of station is null o empty, e.g. empty but with tabs or spaces
        if not line_station or not line_station[0].strip():
            continue

        # new instance of station
        station = Station()

        global threshold_problem
        threshold_problem = [False, False, False]

        try:
            station.code = line_station[0]
            station.name = line_station[1]
            station.lat = line_station[2].replace(',', '.')
            station.lon = line_station[3].replace(',', '.')

            station.file_D = open(line_station[4], 'rb')
            station.type_D = line_station[5]

            station.file_I = line_station[6]
            station.type_I = line_station[7]

            station.range_below_I = line_station[8]
            station.range_above_I = line_station[9]

            station.threshold_below_var_I = line_station[10].replace(',', '.')
            station.threshold_above_var_I = line_station[11].replace(',', '.')

            station.analysis_interval = line_station[12]

            options_analysis_interval = ["5days", "10days", "15days", "trimester"]
            if station.analysis_interval not in options_analysis_interval:
                raise Exception(_("The analysis interval {0} is invalid,\n"
                                  "should be one of these: {1}")
                                  .format(station.analysis_interval,
                                          ', '.join(options_analysis_interval)))

            if station.analysis_interval != "trimester":
                # detect analysis_interval number from string
                _count = 0
                for digit in station.analysis_interval:
                    try:
                        int(digit)
                        _count += 1
                    except:
                        pass
                station.analysis_interval_num_days = int(station.analysis_interval[0:_count])

            if args.forecasting:
                if len(line_station) < 23:
                    raise Exception(_("For forecasting process you need define "
                                      "9 probability\n variables and trimester to "
                                      "process in stations file."))
                station.f_var_I_B = [float(line_station[13].replace(',', '.')),
                                     float(line_station[16].replace(',', '.')),
                                     float(line_station[19].replace(',', '.'))]
                station.f_var_I_N = [float(line_station[14].replace(',', '.')),
                                     float(line_station[17].replace(',', '.')),
                                     float(line_station[20].replace(',', '.'))]
                station.f_var_I_A = [float(line_station[15].replace(',', '.')),
                                     float(line_station[18].replace(',', '.')),
                                     float(line_station[21].replace(',', '.'))]

                station.forecasting_date = line_station[22]

        except Exception, e:
            print_error(_("Reading stations from file \"{0}\" in line {1}:\n")
                        .format(args.stations.name, stations.line_num) +
                        ';'.join(line_station) + "\n\n" + str(e))

        station.line_station = line_station
        station.line_num = stations.line_num

        # console message
        print _("\n################# STATION: {0} ({1})").format(station.name, station.code)

        # run pre_process: read, validated and check data
        station = pre_process(station)

        # run process:
        station = process(station)

        # clear and delete all instances of maps created by pyplot
        plt.close('all')

        # delete instance
        del station


    print colored.green(_("\nProcess completed!, {0} station(s) processed.\n")
                        .format(Station.stations_processed))
    print _("Good bye :)\n")


# Run main() when call jaziku.py
if __name__ == "__main__":
    main()
