#!/usr/bin/env python2
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


# Transform data stations:
#
# This script transform a particular input stations (see file
# transform_data_stations_input_example.csv) to individual data per
# station ready for process with Jaziku program, besides, create
# basic structure of station list file with station name and link to file
# dep var(before processed) for run with Jaziku, but this needs to be complete.
#
# Use:
#
# Open terminal where saved this script and file to process(i.e FILE_DATA.csv)
# and run:
#
#     python transform_data_stations.py FILE_DATA.csv
#

import csv
import os
import sys

if len(sys.argv) < 2:
    print "Error, missing argument.\nUse: python {0} FILE_DATA.csv".format(sys.argv[0])
    exit()

print "\nProcessing file: {0}".format(sys.argv[1])

#csv file from arguments
csv_data_input = sys.argv[1]
#extract list name stations
dir_stations_output = csv_data_input.split('.')[0]

stations_dir = "dependent_var_files"

stations_list_name = "stations_list.csv"
csv_stations_list = csv.writer(open(stations_list_name, 'w'), delimiter = ';')

#get values from file input
reader = csv.reader(open(csv_data_input, 'rb'), delimiter = ';')
is_first_time_run = True
values = []
for row in reader:
    if is_first_time_run:
        stations = row[2::]
        is_first_time_run = False
    else:
        values.append(row)

#get number of years
years = 0
for line in values:
    if line[1] == '1':
        years += 1
    else:
        break

is_first_time_run = True
csv_stations = []
for year in range(years):

        if is_first_time_run:
            is_first_time_run = False

            for station in stations:
                if not os.path.isdir(stations_dir):
                    os.makedirs(stations_dir)
                file_name = os.path.join(stations_dir, station)
                csv_stations.append(csv.writer(open(file_name + ".txt", 'w'), delimiter = '\t'))
                #write station list
                csv_stations_list.writerow(["(code)", station, "(lat)", "(lon)", file_name + ".txt",
                                            "(type var dep)", "(dir var indep)", "(type var indep)",
                                            "(threshold below)", "(threshold above)", "(forecasting options...)"])

        for month in range(12):

            for number, station in enumerate(csv_stations):
                station.writerow(["{0}-{1}".format(values[month * years + year][0], values[month * years + year][1]), values[month * years + year][number + 2]])

print "\nSaving result in dir: {0}/".format(stations_dir)
print "\nSaving stations list file: {0}\n(basic structure with station name and link to file dep var)".format(stations_list_name)
print "\nDone"
