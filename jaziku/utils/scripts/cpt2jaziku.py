#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright © 2011-2015 IDEAM
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
# var_D (before processed) for run with Jaziku, but this needs to be complete.
#
# Use:
#
# Open terminal where saved the file to process(i.e FILE_DATA.csv)
# and run:
#
#     cpt2jaziku FILE_DATA.csv
#
# This script is installed together with Jaziku, and this needs some
# Jaziku libraries.
#

import csv
import os
import errno
import argparse
from subprocess import call
from clint.textui import colored

from jaziku.utils import console
from jaziku.utils.scripts import runfile_skeleton, normalize_format


def main():

    print "\nTRANSFORM DATA SCRIPT FROM CLIMATE PREDICTABILITY TOOL FORMAT TO JAZIKU FORMAT\n"

    # -------------------------------------------------------------------------
    # PARSER AND CHECK ARGUMENTS

    # Create parser arguments
    arguments = argparse.ArgumentParser(
                     prog="cpt2jaziku",
                     description=_("This script transform from Climate Predictability Tool format to Jaziku format."),
                     epilog=console.msg_footer(text=True),
                     formatter_class=argparse.RawTextHelpFormatter)

    # file input argument
    arguments.add_argument('input_file', type=str, help=_('CPT file input'))

    arg = arguments.parse_args()

    print "Processing file: " + colored.green(arg.input_file)

    # -------------------------------------------------------------------------
    # prepare names directories

    dir_output_name = os.path.abspath(os.path.splitext(arg.input_file)[0])

    # next TODO
    if len([e for e in os.path.splitext(arg.input_file) if e]) <= 1:
        dir_output_name += "_"

    dir_var_D_stations = "var_D_files"

    # -------------------------------------------------------------------------
    # prepare directories

    def prepare_directories():
        path = os.path.join(dir_output_name, dir_var_D_stations)
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    # -------------------------------------------------------------------------
    # prepare runfile

    def prepare_runfile():
        runfile_name = "runfile.csv"
        runfile = open(os.path.join(dir_output_name, runfile_name), 'w')

        # write the base of runfile
        runfile.write(runfile_skeleton.raw)
        # define the runfile csv format to write the stations
        return csv.writer(runfile, delimiter=';')

    # -------------------------------------------------------------------------
    # prepare input file

    # test if dos2unix exists
    if not console.which('dos2unix'):
        print colored.red("Error: this script need the program 'dos2unix' for\n"
                          "convert and clean all 'DOS' characters inside the CPT format.\n"
                          "Install 'dos2unix' from repositories of your Linux distribution.\n")
        exit()

    print "\nConverting and cleaning all 'DOS' characters inside the CPT format of input file:"

    # standard clean with dos2unix
    call([console.which('dos2unix'), '-f', arg.input_file], shell=False)
    # convert ^M in extra newline
    call([console.which('dos2unix'), '-f', '-l', arg.input_file], shell=False)
    print ""

    # -------------------------------------------------------------------------
    # process input file and all stations

    prepare_directories()

    stations_list_name = "stations_list.csv"
    runfile = prepare_runfile()

    # get values from file input
    with open(arg.input_file, 'rb') as csvfile:
        #dialect = csv.Sniffer().sniff(csvfile.read(4096))
        #csvfile.seek(0)
        #reader = csv.reader(csvfile, dialect)
        reader = csv.reader(csvfile, delimiter='\t')

        values = []
        for idx, line in enumerate(reader):
            if idx == 0:
                stations_list = line[2::]
            elif idx == 1:
                if line[0] == 'LAT':
                    latitude = line[2::]
                else:
                    latitude = None
                    values.append(line)
            elif idx == 2:
                if line[0] == 'LON':
                    longitude = line[2::]
                else:
                    longitude = None
                    values.append(line)
            else:
                values.append(line)

    # get number of years (counts based on numbers of januaries)
    years = 0
    for line in values:
        if line[1] == '1':
            years += 1
        else:
            break

    is_first_time_run = True
    stations_files = []
    for year in range(years):

        if is_first_time_run:
            is_first_time_run = False

            for idx_station, station_name in enumerate(stations_list):

                file_name = os.path.join(dir_output_name, dir_var_D_stations, station_name)
                stations_files.append(open(file_name + ".txt", 'w'))
                lat = latitude[idx_station] if latitude is not None else 'lat'
                lon = longitude[idx_station] if longitude is not None else 'lon'
                # write station list
                runfile.writerow(['code', station_name, lat, lon, 'alt', os.path.join(dir_var_D_stations, station_name + ".txt")])

        for month in range(12):
            for number, station_file in enumerate(stations_files):
                csv_file = csv.writer(station_file, delimiter=' ')
                csv_file.writerow(["{0}-{1}".format(values[month * years + year][0], values[month * years + year][1]), values[month * years + year][number + 2]])
                station_file.flush()

    # applying normalize format for each station
    for station_file in stations_files:
        normalize_format.main(station_file.name, make_backup=False)
        station_file.close()

    print "\nSaving result in dir: " + colored.green(dir_output_name)
    print "\nSaving stations list file: " + colored.green(stations_list_name)
    print colored.yellow("\nComplete the stations_list.csv file before running with Jaziku")
    print colored.green("\nDone\n")
