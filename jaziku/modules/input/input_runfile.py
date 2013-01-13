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

from jaziku.modules.maps.grid import Grid
from jaziku.utils import globals_vars, console
from jaziku.modules.station import Station


def read_runfile():
    """
    Read all settings and all stations from runfile

    :return:
        stations class list

    :global:
        globals_vars.config_run['*']
    """

    in_config_run = False
    in_station_list = False
    in_grids_list = False

    grid = None
    lines_of_stations = []

    # -------------------------------------------------------------------------
    # read line by line the RUNFILE

    for line_in_run_file in globals_vars.runfile:
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
            if line_in_run_file[0][0:3] == "## ":
                continue

            if len(line_in_run_file) <= 1:
                console.msg_error(_(
                    "error read line in 'CONFIGURATION RUN' in runfile,"
                    " line {0}:\n{1}, no was defined.")
                .format(globals_vars.runfile.line_num, line_in_run_file[0]), False)

            if line_in_run_file[0] in globals_vars.config_run:
                # in this case, for python 'disable' is None,
                # then let default value (it is 'None')
                if line_in_run_file[1] == "disable":
                    globals_vars.config_run[line_in_run_file[0]] = False
                elif line_in_run_file[1] == "enable":
                    globals_vars.config_run[line_in_run_file[0]] = True
                else:
                    try:
                        globals_vars.config_run[line_in_run_file[0]] = float(str(line_in_run_file[1].replace(',', '.')).replace(',', '.'))
                    except:
                        globals_vars.config_run[line_in_run_file[0]] = line_in_run_file[1]
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
                    .format(globals_vars.runfile.line_num, line_in_run_file[0]), False)

        # read GRIDS LIST
        if in_grids_list:
            if line_in_run_file[0][0:2] == "##" and line_in_run_file[0] != "####################":
                if grid:
                    del grid
                grid = Grid()
                continue

            if line_in_run_file[0] in Grid.fields:
                if len(line_in_run_file) == 1:
                    setattr(Grid.all_grids[-1], line_in_run_file[0], None)
                if len(line_in_run_file) == 2:
                    try:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], float(line_in_run_file[1].replace(',', '.')))
                    except:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], line_in_run_file[1])
                if len(line_in_run_file) == 3:
                    try:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], [float(line_in_run_file[1].replace(',', '.')),
                                                                          float(line_in_run_file[2].replace(',', '.'))])
                    except:
                        setattr(Grid.all_grids[-1], line_in_run_file[0], [line_in_run_file[1], line_in_run_file[2]])
            else:
                if line_in_run_file[1] == "STATIONS LIST":
                    in_grids_list = False
                    in_station_list = True
                else:
                    console.msg_error(_("error read line in 'GRIDS LIST' in runfile, line {0}:\n{1}")
                    .format(globals_vars.runfile.line_num, line_in_run_file[0]), False)

        # read STATIONS LIST
        if in_station_list:
            if line_in_run_file[0][0:2] == "##":
                continue
            lines_of_stations.append([line_in_run_file, globals_vars.runfile.line_num])

    # -------------------------------------------------------------------------
    # post-process after read the runfile

    # when climate is disable:
    if not globals_vars.config_run['climate_process']:
        globals_vars.config_run['forecasting_process'] = False
        globals_vars.config_run['maps'] = False

    # if forecasting_process is activated
    if globals_vars.config_run['forecasting_process']:
        try:

            globals_vars.forecasting_phen_below = [float(str(globals_vars.config_run['lag_0_phen_below']).replace(',', '.')),
                                                   float(str(globals_vars.config_run['lag_1_phen_below']).replace(',', '.')),
                                                   float(str(globals_vars.config_run['lag_2_phen_below']).replace(',', '.'))]
            globals_vars.forecasting_phen_normal = [float(str(globals_vars.config_run['lag_0_phen_normal']).replace(',', '.')),
                                                    float(str(globals_vars.config_run['lag_1_phen_normal']).replace(',', '.')),
                                                    float(str(globals_vars.config_run['lag_2_phen_normal']).replace(',', '.'))]
            globals_vars.forecasting_phen_above = [float(str(globals_vars.config_run['lag_0_phen_above']).replace(',', '.')),
                                                   float(str(globals_vars.config_run['lag_1_phen_above']).replace(',', '.')),
                                                   float(str(globals_vars.config_run['lag_2_phen_above']).replace(',', '.'))]
        except:
            console.msg_error(_("Problems with the 9 probability values for forecasting process\n"
                                "defined in runfile, these must be a numbers, please check it."), False)

        globals_vars.forecasting_date = globals_vars.config_run['forecasting_date']

    # Set type and units for variables D and I
    # var D
    if '(' and ')' in globals_vars.config_run['type_var_D']:
        string = globals_vars.config_run['type_var_D']
        # get type
        globals_vars.config_run['type_var_D'] = string[0:string.index('(')].strip()
        # get units
        globals_vars.units_var_D = string[string.index('(')+1:string.index(')')].strip()
    else:
        if globals_vars.config_run['type_var_D'] in globals_vars.units_of_types_var_D:
            globals_vars.units_var_D = globals_vars.units_of_types_var_D[globals_vars.config_run['type_var_D']]
        else:
            globals_vars.units_var_D = '--'
    # var I
    if '(' and ')' in globals_vars.config_run['type_var_I']:
        string = globals_vars.config_run['type_var_I']
        # get type
        globals_vars.config_run['type_var_I'] = string[0:string.index('(')].strip()
        # get units
        globals_vars.units_var_I = string[string.index('(')+1:string.index(')')].strip()
    else:
        if globals_vars.config_run['type_var_I'] in globals_vars.units_of_types_var_I:
            globals_vars.units_var_I = globals_vars.units_of_types_var_I[globals_vars.config_run['type_var_I']]
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
            station.name = line_station[1]
            station.lat = line_station[2].replace(',', '.')
            station.lon = line_station[3].replace(',', '.')
            station.alt = line_station[4].replace(',', '.')

            station.var_D.type_series = globals_vars.config_run['type_var_D']
            #station.file_D = open(line_station[5], 'rb')
            station.var_D.set_file(line_station[5])

            station.var_I.type_series = globals_vars.config_run['type_var_I']
            #station.file_I = globals_vars.config_run['path_to_file_var_I']
            station.var_I.set_file(globals_vars.config_run['path_to_file_var_I'])

        except Exception, e:
            console.msg_error_line_stations(station, e)

        stations.append(station)

    return stations