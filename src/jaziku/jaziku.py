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
    Jazikü is a word in huitoto mean jungle, forest.

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
           [-p_above P_ABOVE] [-c] [-f] [-period PERIOD] [-ra]

EXAMPLE:
    jaziku -stations station.csv -c -f

    jaziku -stations station.csv -p_below "Debajo" -p_normal "Normal" -p_above
    "Encima" -c -f -period 1980-2009 -ra

Copyright © 2011 IDEAM
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

# internationalization:
import gettext
TRANSLATION_DOMAIN = "jaziku"
LOCALE_DIR = 'locale'  # os.path.join(os.path.dirname(__file__), "locale")
gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR)

# import funtions in plugins
import plugins.global_var as global_var
import plugins.input_validation as input_validation
import plugins.input_arg as input_arg
import plugins.contingency_test as ct
import plugins.significance_corr as sc

# from progressbar import Bar, Percentage, ProgressBar
# http://code.google.com/p/python-progressbar/


#==============================================================================
# PRINT FUCTIONS


def print_error(text_error):
    '''
    Print error generic function, this is called on any error occurred in
    Jaziku
    '''

    print _('\n\nERROR:\n{0}\n\nFor more help run program with argument: -h')\
           .format(text_error)
    exit()


def print_number(num):
    '''
    Print number to csv file acording to accuracy and fix decimal character
    '''
    return str(round(float(num), global_var.ACCURACY)).replace('.', ',')


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
    reader_csv = csv.reader(file_D, delimiter = '\t')

    # reader_csv = csv.reader(fo, delimiter = '\t')
    # reader_csv.write(data.replace('\x00', ''))

    # Read line to line file_D, validation and save var_D
    try:
        for row in reader_csv:
            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')
            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_D.name, reader_csv.line_num))
            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                value = float(row[1])
                # set date of dependent variable from file_D, column 1,
                # format: yyyy-mm
                date_D.append(date(year, month, 1))
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

        print _("\n\n\tWarning: Repairing file \"{0}\" of NULL bytes garbage,"\
              "\n\tsaving new file as: {1}").format(station.file_D.name,
                                                    name_fix)

        reader_csv_fix = csv.reader(open(name_fix, 'rb'), delimiter = '\t')

        # Now read fix file
        for row in reader_csv_fix:
            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')
            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_D.name, reader_csv.line_num))
            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                value = float(row[1])
                # set date of dependent variable from file_D, column 1,
                # format: yyyy-mm
                date_D.append(date(year, month, 1))
                # set values of dependent variable
                var_D.append(input_validation.validation_var_D(station.type_D,
                                                               value,
                                                               date_D[-1]))

            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                            .format(station.file_D.name,
                                    reader_csv_fix.line_num, e))

    return var_D, date_D


def read_var_I(station):
    '''
    Read independent variable from file define in station list
    and check and validate value by value.

    Return: values[] and dates[]
    '''
    date_I = []
    var_I = []

    file_I = station.file_I
    reader_csv = csv.reader(file_I, delimiter = '\t')
    # Read line to line file_I, validation and save var_I
    try:
        for row in reader_csv:
            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')
            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_D.name, reader_csv.line_num))
            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                value = float(row[1])
                # set date of independent variable from file_I, column 1,
                # format: yyyy-mm
                date_I.append(date(year, month, 1))
                # set values of independent variable
                var_I.append(input_validation.validation_var_I(station.type_I,
                                                               value))

            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                            .format(station.file_I.name,
                                    reader_csv.line_num, e))

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

        print _("\n\n\tWarning: Repairing file \"{0}\" of NULL bytes garbage,"\
              "\n\tsaving new file as: {1}").format(station.file_I.name,
                                                    name_fix)

        reader_csv_fix = csv.reader(open(name_fix, 'rb'), delimiter = '\t')

        # Now read fix file
        for row in reader_csv_fix:
            try:
                row[0] = row[0].replace('/', '-')
                row[1] = row[1].replace(',', '.')
            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n"
                              "this could be caused by wrong line or garbage "
                              "character,\nplease check manually, fix it and "
                              "run again.")
                             .format(station.file_D.name, reader_csv.line_num))
            try:
                # delete garbage characters and convert format
                year = int(re.sub(r'[^\w]', '', row[0].split("-")[0]))
                month = int(re.sub(r'[^\w]', '', row[0].split("-")[1]))
                value = float(row[1])
                # set date of independent variable from file_I, column 1,
                # format: yyyy-mm
                date_I.append(date(year, month, 1))
                # set values of independent variable
                var_I.append(input_validation.validation_var_I(station.type_I,
                                                               value))

            except Exception, e:
                print_error(_("Reading from file \"{0}\" in line: {1}\n\n{2}")
                            .format(station.file_I.name,
                                    reader_csv_fix.line_num, e))

    return var_I, date_I

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
        if (period_start < common_date[0].year or
            period_end > common_date[-1].year):
            print_error(_("period define in argument {0}-{1} is outside the "
                          "common period {2}-{3}")
                        .format(period_start, period_end, common_date[0].year,
                                common_date[-1].year))

        common_date = common_date[common_date.index(date(period_start, 1, 1)):
                                  common_date.index(date(period_end, 12, 1))]

    common_period = []
    # set values matrix for common_period
    for date_period in common_date:
        # common_period format list: [[  date ,  var_D ,  var_I ],... ]
        common_period.append([date_period,
                              station.var_D[station.date_D.index(date_period)],
                              station.var_I[station.date_I.index(date_period)]])
    return common_period


