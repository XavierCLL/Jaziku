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

from jaziku import env
from jaziku.core.station import Station
from jaziku.modules.maps.grid import Grid
from jaziku.utils import  console, input


def read_runfile():
    """Read all settings and all stations from runfile

    :return:
        stations class list

    :global:
        env.config_run.get['*']
    """

    in_config_run = False
    in_maps = False
    in_grids_list = False
    in_station_list = False

    grid = None
    lines_of_stations = []

    runfile_open = open(env.globals_vars.ARGS.runfile, 'rb')

    # delete all NULL byte inside the runfile.csv
    runfile = (x.replace('\0', '') for x in runfile_open)

    # open runfile as csv
    runfile = csv.reader(runfile, delimiter=env.globals_vars.INPUT_CSV_DELIMITER)

    def set_settings(runfile, line):
        # check if this settings was defined
        if not len(line) >= 2:
            line.append(None)

        # in this case, for python 'disable' is None,
        # then let default value (it is 'None')
        if line[1] == "disable":
            env.config_run.settings[line[0]] = False
        elif line[1] == "enable":
            env.config_run.settings[line[0]] = True
        else:
            if len(line) == 2:
                # save value of this settings as simple item
                try:
                    env.config_run.settings[line[0]] = input.to_float(line[1])
                except:
                    env.config_run.settings[line[0]] = line[1]
            else: # >2
                # save values of this settings as list
                try:
                    env.config_run.settings[line[0]] = [input.to_float(item) for item in line[1::]]
                except:
                    env.config_run.settings[line[0]] = [item for item in line[1::]]

    # -------------------------------------------------------------------------
    # read line by line the RUNFILE

    for line_in_runfile in runfile:

        # if line is null o empty, e.g. empty but with tabs or spaces
        if not line_in_runfile or not line_in_runfile[0].strip() or line_in_runfile == []:
            continue

        if line_in_runfile[0].strip() not in ['forecast_var_I_lag_0','forecast_var_I_lag_1','forecast_var_I_lag_2']:
            # trim all items in line_in_runfile and clean empty items
            line_in_runfile = [i.strip() for i in line_in_runfile if i != '']
        else:
            # trim all items in line_in_runfile and NOT clean empty items
            line_in_runfile = [i.strip() for i in line_in_runfile]

        # is the first line, start read configuration run
        if not in_config_run and not in_maps and not in_grids_list and not in_station_list:
            if line_in_runfile[1] == "CONFIGURATION RUN":
                in_config_run = True
                continue

        # read CONFIGURATION RUN
        if in_config_run:
            # skip line if start with # but if this is not a starts the next section
            if line_in_runfile[0].startswith("#") and not \
                (len(line_in_runfile) >= 2 and line_in_runfile[1] == "MAPS"):
                continue

            if line_in_runfile[0] in env.config_run.settings:
                # set this line as settings and save in env.config_run.settings
                set_settings(runfile, line_in_runfile)
            else:
                if len(line_in_runfile) >= 2 and line_in_runfile[1] == "MAPS":
                    in_config_run = False
                    in_maps = True
                elif len(line_in_runfile) >= 2 and line_in_runfile[1] == "STATIONS LIST":
                    in_config_run = False
                    in_station_list = True
                else:
                    console.msg_error(_(
                        "error read line in 'CONFIGURATION RUN' in runfile,\n"
                        "unknown option in line {0}:\n\n"
                        "{1}")
                    .format(runfile.line_num, line_in_runfile[0]), False)

        # read MAPS
        if in_maps:
            # skip line if start with # but if this is not a starts the next section
            if line_in_runfile[0].startswith("#") and not \
                (line_in_runfile[0].startswith("## GRID DEFINITION") or \
                (len(line_in_runfile) >= 2 and line_in_runfile[1] == "STATIONS LIST")):
                continue

            if line_in_runfile[0] in env.config_run.settings:
                # set this line as settings and save in env.config_run.settings
                set_settings(runfile, line_in_runfile)
            else:
                if line_in_runfile[0].startswith("## GRID DEFINITION"):
                    in_maps = False
                    in_grids_list = True
                elif len(line_in_runfile) >= 2 and line_in_runfile[1] == "STATIONS LIST":
                    in_maps = False
                    in_station_list = True
                else:
                    console.msg_error(_(
                        "error read line in 'MAPS' in runfile,\n"
                        "unknown option in line {0}:\n\n"
                        "{1}")
                    .format(runfile.line_num, line_in_runfile[0]), False)

        # read GRIDS LIST
        if in_grids_list:
            # create instances of Grid
            if line_in_runfile[0].startswith("## GRID DEFINITION"):
                if grid:
                    # delete old instance if exists
                    del grid
                grid = Grid()
                continue

            # skip line if start with # but if this is not a starts the next section
            if line_in_runfile[0].startswith("#") and not \
                (len(line_in_runfile) >= 2 and line_in_runfile[1] == "STATIONS LIST"):
                continue

            if line_in_runfile[0] in Grid.fields:
                # check if this settings was defined
                if len(line_in_runfile) == 1:
                    if env.config_run.settings['maps']:
                        console.msg_error(_(
                            "error reading the settings line in runfile,"
                            " line {0}:\n'{1}' no was defined.")
                        .format(runfile.line_num, line_in_runfile[0]), False)
                if len(line_in_runfile) == 2:
                    try:
                        setattr(Grid.all_grids[-1], line_in_runfile[0], input.to_float(line_in_runfile[1]))
                    except:
                        setattr(Grid.all_grids[-1], line_in_runfile[0], line_in_runfile[1])
                if len(line_in_runfile) >= 3:
                    try:
                        setattr(Grid.all_grids[-1], line_in_runfile[0], [input.to_float(item) for item in line_in_runfile[1::]])
                    except:
                        setattr(Grid.all_grids[-1], line_in_runfile[0], [item for item in line_in_runfile[1::]])
            else:
                if len(line_in_runfile) >= 2 and line_in_runfile[1] == "STATIONS LIST":
                    in_grids_list = False
                    in_station_list = True
                else:
                    console.msg_error(_("error read line in 'GRIDS LIST' in runfile, line {0}:\n{1}")
                    .format(runfile.line_num, line_in_runfile[0]), False)

        # read STATIONS LIST
        if in_station_list:
            # skip line if start with #
            if line_in_runfile[0].startswith("#"):
                continue
            lines_of_stations.append([line_in_runfile, runfile.line_num])

    runfile_open.close()
    del runfile

    # -------------------------------------------------------------------------
    # post-process after read the runfile

    # when climate is disable:
    if not env.config_run.settings['climate_process']:
        env.config_run.settings['forecast_process'] = False
        env.config_run.settings['maps'] = False

    # if path_to_file_var_I is relative convert to absolute, except if is 'internal'
    if not os.path.isabs(env.config_run.settings["path_to_file_var_I"]) and\
       not env.config_run.settings["path_to_file_var_I"] == 'internal':
        env.config_run.settings["path_to_file_var_I"] \
            = os.path.abspath(os.path.join(os.path.dirname(env.globals_vars.ARGS.runfile),
                                           env.config_run.settings["path_to_file_var_I"]))

    # Set type and units for variables D and I
    # var D
    if env.config_run.settings['type_var_D'] is not None and '(' and ')' in env.config_run.settings['type_var_D']:
        string = env.config_run.settings['type_var_D']
        # get type
        env.var_D.TYPE_SERIES = string[0:string.index('(')].strip()
        # get units
        env.var_D.units = string[string.index('(') + 1:string.index(')')].strip()
    else:
        env.var_D.TYPE_SERIES = env.config_run.settings['type_var_D']
        if env.var_D.TYPE_SERIES in env.var_D.INTERNAL_UNITS:
            env.var_D.units = env.var_D.INTERNAL_UNITS[env.var_D.TYPE_SERIES]
        else:
            env.var_D.units = '--'
    # var I
    if env.config_run.settings['type_var_I'] is not None and '(' and ')' in env.config_run.settings['type_var_I']:
        string = env.config_run.settings['type_var_I']
        # get type
        env.var_I.TYPE_SERIES = string[0:string.index('(')].strip()
        # get units
        env.var_I.units = string[string.index('(') + 1:string.index(')')].strip()
    else:
        env.var_I.TYPE_SERIES = env.config_run.settings['type_var_I']
        if env.var_I.TYPE_SERIES in env.var_I.INTERNAL_UNITS:
            env.var_I.units = env.var_I.INTERNAL_UNITS[env.var_I.TYPE_SERIES]
        else:
            env.var_I.units = '--'

    # -------------------------------------------------------------------------
    # read stations:
    # makes all stations base on all lines of stations list previously read
    stations = read_stations(lines_of_stations)

    return stations


