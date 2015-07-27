#!/usr/bin/env python2
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


# Transform data stations:
#
# This script transform from ideam format got from SISDHIM software
# (see a example into docs) to individual data per station ready for
# process with Jaziku, besides, create the structure of runfile with
# all stations processed, but this needs to be complete before run
# with Jaziku.
#
# Use:
#
# Open terminal where saved the file to be processed (i.e INPUT_FILE)
# and run:
#
#     sisdhim2jaziku INPUT_FILE [--start_year START_YEAR]
#                                         [--end_year END_YEAR]
#                                         [--min_years MIN_YEARS]
#

import os
import csv
import argparse
import errno
from calendar import monthrange
from subprocess import call
from clint.textui import colored

from jaziku.utils import output, console, text
from jaziku.utils.geographic import dms2dd
from jaziku.utils.scripts import runfile_skeleton


def main():
    print "\nTRANSFORM DATA SCRIPT FROM IDEAM FORMAT TO JAZIKU FORMAT\n"
    # print colored.yellow("Important: This transform data script version is input valid for Jaziku 0.3.x")

    # -------------------------------------------------------------------------
    # PARSER AND CHECK ARGUMENTS

    # Create parser arguments
    arguments = argparse.ArgumentParser(
        prog="sisdhim2jaziku",
        description=_("This script transform from ideam format got from SISDHIM to Jaziku format."),
        epilog=console.msg_footer(text=True),
        formatter_class=argparse.RawTextHelpFormatter)

    # file input argument
    arguments.add_argument('input_file', type=str, help=_('File input from SISDHIM'))

    # start year
    arguments.add_argument('--start_year', type=int, default=None,
                           help=_('put in runfile only time series have contain this year by below.'), required=False)

    # end year
    arguments.add_argument('--end_year', type=int, default=None,
                           help=_('put in runfile only time series have contain this year by above.'), required=False)

    # min years
    arguments.add_argument('--min_years', type=int, default=None,
                           help=_('put in runfile only time series have contain at least this minimum of years.'),
                           required=False)

    arg = arguments.parse_args()

    # check arguments
    if arg.start_year is not None and arg.end_year is not None and arg.min_years is not None:
        print colored.red("ERROR: you can't defined all arguments 'start_year', "
                          "'end_year' and 'min_years' at the same time\n")
        exit()

    if not os.path.isfile(arg.input_file):
        print colored.red("ERROR: no such file or directory: {0}\n".format(arg.input_file))
        exit()

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

    def prepare_directories(variable):
        # TODO: fix when the name is the same directory, without extension
        path = os.path.join(dir_output_name, text.slugify(variable['name']), dir_var_D_stations)
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    # -------------------------------------------------------------------------
    # prepare runfile

    def prepare_runfile(variable):
        runfile_name = "runfile.csv"
        runfile = open(os.path.join(dir_output_name, text.slugify(variable['name']), runfile_name), 'w')

        # write the base of runfile
        runfile.write(runfile_skeleton.raw)
        # define the runfile csv format to write the stations
        return csv.writer(runfile, delimiter=';')

    # -------------------------------------------------------------------------
    # prepare input file

    # test if dos2unix exists
    if not console.which('dos2unix'):
        print colored.red("Error: this script need the program 'dos2unix' for\n"
                          "convert and clean all 'DOS' characters inside the SISDHIM format.\n"
                          "Install 'dos2unix' from repositories of your Linux distribution.\n")
        exit()

    print "\nConverting and cleaning all 'DOS' characters inside the SISDHIM format of input file:"

    # standard clean with dos2unix
    call([console.which('dos2unix'), '-f', arg.input_file], shell=False)
    # convert ^M in extra newline
    call([console.which('dos2unix'), '-f', '-l', arg.input_file], shell=False)
    print ""

    # -------------------------------------------------------------------------
    # utility functions

    def if_station_pass_filters():

        if 'start_year' not in station or 'end_year' not in station:
            return False

        write_in_runfile = None
        if arg.start_year is not None:
            if arg.start_year >= station['start_year']:
                write_in_runfile = True
            else:
                write_in_runfile = False

        if arg.end_year is not None:
            if arg.end_year <= station['end_year'] and write_in_runfile is not False:
                write_in_runfile = True
            else:
                write_in_runfile = False

        if arg.min_years is not None:
            if arg.min_years <= (station['end_year'] - station['start_year']) and write_in_runfile is not False:
                write_in_runfile = True
            else:
                write_in_runfile = False

        if write_in_runfile is None:
            write_in_runfile = True

        return write_in_runfile

    def file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    # -------------------------------------------------------------------------
    # init some variables

    variables = {}
    station = {}
    name_variable = None
    before_name_variable = None
    frequency_data = None
    in_station_data = False
    in_station_properties = False
    continue_station = False
    starting_new_variable = False
    before_year = None
    len_of_file = file_len(arg.input_file)

    # -------------------------------------------------------------------------
    # process input file and all stations

    with open(arg.input_file, 'rb+') as fileobject:

        for line_num, line in enumerate(fileobject):

            # continue if line is null, empty or with ****
            if not line or not line.strip() or line.strip().startswith("************"):
                # not continue if is reading the name variable
                if line_in_station_properties != 2:
                    continue

            # read station properties
            if in_station_properties:
                # name variable
                if line_in_station_properties == 1:
                    variable_in_line = line.strip().split('       ')[0].strip()
                    if len(variable_in_line.split('(')) == 1:
                        new_name_variable = variable_in_line
                    elif len(variable_in_line.split('(')) == 2:
                        new_name_variable = variable_in_line.split('(')[0].strip()
                    else:
                        new_name_variable = ''.join(variable_in_line.split('(')[:-1]).strip()
                        new_name_variable = new_name_variable.replace(')', '')

                # continue read the name variable if exist
                if line_in_station_properties == 2:

                    if name_variable in variables and (
                                variables[name_variable]['name'].startswith(new_name_variable) or
                                new_name_variable.startswith(variables[name_variable]['name'])):
                        new_name_variable = variables[name_variable]['name']
                    elif line.strip():
                        new_name_variable = new_name_variable + ' ' + line.strip()

                    if new_name_variable not in variables:
                        # save the previous station before to create a variable
                        continue_station = False
                        if 'code' in station and 'name' in station:
                            # write station properties into runfile
                            if if_station_pass_filters() is True:
                                variables[name_variable]['runfile_csv']. \
                                    writerow([station['code'], station['name'], output.number(station['lat']),
                                              output.number(station['lon']), output.number(station['alt']),
                                              station['path']])
                                variables[name_variable]['stations_in_runfile'] += 1
                            # mark the station as processed
                            variables[name_variable]['stations_processed'][(station['code'], station['name'])] = True

                        variable = {}
                        variable['name'] = new_name_variable
                        before_name_variable = name_variable
                        name_variable = new_name_variable

                        prepare_directories(variable)
                        variable['runfile_csv'] = prepare_runfile(variable)
                        variable['stations_processed'] = {}
                        variable['stations_in_runfile'] = 0
                        variables[name_variable] = variable
                        starting_new_variable = True
                    else:
                        before_name_variable = name_variable
                        name_variable = new_name_variable

                # code, name (and year)
                if line_in_station_properties == 3:

                    # only for daily data
                    year = line[59:63].strip()

                    if year and len(year) == 4:
                        year = int(year)
                        # set the frequency_data of input file
                        frequency_data = 'daily'
                    else:
                        frequency_data = 'monthly'

                    code = line[104:114].strip()
                    name = line[114::].strip().replace('/', '_')

                    # check if station is repeat
                    if (code, name) in variables[name_variable]['stations_processed'] and \
                                    variables[name_variable]['stations_processed'][(code, name)] is True:
                        print colored.yellow(
                            "WARNING: detect repeat station for {0} - {1}: ignore and continue".format(code, name))
                        in_station_properties = False
                        in_station_data = False
                    # continue read the same station in the next block
                    elif (code, name) in variables[name_variable]['stations_processed'] and \
                            ('code' in station and 'name' in station) and \
                            (station['code'] == code and station['name'] == name) \
                            and not starting_new_variable:

                        continue_station = True

                        for variable in variables:
                            if variable.startswith(name_variable):
                                name_variable = variable
                        if variables[name_variable]['stations_processed'][(station['code'], station['name'])] is False:
                            print colored.blue(
                                "Continue the station:   {0} - {1}".format(station['code'], station['name']))

                        # check if for daily data the year is repeat
                        if frequency_data == 'daily' and before_year == year:
                            print colored.yellow("WARNING: detected the year {0} is repeat for the same station\n"
                                                 "         save only the data of first year.".format(year))
                            in_station_properties = False
                            in_station_data = False
                    # start new station
                    else:
                        # save the previous station before to create a new station
                        continue_station = False
                        if 'code' in station and 'name' in station and not starting_new_variable:
                            # write station properties into runfile
                            if if_station_pass_filters() is True:
                                variables[before_name_variable]['runfile_csv']. \
                                    writerow([station['code'], station['name'], output.number(station['lat']),
                                              output.number(station['lon']), output.number(station['alt']),
                                              station['path']])
                                variables[before_name_variable]['stations_in_runfile'] += 1
                            # mark the station as processed
                            variables[before_name_variable]['stations_processed'][
                                (station['code'], station['name'])] = True

                        # start the new station
                        station = {}
                        station['code'] = code
                        station['name'] = name
                        if (station['code'], station['name']) in variables[name_variable]['stations_processed'] and \
                                        variables[name_variable]['stations_processed'][
                                            (station['code'], station['name'])] is True:
                            print colored.yellow(
                                "The station {0} - {1} is already exist: Overwriting".format(station['code'],
                                                                                             station['name']))
                        else:
                            print "Processing the station: {0} - {1}".format(station['code'], station['name'])
                            variables[name_variable]['stations_processed'][(station['code'], station['name'])] = False

                        if frequency_data == 'daily':
                            before_year = None
                        if starting_new_variable:
                            starting_new_variable = False

                # latitude
                if line_in_station_properties == 4 and not continue_station:
                    lat_deg = line[14:17].strip()
                    lat_min = line[17:19].strip()
                    lat_loc = line[20:21].strip()

                    lat_dms = dms2dd("{0}:{1}:00".format(lat_deg, lat_min))

                    if lat_loc == "S":
                        lat_dms = -lat_dms

                    station['lat'] = lat_dms
                # longitude
                if line_in_station_properties == 5 and not continue_station:
                    lon_deg = line[14:17].strip()
                    lon_min = line[17:19].strip()
                    lon_loc = line[20:21].strip()

                    lon_dms = dms2dd("{0}:{1}:00".format(lon_deg, lon_min))

                    if lon_loc == "W":
                        lon_dms = -lon_dms

                    station['lon'] = lon_dms
                # altitude
                if line_in_station_properties == 6 and not continue_station:
                    alt = line[14:19].strip()

                    station['alt'] = alt
                # write station info and switch to read the station data
                if line_in_station_properties == 7:
                    if not continue_station:
                        # define path to save file
                        station['file'] = "{0}-{1}.txt".format(station['code'], station['name'])
                        station['path'] = os.path.join(dir_var_D_stations, station['file'])
                        # open to write station
                        station['file_to_write'] \
                            = csv.writer(open(
                            os.path.join(dir_output_name, text.slugify(variables[name_variable]['name']),
                                         station['path']), 'w'), delimiter=' ')
                        if frequency_data == 'monthly':
                            before_year = None

                    in_station_data = True
                    in_station_properties = False
                    if frequency_data == 'daily':
                        months_data = [[], [], [], [], [], [], [], [], [], [], [], []]
                    continue

                line_in_station_properties += 1

            # read station data
            if in_station_data:

                # continue for some special characters inside data
                if line.strip().startswith("MEDIA VECTORIAL"):
                    continue

                if frequency_data == 'monthly':
                    year = line[1:5]
                    try:
                        year = int(year)
                    except:
                        in_station_data = False

                if frequency_data == 'daily':
                    day_to_process = line[11:13]
                    try:
                        day_to_process = int(day_to_process)
                    except:
                        # write data
                        for month in range(0, 12):
                            days_in_month = monthrange(year, month + 1)[1]
                            for day in range(0, days_in_month):
                                station['file_to_write'].writerow(
                                    ["{0}-{1}-{2}".format(year, output.fix_zeros(month + 1), output.fix_zeros(day + 1)),
                                     months_data[month][day]])

                        before_year = year
                        station['end_year'] = year
                        in_station_data = False

                # check if station is repeat
                if continue_station and year < before_year:
                    print colored.yellow(
                        "WARNING: detect repeat station for {0} - {1}: ignore and continue".format(station['code'],
                                                                                                   station['name']))
                    variables[name_variable]['stations_processed'][(station['code'], station['name'])] = True
                    in_station_properties = False
                    in_station_data = False

                if in_station_data:
                    # fill the empty months or days with nan if not exists
                    if before_year is not None:
                        while year > before_year + 1:
                            if frequency_data == 'monthly':
                                for month in range(0, 12):
                                    station['file_to_write'].writerow(
                                        ["{0}-{1}".format(before_year + 1, output.fix_zeros(month + 1)), 'nan'])
                            if frequency_data == 'daily':
                                for month in range(0, 12):
                                    days_in_month = monthrange(before_year + 1, month + 1)[1]
                                    for day in range(0, days_in_month):
                                        station['file_to_write'].writerow(["{0}-{1}-{2}".format(before_year + 1,
                                                                                                output.fix_zeros(
                                                                                                    month + 1),
                                                                                                output.fix_zeros(
                                                                                                    day + 1)), 'nan'])
                            before_year += 1
                    else:
                        # save the first year
                        station['start_year'] = year
                    # get the values when the data are monthly
                    if frequency_data == 'monthly':
                        # write the month values for the year
                        for month in range(0, 12):
                            value = line[12 + 9 * month:19 + 9 * month].strip()
                            if value in ['', '*', '+']:
                                value = 'nan'
                            # for runoff  TODO: check
                            if value == 'seco':
                                value = 0
                            # convert value
                            try:
                                value = round(float(value), 5)
                            except:
                                # for wind or unknown words  TODO: accept wind values
                                value = line[12 + 9 * month:19 + 9 * month].strip()
                            station['file_to_write'].writerow(
                                ["{0}-{1}".format(year, output.fix_zeros(month + 1)), value])
                    # get the values when the data are daily
                    if frequency_data == 'daily':
                        # write the month values for the year
                        for month in range(0, 12):
                            value = line[18 + 9 * month:25 + 9 * month].strip()
                            if value in ['', '*', '+']:
                                value = 'nan'
                            # for runoff  TODO: check
                            if value == 'seco':
                                value = 0
                            # convert value
                            try:
                                value = round(float(value), 5)
                            except:
                                # for wind or unknown words  TODO: accept wind values
                                value = line[18 + 9 * month:27 + 9 * month].strip()

                            months_data[month].append(value)

                    if frequency_data == 'monthly':
                        before_year = year
                        station['end_year'] = year

            # read until start next station (continue or new station)
            if not in_station_properties and not in_station_data:
                if "I D E A M" in line:
                    # start read new block
                    in_station_properties = True
                    line_in_station_properties = 0

                if line_num > len_of_file - 20:
                    # write the last station before finish
                    if if_station_pass_filters() is True:
                        variables[name_variable]['runfile_csv']. \
                            writerow([station['code'], station['name'], output.number(station['lat']),
                                      output.number(station['lon']), output.number(station['alt']), station['path']])
                        variables[name_variable]['stations_in_runfile'] += 1
                    # mark the station as processed
                    variables[name_variable]['stations_processed'][(station['code'], station['name'])] = True
                    # finish
                    break

    print "\nStations processed and inside runfile for " + str(len(variables)) + " different variables :"
    for variable in variables:
        stations_in_runfile = []
        for _station in variables[variable]['stations_processed']:
            if variables[variable]['stations_processed'][_station]:
                stations_in_runfile.append(_station)

        print "  " + str(variable) + ": " + str(len(stations_in_runfile)) + " stations (inside runfile: " + str(
            variables[variable]['stations_in_runfile']) + " stations that pass all filters)"

    print "\nSaving result in: " + os.path.splitext(arg.input_file)[0]
    # print "Saving runfile in: " + os.path.join(os.path.splitext(arg.input_file)[0], runfile_name)
    # print "Saving stations list files in: " + os.path.join(os.path.splitext(arg.input_file)[0], dir_var_D_stations)
    print colored.yellow("Complete the runfile.csv before run with Jaziku")
    print colored.green("\nDone\n")

    exit()