def column(matrix, i):
    '''Return column i from matrix'''

    return [row[i] for row in matrix]


def get_lag_values(station, lag, trim, var):
    '''
    Return all values of var_D, var_I or date
    of specific lag and trimester.
    '''

    var_select = {'date': 0, 'var_D': 1, 'var_I': 2}
    lag_select = {0: station.Lag_0, 1: station.Lag_1, 2: station.Lag_2}
    temp_list = []
    for line in lag_select[lag]:
        if trim == line[0]:
            temp_list.append(line[1])
    return [row[var_select[var]] for row in temp_list]


def meanTrim(var_1, var_2, var_3):
    '''
    Return average from 3 values, ignoring valid null values.
    '''

    if (int(var_1) in global_var.VALID_NULL and
        int(var_2) in global_var.VALID_NULL and
        int(var_3) in global_var.VALID_NULL):
        return  global_var.VALID_NULL[1]

    if (int(var_1) not in global_var.VALID_NULL and
        int(var_2) in global_var.VALID_NULL and
        int(var_3) in global_var.VALID_NULL):
        return  var_1

    if (int(var_1) in global_var.VALID_NULL and
        int(var_2) not in global_var.VALID_NULL and
        int(var_3) in global_var.VALID_NULL):
        return  var_2

    if (int(var_1) in global_var.VALID_NULL and
        int(var_2) in global_var.VALID_NULL and
        int(var_3) not in global_var.VALID_NULL):
        return  var_3

    if (int(var_1) not in global_var.VALID_NULL and
        int(var_2) not in global_var.VALID_NULL and
        int(var_3) in global_var.VALID_NULL):
        return  (var_1 + var_2) / 2.0

    if (int(var_1) in global_var.VALID_NULL and
        int(var_2) not in global_var.VALID_NULL and
        int(var_3) not in global_var.VALID_NULL):
        return  (var_2 + var_3) / 2.0

    if (int(var_1) not in global_var.VALID_NULL and
        int(var_2) in global_var.VALID_NULL and
        int(var_3) not in global_var.VALID_NULL):
        return  (var_1 + var_3) / 2.0

    if (int(var_1) not in global_var.VALID_NULL and
        int(var_2) not in global_var.VALID_NULL and
        int(var_3) not in global_var.VALID_NULL):
        return  (var_1 + var_2 + var_3) / 3.0


