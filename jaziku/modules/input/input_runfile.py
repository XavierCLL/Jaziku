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

from ..maps.grid import Grid
from ...utils import globals_vars, console


def read_runfile(run_file):

    in_config_run = False
    in_station_list = False
    in_grids_list = False

    grid = None
    stations = []

    # read line by line the RUNFILE
    for line_in_run_file in run_file:
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
                .format(run_file.line_num, line_in_run_file[0]), False)

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
                    .format(run_file.line_num, line_in_run_file[0]), False)

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
                    .format(run_file.line_num, line_in_run_file[0]), False)

        # read STATIONS LIST
        if in_station_list:
            if line_in_run_file[0][0:2] == "##":
                continue
            stations.append([line_in_run_file, run_file.line_num])

    return stations