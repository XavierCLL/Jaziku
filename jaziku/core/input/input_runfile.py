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

from jaziku.env import globals_vars, config_run
from jaziku.core.station import Station
from jaziku.modules.maps.grid import Grid
from jaziku.utils import  console


def get_float(item):
    try:
        return float(str(item.replace(',', '.')).replace(',', '.'))
    except:
        return item

def get_integer(item):
    try:
        return int(str(item.replace(',', '.')).replace(',', '.'))
    except:
        return item


def read_runfile():
    """
    Read all settings and all stations from runfile

    :return:
        stations class list

    :global:
        config_run.get['*']
    """

    in_config_run = False
    in_station_list = False
    in_grids_list = False

    grid = None
    lines_of_stations = []

    runfile_open = open(globals_vars.ARGS.runfile, 'rb')

    # delete all NULL byte inside the runfile.csv
    runfile = (x.replace('\0', '') for x in runfile_open)

    # open runfile as csv
    runfile = csv.reader(runfile, delimiter=globals_vars.INPUT_CSV_DELIMITER)

    # -------------------------------------------------------------------------
    # read line by line the RUNFILE

    for line_in_run_file in runfile:
        # trim all items in line_in_run_file
        line_in_run_file = [i.strip() for i in line_in_run_file if i != '']

        # if line is null o empty, e.g. empty but with tabs or spaces
        if not line_in_run_file or not line_in_run_file[0].strip() or line_in_run_file == []:
            continue

        # is the first line, start read configuration run
        if not in_config_run and not in_grids_list and not in_station_list:
            if line_in_run_file[1] == "CONFIGURATION RUN":
                in_config_run = True
                continue

        # read CONFIGURATION RUN
        if in_config_run:
            if line_in_run_file[0].startswith("#"):
                continue

            if not len(line_in_run_file) >= 2:
                console.msg_error(_(
                    "error read line in 'CONFIGURATION RUN' in runfile,"
                    " line {0}:\n{1}, no was defined.")
                .format(runfile.line_num, line_in_run_file[0]), False)

            if line_in_run_file[0] in config_run.settings:
                # in this case, for python 'disable' is None,
                # then let default value (it is 'None')
                if line_in_run_file[1] == "disable":
                    config_run.settings[line_in_run_file[0]] = False
                elif line_in_run_file[1] == "enable":
                    config_run.settings[line_in_run_file[0]] = True
                else:
                    if len(line_in_run_file) == 2:
                        try:
                            config_run.settings[line_in_run_file[0]] = get_float(line_in_run_file[1])
                        except:
                            config_run.settings[line_in_run_file[0]] = line_in_run_file[1]
                    else: # >2
                        try:
                            config_run.settings[line_in_run_file[0]] = [get_float(item) for item in line_in_run_file[1::]]
                        except:
                            config_run.settings[line_in_run_file[0]] = [item for item in line_in_run_file[1::]]
            else:
                if line_in_run_file[1] == "GRIDS LIST":
                    in_config_run = False
                    in_grids_list = True
                    continue
                elif line_in_run_file[1] == "STATIONS LIST":
                    in_config_run = False
                    in_station_list = True
                else:
                    console.msg_error(_(
                        "error read line in 'CONFIGURATION RUN' in runfile, line {0}:\n{1}")
                    .format(runfile.line_num, line_in_run_file[0]), False)

        # read GRIDS LIST
        if in_grids_list:
            if line_in_run_file[0].startswith("#") and line_in_run_file[0] != "####################":
                if grid:
                    del grid
                grid = Grid()
                continue

            if line_in_run_file[0] in Grid.fields:
                if len(line_in_run_file) == 1:
                    setattr(Grid.all_grids[-1], line_in_run_file[0], None)
                if len(line_in_run_file) == 2:
                    try:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], get_float(line_in_run_file[1]))
                    except:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], line_in_run_file[1])
                if len(line_in_run_file) == 3:
                    try:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], [get_float(line_in_run_file[1]),
                                                                          get_float(line_in_run_file[2])])
                    except:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], [line_in_run_file[1], line_in_run_file[2]])
            else:
                if line_in_run_file[1] == "STATIONS LIST":
                    in_grids_list = False
                    in_station_list = True
                else:
                    console.msg_error(_("error read line in 'GRIDS LIST' in runfile, line {0}:\n{1}")
                    .format(runfile.line_num, line_in_run_file[0]), False)

        # read STATIONS LIST
        if in_station_list:
            if line_in_run_file[0].startswith("#"):
                continue
            lines_of_stations.append([line_in_run_file, runfile.line_num])

    runfile_open.close()
    del runfile

    # -------------------------------------------------------------------------
    # post-process after read the runfile

    # when climate is disable:
    if not config_run.settings['climate_process']:
        config_run.settings['forecast_process'] = False
        config_run.settings['maps'] = False

    # if forecast_process is activated
    if config_run.settings['forecast_process']:
        try:

            globals_vars.forecast_phen_below = [get_float(config_run.settings['lag_0_phen_below']),
                                                get_float(config_run.settings['lag_1_phen_below']),
                                                get_float(config_run.settings['lag_2_phen_below'])]
            globals_vars.forecast_phen_normal = [get_float(config_run.settings['lag_0_phen_normal']),
                                                 get_float(config_run.settings['lag_1_phen_normal']),
                                                 get_float(config_run.settings['lag_2_phen_normal'])]
            globals_vars.forecast_phen_above = [get_float(config_run.settings['lag_0_phen_above']),
                                                get_float(config_run.settings['lag_1_phen_above']),
                                                get_float(config_run.settings['lag_2_phen_above'])]
        except:
            console.msg_error(_("Problems with the 9 probability values for forecast process\n"
                                "defined in runfile, these must be a numbers, please check it."), False)


    # if path_to_file_var_I is relative convert to absolute, except if is 'internal'
    if not os.path.isabs(config_run.settings["path_to_file_var_I"]) and\
       not config_run.settings["path_to_file_var_I"] == 'internal':
        config_run.settings["path_to_file_var_I"] \
            = os.path.abspath(os.path.join(os.path.dirname(globals_vars.ARGS.runfile),
                                           config_run.settings["path_to_file_var_I"]))

    # Set type and units for variables D and I
    # var D
    if '(' and ')' in config_run.settings['type_var_D']:
        string = config_run.settings['type_var_D']
        # get type
        config_run.settings['type_var_D'] = string[0:string.index('(')].strip()
        # get units
        globals_vars.units_var_D = string[string.index('(') + 1:string.index(')')].strip()
    else:
        if config_run.settings['type_var_D'] in globals_vars.UNITS_FOR_TYPES_VAR_D:
            globals_vars.units_var_D = globals_vars.UNITS_FOR_TYPES_VAR_D[config_run.settings['type_var_D']]
        else:
            globals_vars.units_var_D = '--'
    # var I
    if '(' and ')' in config_run.settings['type_var_I']:
        string = config_run.settings['type_var_I']
        # get type
        config_run.settings['type_var_I'] = string[0:string.index('(')].strip()
        # get units
        globals_vars.units_var_I = string[string.index('(') + 1:string.index(')')].strip()
    else:
        if config_run.settings['type_var_I'] in globals_vars.UNITS_FOR_TYPES_VAR_I:
            globals_vars.units_var_I = globals_vars.UNITS_FOR_TYPES_VAR_I[config_run.settings['type_var_I']]
        else:
            globals_vars.units_var_I = '--'

    # -------------------------------------------------------------------------
    # read stations:
    # makes all stations base on all lines of stations list previously read
    stations = read_stations(lines_of_stations)

    return stations


def read_stations(lines_of_stations):
    """
    Read raw line of stations and make a list class stations
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
            station.lat = line_station[2].replace(',', '.')
            station.lon = line_station[3].replace(',', '.')
            station.alt = line_station[4].replace(',', '.')

            station.var_D.type_series = config_run.settings['type_var_D']
            #station.file_D = open(line_station[5], 'rb')
            station.var_D.set_file(line_station[5])

            station.var_I.type_series = config_run.settings['type_var_I']
            #station.file_I = config_run.get['path_to_file_var_I']
            station.var_I.set_file(config_run.settings['path_to_file_var_I'])

        except Exception, e:
            console.msg_error_line_stations(station, e)

        stations.append(station)

    return stations