def calculate_lags(station):
    '''
    Calculate and return lags 0, 1 and 2 of specific stations
    and save csv file of time series for each lag and trimester,
    the lags are calculated based in: +1 year below of start
    commond period and -1 year above of end commond period.
    '''

    # initialized Lag_X
    # format list: [trim, [ date, meanTrim_var_D, meanTrim_var_I ]], ...
    Lag_0 = []
    Lag_1 = []
    Lag_2 = []

    # directories to save lags
    dir_lag = [os.path.join(station.climate_dir, _('time_series'), _('lag_0')),
               os.path.join(station.climate_dir, _('time_series'), _('lag_1')),
               os.path.join(station.climate_dir, _('time_series'), _('lag_2'))]

    for lag in lags:

        if not os.path.isdir(dir_lag[lag]):
            os.makedirs(dir_lag[lag])

        # all months in year 1->12
        for month in range(1, 13):
            csv_name = os.path.join(dir_lag[lag],
                                    _('meanLag_{0}_trim_{1}_{2}_{3}_{4}_{5}_'
                                      '({6}-{7}).csv')
                                    .format(lag, month, station.code,
                                            station.name, station.type_D,
                                            station.type_I,
                                            station.period_start,
                                            station.period_end))

            # output write file:
            # [[ yyyy/month, meanLag_X_var_D, meanLag_X_var_I ],... ]
            csv_file_write = csv.writer(open(csv_name, 'w'), delimiter = ';')
            # temporal var initialize iter_date = start common_period + 1 year,
            # month=1, day=1
            iter_date = date(station.period_start + 1, 1, 1)
            # temporal var initialize end_date = end common_period - 1 year,
            # month=12, day=31
            end_date = date(station.period_end - 1, 12, 31)

            # iteration for years from first-year +1 to end-year -1 inside
            # range common_period
            while True:
                if iter_date >= end_date:
                    break

                # calculate var_D for this months
                var_D_1 = station.var_D[station.date_D.index(iter_date +
                                        relativedelta(months = month - 1))]
                var_D_2 = station.var_D[station.date_D.index(iter_date +
                                        relativedelta(months = month))]
                var_D_3 = station.var_D[station.date_D.index(iter_date +
                                        relativedelta(months = month + 1))]
                # calculate meanTrim_var_D
                meanTrim_var_D = meanTrim(var_D_1, var_D_2, var_D_3)

                # calculate var_I for this months
                var_I_1 = station.var_I[station.date_I.index(iter_date +
                                        relativedelta(months = month - 1 - lag))]
                var_I_2 = station.var_I[station.date_I.index(iter_date +
                                        relativedelta(months = month - lag))]
                var_I_3 = station.var_I[station.date_I.index(iter_date +
                                        relativedelta(months = month + 1 - lag))]
                # calculate meanTrim_var_I
                meanTrim_var_I = meanTrim(var_I_1, var_I_2, var_I_3)

                # add line in list: Lag_X
                vars()[_('Lag_') + str(lag)].append([month, [iter_date,
                                                             meanTrim_var_D,
                                                             meanTrim_var_I]])

                # add line output file csv_file_write
                csv_file_write.writerow([str(iter_date.year) + "/" + str(month),
                                             print_number(meanTrim_var_D),
                                             print_number(meanTrim_var_I)])
                # next year
                iter_date += relativedelta(years = +1)

    return Lag_0, Lag_1, Lag_2


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
            print_error(_("threshoulds ​​could not were identified:\n{0} - {1}")
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


def get_contingency_table(station, lag, month):
    '''
    Calculate and return the contingency table in absolute values,
    values in percent, values to print and thresholds by below and
    above of dependent and independent variable.
    '''

    # get all values of var D and var I based on this lag and month
    station.var_D_values = get_lag_values(station, lag, month, 'var_D')
    station.var_I_values = get_lag_values(station, lag, month, 'var_I')

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

    sum_per_column_percent = contingency_table_percent.sum(axis = 1)

    # threshold_problem is global variable for detect problem with
    # threshold of independent variable, if a problem is detected
    # show message and print "nan" (this mean null value for 
    # division by cero) in contingency tabla percent in result 
    # table, jaziku continue but the graphics will not be created 
    # because "nan"  character could not be calculate.
    global threshold_problem

    # if threshold by below of independent variable is wrong
    if float(sum_per_column_percent[0]) == 0 and not threshold_problem[0]:
        print _(u'\n\nWarning:\nThe thresholds selected \"{0}\" and \"{1}\" are not suitable for\n' \
                u'compound analysis of variable \"{2}\" with relation to \"{3}\"\n' \
                u'inside category \"{4}\". Therefore, the graphics will not be created.') \
                .format(station.threshold_below_var_I, station.threshold_below_var_I,
                       station.type_D, station.type_I, station.phenomenon_below)
        threshold_problem[0] = True

    # if threshold by below or above calculating normal phenomenon of independent variable is wrong
    if float(sum_per_column_percent[1]) == 0 and not threshold_problem[1]:
        print _(u'\n\nWarning:\nThe thresholds selected \"{0}\" and \"{1}\" are not suitable for\n' \
                u'compound analysis of variable \"{2}\" with relation to \"{3}\"\n' \
                u'inside category \"{4}\". Therefore, the graphics will not be created.') \
                .format(station.threshold_below_var_I, station.threshold_below_var_I,
                       station.type_D, station.type_I, station.phenomenon_normal)
        threshold_problem[1] = True

    # if threshold by above of independent variable is wrong
    if float(sum_per_column_percent[2]) == 0 and not threshold_problem[2]:
        print _(u'\n\nWarning:\nThe thresholds selected \"{0}\" and \"{1}\" are not suitable for\n' \
                u'compound analysis of variable \"{2}\" with relation to \"{3}\"\n' \
                u'inside category \"{4}\". Therefore, the graphics will not be created.') \
               .format(station.threshold_below_var_I, station.threshold_below_var_I,
                       station.type_D, station.type_I, station.phenomenon_above)
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

    # directories to save contingency tables
    dir_contingency = \
        [os.path.join(station.climate_dir, _('contingency_table'), _('lag_0')),
         os.path.join(station.climate_dir, _('contingency_table'), _('lag_1')),
         os.path.join(station.climate_dir, _('contingency_table'), _('lag_2'))]

    # [lag][month][phenomenon][data(0,1,2)]
    contingencies_tables_percent = []

    for lag in lags:

        if not os.path.isdir(dir_contingency[lag]):
            os.makedirs(dir_contingency[lag])

        month_list = []
        # all months in year 1->12
        for month in range(1, 13):

            contingency_table, \
            contingency_table_percent, \
            contingency_table_percent_print, \
            thresholds_var_D_var_I = get_contingency_table(station, lag, month)

            month_list.append(contingency_table_percent)

            ## print result in csv file
            # add new line in csv_contingency_table

            csv_name = \
                os.path.join(dir_contingency[lag], _('contingency_table_Lag'
                    '_{0}_trim_{1}_{2}_{3}_{4}_{5}_({6}-{7}).csv')
                    .format(lag, month, station.code, station.name, station.type_D,
                            station.type_I, station.period_start, station.period_end))
            csv_contingency_table = csv.writer(open(csv_name, 'w'), delimiter = ';')

            csv_contingency_table.writerow(['', _('var I Below'),
                                            _('var I Normal'),
                                            _('var I Above')])

            csv_contingency_table.writerow([_('var D Below'),
                                       contingency_table_percent_print[0][0],
                                       contingency_table_percent_print[1][0],
                                       contingency_table_percent_print[2][0]])

            csv_contingency_table.writerow([_('var D Normal'),
                                       contingency_table_percent_print[0][1],
                                       contingency_table_percent_print[1][1],
                                       contingency_table_percent_print[2][1]])

            csv_contingency_table.writerow([_('var D Above'),
                                       contingency_table_percent_print[0][2],
                                       contingency_table_percent_print[1][2],
                                       contingency_table_percent_print[2][2]])

        contingencies_tables_percent.append(month_list)

    return contingencies_tables_percent


def result_table(station):
    '''
    Calculate and print the result table csv file, this file contein several 
    variables of previous calculations and different tests.
    '''

    # dir and name to save the result table
    csv_name = \
    os.path.join(station.climate_dir, _('result_table_{0}_{1}_{2}_{3}_({4}-{5}).csv')
                .format(station.code, station.name, station.type_D, station.type_I,
                        station.period_start, station.period_end))

    csv_result_table = csv.writer(open(csv_name, 'w'), delimiter = ';')

    # print headers in result table
    csv_result_table.writerow([
         _('var_D'), _('var_I'), _('Pearson'), _('Sign Pearson'),
         _('Is sign "Sign Pearson"?'), _('threshold below (var D)'),
         _('threshold above (var D)'), _('threshold below (var I)'),
         _('threshold above (var I)'), _('Contingency Table (CT)'),
         '', '', '', '', '', '', '', '', _('Contingency Table in %'),
         '', '', '', '', '', '', '', '', _('is sig risk analysis?'),
         '', '', '', '', '', '', '', '', _('Test Stat - Chi2'),
         _('Crit Value - Chi2'), _('Is sig CT?'), _('correl_CT')])

    pearson_list = []
    is_sig_risk_analysis = []

    for lag in lags:

        # print division line between lags
        csv_result_table.writerow([
             _('Lag {0}').format(lag), '', '', '', '', '', '', '', '',
             station.phenomenon_below.encode("utf-8"), '', '',
             station.phenomenon_normal.encode("utf-8"), '', '',
             station.phenomenon_above.encode("utf-8"), '', '',
             station.phenomenon_below.encode("utf-8"), '', '',
             station.phenomenon_normal.encode("utf-8"), '', '',
             station.phenomenon_above.encode("utf-8")])

        csv_result_table.writerow([
             '', '', '', '', '', '', '', '', '',
             _('var Dep below'), _('var Dep normal'), _('var Dep above'),
             _('var Dep below'), _('var Dep normal'), _('var Dep above'),
             _('var Dep below'), _('var Dep normal'), _('var Dep above'),
             _('var Dep below'), _('var Dep normal'), _('var Dep above'),
             _('var Dep below'), _('var Dep normal'), _('var Dep above'),
             _('var Dep below'), _('var Dep normal'), _('var Dep above')])

        pearson_list_month = []
        is_sig_risk_analysis_month = []

        # all months in year 1->12
        for month in range(1, 13):

            # get the contingency tables and thresholds
            contingency_table, \
            contingency_table_percent, \
            contingency_table_percent_print, \
            thresholds_var_D_var_I = get_contingency_table(station, lag, month)

            # test:
            # is significance risk analysis?
            contingency_table_matrix = np.matrix(contingency_table)
            sum_per_row = contingency_table_matrix.sum(axis = 0).tolist()[0]
            sum_per_column = contingency_table_matrix.sum(axis = 1).tolist()
            sum_contingency_table = contingency_table_matrix.sum()

            is_sig_risk_analysis_month_list = []
            for c, column_table in enumerate(contingency_table):
                for r, Xi in enumerate(column_table):
                    M = sum_per_column[c]
                    n = sum_per_row[r]
                    N = sum_contingency_table
                    X = stats.hypergeom.cdf(Xi, N, M, n)
                    Y = stats.hypergeom.sf(Xi, N, M, n, loc = 1)
                    if X <= 0.1 or Y <= 0.1:
                        is_sig_risk_analysis_month_list.append(_('yes'))
                    else:
                        is_sig_risk_analysis_month_list.append(_('no'))

            # get values of var D and I from this lag and month
            var_D_values = get_lag_values(station, lag, month, 'var_D')
            var_I_values = get_lag_values(station, lag, month, 'var_I')

            # calculate pearson correlation of var_D and var_I
            pearson = stats.pearsonr(var_D_values, var_I_values)[0]
            pearson_list_month.append(pearson)

            # significance correlation
            singr, T_test, t_crit = \
                sc.corrtest(rho = 0, r = pearson, n = len(station.common_period) + 1,
                            alpha = 0.05, side = 0)

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
                 trim_text[month - 1], trim_text[month - 1 - lag],
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
                 is_sig_risk_analysis_month_list[0], is_sig_risk_analysis_month_list[1],
                 is_sig_risk_analysis_month_list[2], is_sig_risk_analysis_month_list[3],
                 is_sig_risk_analysis_month_list[4], is_sig_risk_analysis_month_list[5],
                 is_sig_risk_analysis_month_list[6], is_sig_risk_analysis_month_list[7],
                 is_sig_risk_analysis_month_list[8],
                 print_number(test_stat), print_number(crit_value),
                 is_significant_CT, print_number_accuracy(corr_CT, 4)])

            is_sig_risk_analysis_month.append(is_sig_risk_analysis_month_list)

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

    for lag in lags:

        # create dir for lag
        if not os.path.isdir(os.path.join(graphics_dir_ca, _('lag_{0}').format(lag))):
            os.makedirs(os.path.join(graphics_dir_ca, _('lag_{0}').format(lag)))

        image_open = []

        # all months in year 1->12
        for month in range(1, 13):

            contingency_table, \
            contingency_table_percent, \
            contingency_table_percent_print, \
            thresholds_var_D_var_I = get_contingency_table(station, lag, month)

            ## graphics options for plot:
            # the x locations for the groups
            ind = np.array([0, 0.8, 1.6])
            # the width of the bars  
            width = 0.2

            plt.figure()

            # graphics title
            plt.title(unicode(_('Composite analisys - {0} ({1})\n{2} - {3} - '
                                'lag {6} - trim {7} ({8}) - ({4}-{5})')
                                .format(station.name, station.code, station.type_I,
                                        station.type_D, station.period_start,
                                        station.period_end, lag, month,
                                        trim_text[month - 1]), 'utf-8'))

            # label for axis Y 
            plt.ylabel(_('probability (%)'))
            #  adjust the max leaving min unchanged in Y
            plt.ylim(ymin = 0, ymax = 100)
            #  adjust the max leaving min unchanged in X
            plt.xlim(xmin = -0.1, xmax = 2.3)
            # plt.xticks([0.3, 1.1, 1.9], ('var Ind Below', 'var Ind Normal', 'var Ind Above'),)
            plt.xticks([])
            # colors for paint bars and labels: below, normal , above
            colours = ['#DD4620', '#62AD29', '#6087F1']
            # assigning values for plot:
            var_D_below = plt.bar(ind, column(contingency_table_percent, 0),
                                  width, color = colours[0])
            var_D_normal = plt.bar(ind + width, column(contingency_table_percent, 1),
                                   width, color = colours[1])
            var_D_above = plt.bar(ind + 2 * width, column(contingency_table_percent, 2),
                                  width, color = colours[2])

            # assing value for each bart
            def autolabel(rects):
                # attach some text labels
                temp = []
                for rect in rects:
                    temp.append(rect.get_height())
                temp.sort(reverse = True)
                max_heigth = temp[0]

                for rect in rects:
                    height = rect.get_height()
                    plt.text(rect.get_x() + rect.get_width() / 2.0, 0.015 * max_heigth +
                             height, round(height, 1), ha = 'center', va = 'bottom')

            autolabel(var_D_below)
            autolabel(var_D_normal)
            autolabel(var_D_above)

            plt.subplots_adjust(bottom = 0.15, left = 0.22, right = 0.97)
            # plt.legend((var_D_below[0], var_D_normal[0], var_D_above[0]), 
            #            ('var Dep Below', 'var Dep Normal', 'var Dep Above'),
            #             shadow = True, fancybox = True)

            # table in graphic
            colLabels = (station.phenomenon_below, station.phenomenon_normal,
                         station.phenomenon_above)

            rowLabels = [_('var Dep Below'), _('var Dep Normal'), _('var Dep Above')]

            contingency_table_percent_graph = [column(contingency_table_percent_print, 0),
                                               column(contingency_table_percent_print, 1),
                                               column(contingency_table_percent_print, 2)]

            # Add a table at the bottom of the axes
            plt.table(cellText = contingency_table_percent_graph,
                                 rowLabels = rowLabels, rowColours = colours,
                                 colLabels = colLabels, loc = 'bottom')

            ## Save image
            plt.subplot(111)
            image_dir_save = \
                os.path.join(graphics_dir_ca, _('lag_{0}').format(lag),
                             _('ca_lag_{0}_trim_{1}_{2}_{3}_{4}_{5}_({6}-{7}).png')
                             .format(lag, month, station.code, station.name, station.type_D,
                                     station.type_I, station.period_start, station.period_end))

            plt.savefig(image_dir_save, dpi = 75)
            #plt.close()
            plt.clf()

            # save dir image for mosaic
            image_open.append(img_open(image_dir_save))

        ## create mosaic

        # definition height and width of individual image
        image_height = 450
        image_width = 600
        mosaic_dir_save = \
            os.path.join(graphics_dir_ca, _('mosaic_lag_{0}_{1}_{2}_{3}_{4}_({5}-{6}).png')
                        .format(lag, station.code, station.name, station.type_D, station.type_I,
                                station.period_start, station.period_end))

        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        plt.figure(figsize = ((image_width * 3) / 100, (image_height * 4) / 100))
        plt.savefig(mosaic_dir_save, dpi = 100)
        mosaic = img_open(mosaic_dir_save)
        mosaic.paste(image_open[0], (0, 0))
        mosaic.paste(image_open[1], (image_width, 0))
        mosaic.paste(image_open[2], (image_width * 2, 0))
        mosaic.paste(image_open[3], (0, image_height))
        mosaic.paste(image_open[4], (image_width, image_height))
        mosaic.paste(image_open[5], (image_width * 2, image_height))
        mosaic.paste(image_open[6], (0, image_height * 2))
        mosaic.paste(image_open[7], (image_width, image_height * 2))
        mosaic.paste(image_open[8], (image_width * 2, image_height * 2))
        mosaic.paste(image_open[9], (0, image_height * 3))
        mosaic.paste(image_open[10], (image_width, image_height * 3))
        mosaic.paste(image_open[11], (image_width * 2, image_height * 3))
        mosaic.save(mosaic_dir_save)
        plt.clf()

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

    image_open = []

    for lag in lags:

        ## Options for graphics pie
        # make a square figure and axes
        plt.figure(1, figsize = (5, 5))
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
            return '{p:1.1f}%\n({v:1.2f})'.format(p = pct, v = val)

        plt.pie(values_pie, colors = colours, explode = explode, labels = labels,
                autopct = '%1.1f%%', shadow = True)  #'%1.1f%%'

        plt.title(unicode(_('Probability forecasted of {0} - {1}\n{2} - lag {3} - trim {4} ({5}) - ({6}-{7})')
                          .format(station.type_D, station.name, station.type_I, lag, station.f_trim,
                          trim_text[station.f_trim - 1], station.period_start, station.period_end),
                          'utf-8'), fontsize = 13)

        ## Save image
        # plt.subplot(111)
        image_dir_save = \
            os.path.join(station.forecasting_dir, _('prob_of_{0}_lag_{1}_trim_{2}_({3}-{4}).png')
                         .format(station.type_D, lag, station.f_trim,
                                 station.period_start, station.period_end))
        plt.savefig(image_dir_save, dpi = 75)
        plt.clf()

        # save dir image for mosaic
        image_open.append(img_open(image_dir_save))

    ## Create mosaic
    # definition height and width of individual image
    # image_height = 375
    image_width = 375
    mosaic_dir_save = \
        os.path.join(station.forecasting_dir, _('mosaic_prob_of_{0}_trim_{1}_({3}-{4}).png')
                     .format(station.type_D, lag, station.f_trim,
                             station.period_start, station.period_end))
    # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
    plt.figure(figsize = (11.25, 3.75))  # http://www.classical-webdesigns.co.uk/resources/pixelinchconvert.html
    plt.savefig(mosaic_dir_save, dpi = 100)
    mosaic = img_open(mosaic_dir_save)
    mosaic.paste(image_open[0], (0, 0))
    mosaic.paste(image_open[1], (image_width, 0))
    mosaic.paste(image_open[2], (image_width * 2, 0))
    mosaic.save(mosaic_dir_save)
    plt.clf()

