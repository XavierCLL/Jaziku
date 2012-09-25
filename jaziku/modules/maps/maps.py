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

import os
import sys
import csv
import numpy
from subprocess import call

import interpolation
from grid import search_and_set_internal_grid, set_particular_grid
from ncl import make_ncl_file
from jaziku.utils import globals_vars, console


def maps(grid):
    """
    In Maps, jaziku in order to predict variable values in sites not sampled, through Kriging
    spatial interpolation method displays the general trends and spatial continuity of afectation
    scenarios results of Climate and Forecast Modules
    """
    # set name_grid, country and grid_path
    if isinstance(grid.grid, list):
        if len(grid.grid) == 1:
            grid.grid_name = grid.grid_fullname = grid.country = grid.grid[0]
        else:
            grid.grid_name = grid.grid[0]
            grid.grid_fullname = grid.grid[0] + " (" + grid.grid[1] + ")"
            grid.country = grid.grid[1]
        if not grid.shape_path:
            grid.grid_path = os.path.join(grid.grid[1], grid.grid[0])
    else:
        grid.grid_name = grid.grid_fullname = grid.country = grid.grid
        if not grid.shape_path:
            grid.grid_path = os.path.join(grid.grid, grid.grid)

    print "\n################# {0}: {1}".format(_("MAP"), grid.grid_fullname)

    # check if grid defined path to shape else search and set internal shape, lat and lon of grid
    if not grid.shape_path:
        search_and_set_internal_grid(grid)
    else:
        set_particular_grid(grid)

    # check the latitude and longitude
    if grid.minlat >= grid.maxlat or\
       grid.minlon >= grid.maxlon or\
       - 90 > grid.minlat > 90 or\
       - 180 > grid.minlat > 180:
        console.msg_error(_("The latitude and/or longitude are wrong,\n"
                            "these should be decimal degrees."), False)

    # set variables for grid
    grid.grid_properties()

    grid.print_grid_properties()

    ## Matrix with real data and null value for empty value
    # base_matrix[lat, lon]
    global base_matrix
    base_matrix = numpy.matrix(numpy.empty([grid.lat_size, grid.lon_size]))
    # initialize matrix with null value
    base_matrix.fill(globals_vars.VALID_NULL[1])

    phenomenon = {0: globals_vars.phenomenon_below,
                  1: globals_vars.phenomenon_normal,
                  2: globals_vars.phenomenon_above}

    def process_map():
        # copy matrix from base_matrix
        matrix = base_matrix.copy()
        # read values from saved file and set points on matrix
        open_file = open(file_map_points, 'rb')
        csv_file = csv.reader(open_file, delimiter=';')
        first_line = True
        for line in csv_file:
            if first_line:
                first_line = False
                continue
            latitude = float(line[1].replace(',', '.'))
            longitude = float(line[2].replace(',', '.'))

            if grid.if_running["correlation"]:
                index = float(line[3].replace(',', '.'))  # get pearson value
            if grid.if_running["climate"] or grid.if_running["forecasting"]:
                index = float(line[7].replace(',', '.'))  # get index value
                # set the index value on matrix

            matrix, point_state = grid.set_point_on_grid(matrix, latitude, longitude, index)

            if point_state == "nan" and message_warning:
                console.msg(
                    _("\n > WARNING: The point lat:{lat} lon:{lon}\n"
                      "   of the station code: {code} was not added\n"
                      "   because the value of index is \"nan\" (null) .").
                    format(lat=latitude, lon=longitude, code=line[0]), color='yellow', newline=False)
            if point_state == "point not added" and message_warning:
                console.msg(
                    _("\n > WARNING: The point lat:{lat} lon:{lon}\n"
                      "   of the station code: {code} was not added\n"
                      "   because the point is outside of the grid ...").
                    format(lat=latitude, lon=longitude, code=line[0]), color='yellow', newline=False)
            if point_state in [_("average"), _("maximum"), _("minimum")] and message_warning:
                console.msg(
                    _("\n > WARNING: for the point lat:{lat} lon:{lon}\n"
                      "   Jaziku detect overlapping of two values, Jaziku\n"
                      "   will put the {state} value .................").
                    format(lat=latitude, lon=longitude, state=point_state), color='yellow', newline=False)
            if point_state == _("neither") and message_warning:
                console.msg(
                    _("\n > WARNING: for the point lat:{lat} lon:{lon}\n"
                      "   Jaziku detect overlapping of two values, Jaziku\n"
                      "   will not put the {state} values ............").
                    format(lat=latitude, lon=longitude, state=point_state), color='yellow', newline=False)

        open_file.close()
        del csv_file

        # save matrix for interpolation
        open_file = open(inc_file, 'wb')
        open_file.write("Cont_data" + '\n')

        # convert matrix (column per column) to linear values
        matrix_vector = numpy.asarray(matrix.T).reshape(-1)

        # save values to INC file
        for value in matrix_vector:
            if int(value) == globals_vars.VALID_NULL[1]:
                open_file.write(str(int(value)) + '\n')
            else:
                open_file.write(str(value) + '\n')
        open_file.write('/')
        open_file.close()

        # make ordinary kriging interpolation with HPGL
        matrix_interpolation = interpolation.ordinary_kriging(grid, inc_file)

        #matrix_interpolation = np.matrix(matrix_interpolation)

        #matrix_interpolation_vector = np.asarray(matrix_interpolation.T).reshape(-1)

        # save file for NCL
        open_ncl_file = open(ncl_data, 'wb')
        tsv_file = csv.writer(open_ncl_file, delimiter='\t')
        tsv_file.writerow([_('lat'), _('lon'), _('value')])

        for lon_index, lon_value in enumerate(grid.lon_coordinates):
            for lat_index, lat_value in enumerate(grid.lat_coordinates):
                tsv_file.writerow([lat_value, lon_value, matrix_interpolation[lat_index][lon_index]])

        open_ncl_file.close()
        del tsv_file

        # make ncl file for map
        base_path_file = os.path.join(base_path, base_file)
        # make and write ncl file for ncl process
        ncl_file = make_ncl_file(grid, base_path_file, globals_vars)
        devnull = os.open(os.devnull, os.O_WRONLY)

        ## COLORMAP
        # setting path to colormap
        path_to_colormap = os.path.join(globals_vars.ROOT_DIR, 'data', 'maps', 'colormaps')
        # set colormap ncl variable into variables system
        os.environ["NCARG_COLORMAPS"] = path_to_colormap

        ## NCL
        # call ncl command for make maps base on ncl_file
        call(["ncl", os.path.abspath(ncl_file)], shell=False, stdout=devnull)

        ## TRANSFORM IMAGE
        # trim png created
        image_file = os.path.join(os.path.abspath(base_path_file) + ".png").replace(" ", r"\ ")

        call(["convert", image_file, "-trim", image_file], shell=False)

        # delete files
        #os.remove(os.path.abspath(base_path_file) + ".INC")
        #os.remove(os.path.abspath(base_path_file) + ".ncl")
        #os.remove(os.path.abspath(base_path_file) + ".tsv")

        del matrix

    grid.if_running = {}

    # -------------------------------------------------------------------------
    # Process maps for CLIMATE

    if globals_vars.maps['climate']:

        grid.if_running["climate"] = True
        grid.if_running["correlation"] = False
        grid.if_running["forecasting"] = False

        print _("Processing maps for climate:")

        # walking file by file of maps directory and make interpolation and map for each file
        for analysis_interval in globals_vars.options_analysis_interval:

            if globals_vars.maps_files_climate[analysis_interval] is None:
                continue

            # console message
            if analysis_interval == 'trimester':
                console.msg("                {0} ..................... ".format(analysis_interval), newline=False)
            else:
                console.msg("                {0}\t....................... ".format(analysis_interval), newline=False)

            for lag in globals_vars.lags:

                # all months in year 1->12
                for month in range(1, 13):

                    if analysis_interval == 'trimester':
                        for category in [0, 1, 2]:  # phenomenons var_I
                            # show only once
                            if lag == globals_vars.lags[0] and month == 1 and category == 0:
                                message_warning = True
                            else:
                                message_warning = False

                            # file where saved points for plot map
                            file_map_points = globals_vars.maps_files_climate[analysis_interval][lag][month - 1][category]

                            # save matrix for interpolation
                            base_path = os.path.join(os.path.dirname(file_map_points), grid.grid_name)

                            # make dir with the name of grid
                            if not os.path.isdir(base_path):
                                os.makedirs(base_path)

                            base_file = _(u'Map_lag_{0}_{1}_{2}')\
                                .format(lag, globals_vars.trim_text[month - 1], phenomenon[category])

                            grid.date = globals_vars.trim_text[month - 1]
                            grid.lag = lag

                            # file for interpolation
                            inc_file = os.path.join(base_path, base_file + ".INC")

                            # save file for NCL
                            ncl_data = os.path.join(base_path, base_file + ".tsv")

                            process_map()

                    else:
                        # range based on analysis interval
                        if analysis_interval == '5days':
                            range_analysis_interval = [1, 6, 11, 16, 21, 26]
                        if analysis_interval == '10days':
                            range_analysis_interval = [1, 11, 21]
                        if analysis_interval == '15days':
                            range_analysis_interval = [1, 16]
                        for day in range(len(range_analysis_interval)):
                            for category in [0, 1, 2]:  # phenomenons var_I
                                # show only once
                                if lag == globals_vars.lags[0] and month == 1 and category == 0 and day == 0:
                                    message_warning = True
                                else:
                                    message_warning = False

                                # file where saved points for plot map
                                file_map_points = globals_vars.maps_files_climate[analysis_interval][lag][month - 1][day][category]

                                # save matrix for interpolation
                                base_path = os.path.join(os.path.dirname(file_map_points), grid.grid_name)

                                # make dir with the name of grid
                                if not os.path.isdir(base_path):
                                    os.makedirs(base_path)

                                base_file = _(u'Map_lag_{0}_{1}_{2}')\
                                    .format(lag,
                                            globals_vars.month_text[month - 1] + "_" + str(range_analysis_interval[day]),
                                            phenomenon[category])

                                grid.date = globals_vars.month_text[month - 1] + "_" + str(range_analysis_interval[day])
                                grid.lag = lag

                                # file for interpolation
                                inc_file = os.path.join(base_path, base_file + ".INC")

                                # save file for NCL
                                ncl_data = os.path.join(base_path, base_file + ".tsv")

                                process_map()

            console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # Process maps for CORRELATION

    if globals_vars.maps['correlation']:

        grid.if_running["climate"] = False
        grid.if_running["correlation"] = True
        grid.if_running["forecasting"] = False

        print _("Processing maps for correlation:")

        # walking file by file of maps directory and make interpolation and map for each file
        for analysis_interval in globals_vars.options_analysis_interval:

            if globals_vars.maps_files_climate[analysis_interval] is None:
                continue

            # console message
            if analysis_interval == 'trimester':
                console.msg("                {0} ..................... ".format(analysis_interval), newline=False)
            else:
                console.msg("                {0}\t....................... ".format(analysis_interval), newline=False)

            for lag in globals_vars.lags:

                # all months in year 1->12
                for month in range(1, 13):

                    if analysis_interval == 'trimester':
                        category = 1  # normal
                        # show only once
                        if lag == globals_vars.lags[0] and month == 1:
                            message_warning = True
                        else:
                            message_warning = False

                        # file where saved points for plot map
                        file_map_points = globals_vars.maps_files_climate[analysis_interval][lag][month - 1][category]

                        # save matrix for interpolation
                        base_path = os.path.join(globals_vars.climate_dir, _('maps'),
                            globals_vars.translate_analysis_interval[globals_vars.options_analysis_interval.index(analysis_interval)],
                            _('lag_{0}').format(lag),
                            _('Correlation'),
                            grid.grid_name)

                        # make dir with the name of grid
                        if not os.path.isdir(base_path):
                            os.makedirs(base_path)

                        base_file = _(u'Map_correlation_lag_{0}_{1}').format(lag, globals_vars.trim_text[month - 1])

                        grid.date = globals_vars.trim_text[month - 1]
                        grid.lag = lag

                        # file for interpolation
                        inc_file = os.path.join(base_path, base_file + ".INC")

                        # save file for NCL
                        ncl_data = os.path.join(base_path, base_file + ".tsv")

                        process_map()

                    else:
                        # range based on analysis interval
                        if analysis_interval == '5days':
                            range_analysis_interval = [1, 6, 11, 16, 21, 26]
                        if analysis_interval == '10days':
                            range_analysis_interval = [1, 11, 21]
                        if analysis_interval == '15days':
                            range_analysis_interval = [1, 16]
                        for day in range(len(range_analysis_interval)):
                            category = 1  # phenomenons var_I
                            # show only once
                            if lag == globals_vars.lags[0] and month == 1 and day == 0:
                                message_warning = True
                            else:
                                message_warning = False

                            # file where saved points for plot map
                            file_map_points = globals_vars.maps_files_climate[analysis_interval][lag][month - 1][day][category]

                            # save matrix for interpolation
                            base_path = os.path.join(globals_vars.climate_dir, _('maps'),
                                globals_vars.translate_analysis_interval[globals_vars.options_analysis_interval.index(analysis_interval)],
                                _('lag_{0}').format(lag),
                                _('Correlation'),
                                grid.grid_name)

                            # make dir with the name of grid
                            if not os.path.isdir(base_path):
                                os.makedirs(base_path)

                            base_file = _(u'Map_correlation_lag_{0}_{1}')\
                            .format(lag, globals_vars.month_text[month - 1] + "_" + str(range_analysis_interval[day]))

                            grid.date = globals_vars.month_text[month - 1] + "_" + str(range_analysis_interval[day])
                            grid.lag = lag

                            # file for interpolation
                            inc_file = os.path.join(base_path, base_file + ".INC")

                            # save file for NCL
                            ncl_data = os.path.join(base_path, base_file + ".tsv")

                            process_map()

            console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # Process maps for FORECASTING

    if globals_vars.config_run['forecasting_process'] and  globals_vars.maps['forecasting']:

        grid.if_running["climate"] = False
        grid.if_running["correlation"] = False
        grid.if_running["forecasting"] = True

        print _("Processing maps for forecasting:")

        # walking file by file of maps directory and make interpolation and map for each file
        for analysis_interval in ['5days', '10days', '15days', 'trimester']:

            if globals_vars.maps_files_forecasting[analysis_interval] == {}:
                continue

            # console message
            if analysis_interval == 'trimester':
                console.msg("                {0} ..................... ".format(analysis_interval), newline=False)
            else:
                console.msg("                {0}\t....................... ".format(analysis_interval), newline=False)

            for forecasting_date in globals_vars.maps_files_forecasting[analysis_interval]:

                for lag in globals_vars.lags:
                    # show only once
                    if lag == globals_vars.lags[0]:
                        message_warning = True
                    else:
                        message_warning = False

                    # file where saved points for plot map
                    file_map_points = globals_vars.maps_files_forecasting[analysis_interval][forecasting_date][lag]
                    # save matrix for interpolation
                    base_path = os.path.join(os.path.dirname(file_map_points), grid.grid_name)

                    # make dir with the name of grid
                    if not os.path.isdir(base_path):
                        os.makedirs(base_path)

                    base_file = _(u'Map_lag_{0}_{1}').format(lag, forecasting_date)

                    grid.date = forecasting_date
                    grid.lag = lag

                    # file for interpolation
                    inc_file = os.path.join(base_path, base_file + ".INC")

                    # save file for NCL
                    ncl_data = os.path.join(base_path, base_file + ".tsv")

                    process_map()

            console.msg(_("done"), color='green')

    del base_matrix