#!/usr/bin/env python2
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


# Transform data stations:
#
# This script transform from ideam format got from SISDIM software
# (see a example into docs) to individual data per station ready for
# process with Jaziku, besides, create the structure of runfile with
# all stations processed, but this needs to be complete before run
# with Jaziku.
#
# Use:
#
# Open terminal where saved the file to be processed (i.e INPUT_FILE.bin)
# and run:
#
#     ideamFormat2jazikuFormat INPUT_FILE.bin
#

import sys
import os
import csv
from subprocess import call
from clint.textui import colored
import errno

from jaziku.utils import output, console, text
from jaziku.utils.geographic import dms2dd
from jaziku.utils.input_format_converters import runfile_skeleton

def main():
    if len(sys.argv) < 2:
        print "Error, missing argument.\nUse: python2 {0} IDEAM_FORMAT_FILE".format(sys.argv[0])
        exit()

    print "\nTRANSFORM DATA SCRIPT FROM IDEAM FORMAT TO JAZIKU FORMAT\n"
    #print colored.yellow("Important: This transform data script version is input valid for Jaziku 0.3.x")

    #csv file from arguments
    file_input = sys.argv[1]

    if not os.path.isfile(file_input):
        print "ERROR: no such file or directory: {0}\n".format(file_input)
        exit()

    print "Processing file: " + colored.green(file_input)

    # -------------------------------------------------------------------------
    # variables

    variables = {}

    # -------------------------------------------------------------------------
    # prepare names directories

    dir_output_name = os.path.abspath(os.path.splitext(file_input)[0])

    # next TODO
    if len([e for e in os.path.splitext(file_input) if e]) <= 1:
        dir_output_name += "_"

    dir_var_D_stations = "var_D_files"

    # -------------------------------------------------------------------------
    # prepare directories

    def prepare_directories(variable):
        # TODO: fix when the name is the same directory, without extension
        path = os.path.join(dir_output_name, text.slugify(variable['name']), dir_var_D_stations)
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

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
    # prepare filein

    # test if dos2unix exists
    if not console.which('dos2unix'):
        print colored.red("Error: this script need the program 'dos2unix' for\n"
                          "convert and clean all 'DOS' characters inside the SISDIM format.\n"
                          "Install 'dos2unix' from repositories of your Linux distribution.\n")
        exit()

    print "\nConverting and cleaning all 'DOS' characters inside the SISDIM format:"

    # standard clean with dos2unix
    call([console.which('dos2unix'), '-f', file_input], shell=False)
    # convert ^M in extra newline
    call([console.which('dos2unix'), '-f', '-l', file_input], shell=False)
    print ""

    # -------------------------------------------------------------------------
    # process filein and all stations

    def fix_zeros(dt):
        return '0'+str(dt) if len(str(dt))<2 else str(dt)

    in_station_data = False
    in_station_properties = False
    station = {}

    continue_station = False
    all_stations_processed = 0
    before_line = "MINIMOS"

    with open(file_input,'rb+') as fileobject:

        for line in fileobject:

            # continue if line is null o empty
            if not line or not line.strip():
                # not continue if is reading the name variable
                if line_in_station_properties != 2:
                    continue

            # read station properties
            if in_station_properties:
                # name variable
                if line_in_station_properties == 1:
                    name_variable = line[:100].strip().split('(')[0].strip()
                # continue read the name variable if exist
                if line_in_station_properties == 2:
                    if line.strip():
                        name_variable = name_variable + ' ' + line.strip()

                    if name_variable not in variables:
                        variable = {}
                        variable['name'] = name_variable
                        if not continue_station:
                            prepare_directories(variable)
                            variable['runfile_csv'] = prepare_runfile(variable)
                        variable['stations_processed'] = {}
                        variables[name_variable] = variable
                        variables['stations'] = []

                # code and name
                if line_in_station_properties == 3:
                    code = line[104:114].strip()
                    name = line[114::].strip().replace('/','_')
                    if continue_station:
                        if station['code'] != code or station['name'] != name:
                            print colored.red("Error: the station continue but with different name or code ({0} - {1})".format(station['code'], station['name']))
                            exit()
                        for variable in variables:
                            if variable.startswith(name_variable):
                                name_variable = variable
                        if variables[name_variable]['stations_processed'][(station['code'],station['name'])] is False:
                            print colored.blue("Continue the station:   {0} - {1}".format(station['code'], station['name']))
                    if not continue_station:
                        station = {}
                        station['code'] = code
                        station['name'] = name
                        if (station['code'],station['name']) in variables[name_variable]['stations_processed'] and  \
                           variables[name_variable]['stations_processed'][(station['code'],station['name'])] is True:
                            print colored.yellow("The station {0} - {1} is already exist: Overwriting".format(station['code'], station['name']))
                        else:
                            print "Processing the station: {0} - {1}".format(station['code'], station['name'])
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
                if line_in_station_properties == 9:
                    if not continue_station:
                        # define path to save file
                        station['file'] = "{0}-{1}.txt".format(station['code'], station['name'])
                        station['path'] = os.path.join(dir_var_D_stations, station['file'])

                        # write station properties into runfile
                        if (station['code'],station['name']) in variables[name_variable]['stations_processed'] and \
                           variables[name_variable]['stations_processed'][(station['code'],station['name'])] is True:
                            print colored.yellow("But not write the same station into the runfile")
                        else:
                            variables[name_variable]['runfile_csv'].writerow([station['code'], station['name'], output.number(station['lat']),
                                                              output.number(station['lon']), output.number(station['alt']), station['path']])

                        # open to write station
                        station['file_to_write'] \
                            = csv.writer(open(os.path.join(dir_output_name, text.slugify(variables[name_variable]['name']), station['path']), 'w'), delimiter=' ')

                        variables[name_variable]['stations_processed'][(station['code'],station['name'])] = False

                    in_station_data = True
                    before_year = None
                    in_station_properties = False
                    before_line = line
                    continue

                line_in_station_properties += 1

            # read station data
            if in_station_data:

                year = line[1:5]
                try:
                    year = int(year)
                except:
                    in_station_data = False

                if in_station_data:
                    # fill the empty years with nan
                    if before_year is not None:
                        while year != before_year+1:
                            for month in range(0,12):
                                station['file_to_write'].writerow(["{0}-{1}".format(before_year+1,fix_zeros(month+1)), 'nan'])
                            before_year += 1
                    # write the month values for the year
                    for month in range(0,12):
                        value = line[12+9*month:19+9*month].strip()
                        if value in ['','*','+']:
                            value = 'nan'
                        # for runoff  TODO: check
                        if value == 'seco':
                            value = 0
                        # convert value
                        try:
                            value = round(float(value), 5)
                        except:
                            # for wind or unknown words  TODO: accept wind values
                            value = 'unknown'

                        station['file_to_write'].writerow(["{0}-{1}".format(year,fix_zeros(month+1)), value])
                    before_line = line
                    before_year = year


            # read until start next station (continue or new station)
            if not in_station_properties and not in_station_data:
                if line.strip().startswith("I D E A M"):
                    if before_line.strip().startswith("MINIMOS"):
                        continue_station = False
                        if 'code' in station and 'name' in station:
                            variables[name_variable]['stations_processed'][(station['code'],station['name'])] = True
                            all_stations_processed += 1
                        del station
                    else:
                        continue_station = True

                    # start new station
                    in_station_properties = True
                    line_in_station_properties = 0

                before_line = line

    print "\nStations processed: " + str(all_stations_processed)
    print "Saving result in: " + os.path.splitext(file_input)[0]
    #print "Saving runfile in: " + os.path.join(os.path.splitext(file_input)[0], runfile_name)
    #print "Saving stations list files in: " + os.path.join(os.path.splitext(file_input)[0], dir_var_D_stations)
    print colored.yellow("Complete the runfile.csv before run with Jaziku")
    print colored.green("\nDone\n")

    del variables
    exit()