#==============================================================================
# PLOTTING MAPS
# create file for ploting
# TODO: generate maps from previus file, plot all index from all stations


def maps_climate(station):
    '''
    Create maps data svc file for ploting for each trimester, phenomenon and lag,
    each file contain all stations processed.
    '''

    for lag in lags:

        # all months in year 1->12
        for month in range(1, 13):

            for phenomenon in [0, 1, 2]:
                var_below = station.contingencies_tables_percent[lag][month - 1][phenomenon][0]
                var_normal = station.contingencies_tables_percent[lag][month - 1][phenomenon][1]
                var_above = station.contingencies_tables_percent[lag][month - 1][phenomenon][2]

                # select index
                if var_below > var_normal:
                    if var_below > var_above:
                        p_index = -var_below
                    elif var_above > var_normal:
                        p_index = var_above
                    elif var_below == var_normal:
                        p_index = 0
                    else:
                        p_index = var_below
                else:
                    if var_normal == var_above:
                        p_index = 0
                    elif var_normal > var_above:
                        p_index = 0
                    else:
                        p_index = var_above

                station.maps_plots_files_climate[lag][month - 1][phenomenon]\
                    .writerow([station.code, station.lat, station.lon,
                               print_number(station.pearson_list[lag][month - 1]),
                               print_number(var_below), print_number(var_normal),
                               print_number(var_above), print_number(p_index),
                               print_number(sum([float(var_below),
                                                 float(var_normal),
                                                 float(var_above)]))])


