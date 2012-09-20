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

from jaziku.modules.maps.grid import Grid
from jaziku.utils import globals_vars, console
from jaziku.modules.station import Station


def read_runfile():

    in_config_run = False
    in_station_list = False
    in_grids_list = False

    grid = None
    lines_of_stations = []

    # read line by line the RUNFILE
    for line_in_run_file in globals_vars.run_file:
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
                    "error read line in \"CONFIGURATION RUN\" in runfile,"
                    " line {0}:\n{1}, no was defined.")
                .format(globals_vars.run_file.line_num, line_in_run_file[0]), False)

            if line_in_run_file[0] in globals_vars.config_run:
                # in this case, for python 'disable' is None,
                # then let default value (it is 'None')
                if line_in_run_file[1] == "disable":
                    globals_vars.config_run[line_in_run_file[0]] = False
                elif line_in_run_file[1] == "enable":
                    globals_vars.config_run[line_in_run_file[0]] = True
                else:
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
                        "error read line in \"CONFIGURATION RUN\" in runfile, line {0}:\n{1}")
                    .format(globals_vars.run_file.line_num, line_in_run_file[0]), False)

        # read GRIDS LIST
        if in_grids_list:
            if line_in_run_file[0][0:2] == "##" and line_in_run_file[0] != "################":
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
                    console.msg_error(_("error read line in \"GRIDS LIST\" in runfile, line {0}:\n{1}")
                    .format(globals_vars.run_file.line_num, line_in_run_file[0]), False)

        # read STATIONS LIST
        if in_station_list:
            if line_in_run_file[0][0:2] == "##":
                continue
            lines_of_stations.append([line_in_run_file, globals_vars.run_file.line_num])


    # when climate is disable:
    if not globals_vars.config_run['climate_process']:
        globals_vars.config_run['forecasting_process'] = False
        globals_vars.config_run['maps'] = False

    stations = read_stations(lines_of_stations)

    return stations


def read_stations(lines_of_stations):

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
            station.code = line_station[0]
            station.name = line_station[1]
            station.lat = line_station[2].replace(',', '.')
            station.lon = line_station[3].replace(',', '.')
            station.alt = line_station[4].replace(',', '.')

            if len(line_station) < 12:
                raise Exception(_("Problems with the numbers of parameters inside\n"
                                  "the stations list need for run climate process.\n"))

            station.file_D = open(line_station[5], 'rb')
            station.type_D = globals_vars.config_run['type_var_D']

            station.threshold_below_var_D = line_station[6].replace(',', '.')
            station.threshold_above_var_D = line_station[7].replace(',', '.')

            station.file_I = line_station[8]
            station.type_I = globals_vars.config_run['type_var_I']

            station.threshold_below_var_I = line_station[9].replace(',', '.')
            station.threshold_above_var_I = line_station[10].replace(',', '.')

            station.analysis_interval = line_station[11]

            if station.analysis_interval not in globals_vars.options_analysis_interval:
                raise Exception(_("The analysis interval {0} is invalid,\n"
                                  "should be one of these: {1}")
                .format(station.analysis_interval,
                    ', '.join(globals_vars.options_analysis_interval)))

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

            station.translate_analysis_interval\
                = globals_vars.translate_analysis_interval[globals_vars.options_analysis_interval.index(station.analysis_interval)]

            # if forecasting_process is activated
            if globals_vars.config_run['forecasting_process']:
                if len(line_station) < 22:
                    raise Exception(_("For forecasting process you need define "
                                      "9 probability\n variables and trimester to "
                                      "process in stations file."))
                station.f_var_I_B = [float(line_station[12].replace(',', '.')),
                                     float(line_station[15].replace(',', '.')),
                                     float(line_station[18].replace(',', '.'))]
                station.f_var_I_N = [float(line_station[13].replace(',', '.')),
                                     float(line_station[16].replace(',', '.')),
                                     float(line_station[19].replace(',', '.'))]
                station.f_var_I_A = [float(line_station[14].replace(',', '.')),
                                     float(line_station[17].replace(',', '.')),
                                     float(line_station[20].replace(',', '.'))]

                station.forecasting_date = line_station[21]

        except Exception, e:
            console.msg_error_line_stations(station, e)

        stations.append(station)

    return stations