def read_stations(lines_of_stations):
    """Read raw line of stations and make a list class stations
    with all parameters in runfile for each station.

    :return:
        stations class list
    """

    stations = []

    # process each station from stations list
    for line_station, line_num in lines_of_stations:
        # trim all items in line_station
        line_station = [i.strip() for i in line_station]

        # if line of station is null o empty, e.g. empty but with tabs or spaces
        if not line_station or not line_station[0].strip() or line_station[0].strip()[0] == "#":
            continue

        # new instance of station
        station = Station()

        station.line_station = line_station
        station.line_num = line_num

        try:
            if len(line_station) < 6:
                raise Exception(_("Problems with the numbers of parameters inside\n"
                                  "the stations list need for run climate process.\n"))

            station.code = line_station[0]
            station.name = unicode(line_station[1], 'utf-8')
            station.lat = input.to_float(line_station[2])
            station.lon = input.to_float(line_station[3])
            station.alt = input.to_float(line_station[4])

            station.var_D.type_series = env.var_D.TYPE_SERIES
            #station.file_D = open(line_station[5], 'rb')
            station.var_D.set_file(line_station[5])

            station.var_I.type_series = env.var_I.TYPE_SERIES
            #station.file_I = env.config_run.get['path_to_file_var_I']
            station.var_I.set_file(env.config_run.settings['path_to_file_var_I'])

        except Exception as error:
            console.msg_error_line_stations(station, error)

        stations.append(station)

    return stations