def maps_forecasting(station):
    '''
    Create maps data svc file for ploting for each trimester, phenomenon and 
    lag, each file contain all stations processed. 
    '''

    for lag in lags:

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


        station.maps_plots_files_forecasting[lag]\
            .writerow([station.code, station.lat, station.lon,
                       print_number(station.prob_decrease_var_D[lag]),
                       print_number(station.prob_normal_var_D[lag]),
                       print_number(station.prob_exceed_var_D[lag]),
                       print_number(p_index),
                       print_number(sum([station.prob_decrease_var_D[lag],
                                         station.prob_normal_var_D[lag],
                                         station.prob_exceed_var_D[lag]]))])

#==============================================================================
# CLIMATE AND FORECASTING MAIN PROCESS


def climate(station):
    '''
    Main process for climate
    '''

    # console message
    sys.stdout.write(_("Processing climate "))
    sys.stdout.flush()

    if not os.path.isdir(climate_dir):
        os.makedirs(climate_dir)

    station.climate_dir = \
        os.path.join(climate_dir, station.code + '_' + station.name)   # 'results'
    if not os.path.isdir(station.climate_dir):
        os.makedirs(station.climate_dir)

    station.var_D, station.date_D = read_var_D(station)

    station.var_I, station.date_I = read_var_I(station)

    station.common_period = calculate_common_period(station)

    station.period_start = station.common_period[0][0].year

    station.period_end = station.common_period[-1][0].year

    sys.stdout.write("({0}-{1})...........".format(station.period_start,
                                                   station.period_end))
    sys.stdout.flush()

    station.Lag_0, station.Lag_1, station.Lag_2 = calculate_lags(station)

    station.size_time_series = (len(station.common_period) / 12) - 2

    station.contingencies_tables_percent = contingency_table(station)

    station = result_table(station)

    if not threshold_problem[0] and not threshold_problem[1] and not threshold_problem[2]:
        graphics_climate(station)

    maps_climate(station)

    print _("done")

    return station


def forecasting(station):
    '''
    Main process for forecasting
    '''

    # console message
    sys.stdout.write(_("Processing forecasting ({0}-{1}).......")
                     .format(station.period_start, station.period_end))
    sys.stdout.flush()

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

        a = b = c = d = e = f = g = h = i = 0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][0] == _('yes'):
            a = station.contingencies_tables_percent[lag][station.f_trim - 1][0][0] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][1] == _('yes'):
            b = station.contingencies_tables_percent[lag][station.f_trim - 1][0][1] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][2] == _('yes'):
            c = station.contingencies_tables_percent[lag][station.f_trim - 1][0][2] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][3] == _('yes'):
            d = station.contingencies_tables_percent[lag][station.f_trim - 1][1][0] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][4] == _('yes'):
            e = station.contingencies_tables_percent[lag][station.f_trim - 1][1][1] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][5] == _('yes'):
            f = station.contingencies_tables_percent[lag][station.f_trim - 1][1][2] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][6] == _('yes'):
            g = station.contingencies_tables_percent[lag][station.f_trim - 1][2][0] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][7] == _('yes'):
            h = station.contingencies_tables_percent[lag][station.f_trim - 1][2][1] / 100.0

        if not args.risk_analysis or station.is_sig_risk_analysis[lag][station.f_trim - 1][8] == _('yes'):
            i = station.contingencies_tables_percent[lag][station.f_trim - 1][2][2] / 100.0

        prob_decrease_var_D.append((a * station.f_var_I_B[lag]) +
                                   (d * station.f_var_I_N[lag]) +
                                   (g * station.f_var_I_A[lag]))

        prob_normal_var_D.append((b * station.f_var_I_B[lag]) +
                                 (e * station.f_var_I_N[lag]) +
                                 (h * station.f_var_I_A[lag]))

        prob_exceed_var_D.append((c * station.f_var_I_B[lag]) +
                                 (f * station.f_var_I_N[lag]) +
                                 (i * station.f_var_I_A[lag]))

    station.prob_decrease_var_D = prob_decrease_var_D
    station.prob_normal_var_D = prob_normal_var_D
    station.prob_exceed_var_D = prob_exceed_var_D

    if not threshold_problem[0] and not threshold_problem[1] and not threshold_problem[2]:
        graphics_forecasting(station)

    maps_forecasting(station)

    print _("done")

#==============================================================================
# STATION CLASS
# for storage several variables


class Station:
    '''
    Generic station class
    '''

    def __init__(self):
        pass

#==============================================================================
# MAIN PROCESS


def main():
    '''
    Main process of Jaziku
    '''

    # check python version
    if sys.version_info[0] != 2:
        print_error(_("You version of python is {0}, please use Jaziku with python"
                  " v2.x ").format(sys.version_info[0]))

    # Parser and check arguments
    global args
    args = input_arg.arguments.parse_args()

    # console message
    print _("\n########################### JAZIKU ###########################\n" \
            "## Jaziku is a software for the implementation of composite ##\n" \
            "## analysis metodology between the major indices of climate ##\n" \
            "## variability and major meteorological variables in        ##\n" \
            "## puntual scale.                                           ##\n" \
            "##                                                          ##\n" \
            "## Version {0} - {1}\t                            ##\n" \
            "## Copyright © 2011-2012 IDEAM - Colombia                   ##\n" \
            "##############################################################") \
            .format(global_var.VERSION, global_var.COMPILE_DATE)

    # set period for process if is defined as argument
    if args.period:
        global period_start, period_end
        try:
            period_start = int(args.period.split('-')[0])
            period_end = int(args.period.split('-')[1])
            print _("\nSetting period in: {0}-{1}").format(period_start, period_end)
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

    # if phenomenon below is defined inside arguments
    if args.p_below:
        phenomenon_below = unicode(args.p_below, 'utf-8')
    else:
        phenomenon_below = _('var Ind below')
    # if phenomenon normal is defined inside arguments
    if args.p_normal:
        phenomenon_normal = unicode(args.p_normal, 'utf-8')
    else:
        phenomenon_normal = _('var Ind normal')
    # if phenomenon above is defined inside arguments
    if args.p_above:
        phenomenon_above = unicode(args.p_above, 'utf-8')
    else:
        phenomenon_above = _('var Ind above')

    ### maps_plots_files_climate
    if args.climate:
        # climate dir output result
        global climate_dir
        climate_dir = \
            os.path.join(os.path.splitext(args.stations.name)[0], _('Jaziku-climate'))   # 'results'

        print _("\nSave the result for climate in:\n -> {0}").format(climate_dir)

        if os.path.isdir(climate_dir):
            print _("\n   Warning: the output director for climate process\n" \
                    "   is already exist, Jaziku continue but the results\n" \
                    "   could be mixed or replaced of old output.")
        # created and define csv output file for maps climate
        phenomenon = {0:phenomenon_below, 1:phenomenon_normal, 2:phenomenon_above}
        maps_plots_files_climate = [] # maps_plots_files_climate[lag][month][phenomenon]

        # define maps data files and directories      
        for lag in lags:

            maps_dir = os.path.join(climate_dir, _('maps'))
            maps_data_lag = os.path.join(maps_dir, _('maps-data'), _('lag_{0}').format(lag))

            if not os.path.isdir(maps_data_lag):
                os.makedirs(maps_data_lag)

            # all months in year 1->12
            month_list = []
            for month in range(1, 13):
                categories_list = []
                for category in phenomenon:
                    maps_data_phenom = os.path.join(maps_data_lag, phenomenon[category])

                    if not os.path.isdir(maps_data_phenom):
                        os.makedirs(maps_data_phenom)

                    csv_name = \
                        os.path.join(maps_data_phenom, _(u'map_data_lag_{0}_trim_{1}_{2}.csv')
                                     .format(lag, month, phenomenon[category]))
                    csv_file = csv.writer(open(csv_name, 'w'), delimiter = ';')
                    csv_file.writerow([_('code'), _('lat'), _('lon'), _('pearson'),
                                       _('var_below'), _('var_normal'), _('var_above'),
                                       _('p_index'), _('sum')])
                    categories_list.append(csv_file)

                month_list.append(categories_list)

            maps_plots_files_climate.append(month_list)

    ### maps_plots_files_forecasting
    if args.forecasting:
        # forecasting dir output result
        global forecasting_dir
        forecasting_dir = \
            os.path.join(os.path.splitext(args.stations.name)[0], _('Jaziku-forecasting'))   # 'results'

        print _("\nSave the result for forecasting in:\n -> {0}").format(forecasting_dir)

        if os.path.isdir(forecasting_dir):
            print _("\n   Warning: the output director for forecasting process\n" \
                    "   is already exist, Jaziku continue but the results\n" \
                    "   could be mixed or replaced of old output.")

        # created and define csv output file for maps forecasting
        maps_plots_files_forecasting = [] # maps_plots_files_forecasting[lag]

        # define maps data files and directories
        for lag in lags:

            maps_dir = os.path.join(forecasting_dir, _('maps'), _('maps-data'))

            if not os.path.isdir(maps_dir):
                os.makedirs(maps_dir)

            csv_name = os.path.join(maps_dir, _(u'map_data_lag_{0}.csv')
                                    .format(lag))
            csv_file = csv.writer(open(csv_name, 'w'), delimiter = ';')
            csv_file.writerow([_('code'), _('lat'), _('lon'), _('prob_decrease_var_D'),
                               _('prob_normal_var_D'), _('prob_exceed_var_D'),
                               _('index'), _('sum')])

            maps_plots_files_forecasting.append(csv_file)

    # read stations list from stations file (-station arguments) and process station by station
    stations = csv.reader(args.stations, delimiter = ';')
    for line_station in stations:
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

            # validation type_D
            if station.type_D not in input_arg.types_var_D:
                raise Exception(_("{0} is not valid type for dependence variable")
                                .format(station.type_D))

            station.file_I = open(line_station[6], 'r')
            station.type_I = line_station[7]

            # validation type_I
            if station.type_I not in input_arg.types_var_I:
                raise Exception(_("{0} is not valid type for independence variable")
                                .format(station.type_I))

            station.threshold_below_var_I = line_station[8].replace(',', '.')
            station.threshold_above_var_I = line_station[9].replace(',', '.')


            if args.forecasting:
                if len(line_station) < 20:
                    raise Exception(_("For forecasting process you need define "
                                      "9 probability variables and trimester to "
                                      "process in stations file:"))
                station.f_var_I_B = [float(line_station[10].replace(',', '.')),
                                     float(line_station[13].replace(',', '.')),
                                     float(line_station[16].replace(',', '.'))]
                station.f_var_I_N = [float(line_station[11].replace(',', '.')),
                                     float(line_station[14].replace(',', '.')),
                                     float(line_station[17].replace(',', '.'))]
                station.f_var_I_A = [float(line_station[12].replace(',', '.')),
                                     float(line_station[15].replace(',', '.')),
                                     float(line_station[18].replace(',', '.'))]

                try:
                    station.f_trim = int(line_station[19])
                except:
                    raise Exception(_("Trimester forecasting \"{0}\" is invalid, "
                                      "should be integer number").format(line_station[19]))
                if not (1 <= station.f_trim <= 12):
                    raise Exception(_("Trimester forecasting \"{0}\" is invalid, "
                                      "should be a month valid number (1-12)").format(station.f_trim))

        except Exception, e:
            print_error(_("Reading stations from file \"{0}\" in line {1}:\n")
                        .format(args.stations.name, stations.line_num) +
                        ';'.join(line_station) + "\n\n" + str(e))

        # console message
        print _("\n################# Station: {0} ({1})").format(station.name, station.code)

        # define phenomenon label
        station.phenomenon_below = phenomenon_below
        station.phenomenon_normal = phenomenon_normal
        station.phenomenon_above = phenomenon_above


        # run process (climate, forecasting) from input arguments 
        if args.climate:
            station.maps_plots_files_climate = maps_plots_files_climate
            station = climate(station)

        if args.forecasting:
            # TODO: run forecasting without climate
            if not args.climate:
                print_error(_("sorry, Jaziku can't run forecasting process "
                              "without climate, this issue has not been implemented "
                              "yet, \nplease run again with the option \"-c\""))
            station.maps_plots_files_forecasting = maps_plots_files_forecasting
            forecasting(station)

        if not args.climate and not args.forecasting:
            print_error(_("Neither process (climate, forecasting) were executed, "
                          "\nplease enable this process in arguments: \n'-c, "
                          "--climate' for climate and/or '-f, --forecasting' "
                          "for forecasting."))

        # delete instance 
        del station


# Run main() when call jaziku.py
if __name__ == "__main__":
    main()
