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
import numpy
from subprocess import call

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.modules.maps import interpolation
from jaziku.modules.maps.grid import search_and_set_internal_grid, set_particular_grid
from jaziku.modules.maps.ncl import make_ncl_file
from jaziku.utils import console, watermarking, format_out, output
from jaziku.modules.maps.grid import Grid


def check_basic_requirements_for_maps():

    console.msg(_("\nChecking basic requirements for maps:"), newline=False)

    ## NCL

    # test if ncl exists
    if not console.which('ncl'):
        console.msg_error(_("Jaziku can't execute the 'ncl' command for make maps,\n"
                            "please check that ncl is include into PATH variable in your\n"
                            "system. For more information read: http://goo.gl/4dAeH"))

    # first check if NCARG_ROOT is defined into operation system
    if not os.environ.get('NCARG_ROOT'):
        console.msg_error(_('The NCARG_ROOT variable is not defined in your system,\n'
                            'please defined NCARG_ROOT where you have installed NCL.\n'
                            'For more information read: http://goo.gl/4dAeH'))

    # second check if NCARG_ROOT is right
    if not os.path.isdir(os.environ.get('NCARG_ROOT')) or\
       not os.path.isfile(os.path.join(os.environ.get('NCARG_ROOT'),'/lib/ncarg/nclscripts/csm/gsn_code.ncl')) or\
       not os.path.isfile(os.path.join(os.environ.get('NCARG_ROOT'),'/lib/ncarg/nclscripts/csm/gsn_csm.ncl')) or\
       not os.path.isfile(os.path.join(os.environ.get('NCARG_ROOT'),'/lib/ncarg/nclscripts/csm/contributed.ncl')):
        console.msg_error(_('The NCARG_ROOT variable is defined in your system,\n'
                            'but there are problems for found nclscripts files,\n'
                            'please check the NCARG_ROOT variable in your system.\n'
                            'For more information read: http://goo.gl/4dAeH'))

    ## test if 'convert' command exists
    if not console.which('convert'):
        console.msg_error(_("Jaziku can't execute the 'convert' command for transform image,\n"
                            "please check that 'imagemagick' is installed in your system.\n"
                            "For more information read Jaziku install instructions."))

    console.msg(_("done"), color='green')


def maps(grid):
    """
    In Maps, jaziku in order to predict variable values in sites not sampled, through Kriging
    spatial interpolation method displays the general trends and spatial continuity of affectation
    scenarios results of Climate and Forecast Modules
    """

    # restart counter
    Grid.maps_created_in_grid = 0

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
                            "these must be decimal degrees."), False)

    # set variables for grid
    grid.grid_properties()

    grid.print_grid_properties()

    ## Matrix with real data and null value for empty value
    # base_matrix[lat, lon]
    global base_matrix
    base_matrix = numpy.matrix(numpy.empty([grid.lat_size, grid.lon_size]))
    # initialize matrix with null value
    base_matrix.fill(env.globals_vars.VALID_NULL[1])

    if env.config_run.settings['class_category_analysis'] == 3:
        var_I_category_labels_list \
            = [env.config_run.settings['var_I_category_labels']['below'],
               env.config_run.settings['var_I_category_labels']['normal'],
               env.config_run.settings['var_I_category_labels']['above']]
    if env.config_run.settings['class_category_analysis'] == 7:
        var_I_category_labels_list \
            = [env.config_run.settings['var_I_category_labels']['below3'],
               env.config_run.settings['var_I_category_labels']['below2'],
               env.config_run.settings['var_I_category_labels']['below1'],
               env.config_run.settings['var_I_category_labels']['normal'],
               env.config_run.settings['var_I_category_labels']['above1'],
               env.config_run.settings['var_I_category_labels']['above2'],
               env.config_run.settings['var_I_category_labels']['above3']]

    def process_map():
        # add counter of maps created in this grid
        Grid.maps_created_in_grid += 1
        # copy matrix from base_matrix
        matrix = base_matrix.copy()
        # read values from saved file and set points on matrix
        open_file = open(file_map_points, 'rb')
        csv_file = csv.reader(open_file, delimiter=env.globals_vars.INPUT_CSV_DELIMITER)
        first_line = True
        marks_stations = []
        for line in csv_file:
            if first_line:
                first_line = False
                continue

            # get lat and lon from Map_Data
            latitude = float(line[1].replace(',', '.'))
            longitude = float(line[2].replace(',', '.'))

            # get index from Map_Data
            if grid.if_running["correlation"]:
                index = float(line[3].replace(',', '.'))  # get pearson value
            if grid.if_running["climate"] or grid.if_running["forecast"]:
                if env.config_run.settings['class_category_analysis'] == 3:
                    index = float(line[8].replace(',', '.'))  # get index value
                if env.config_run.settings['class_category_analysis'] == 7:
                    index = float(line[12].replace(',', '.'))  # get index value

            # set the index value on matrix
            matrix, point_state = grid.set_point_on_grid(matrix, latitude, longitude, index)

            marks_stations.append([latitude, longitude, index])

            if point_state == "nan" and message_warning:
                console.msg(
                    _("\n > WARNING: The point lat:{lat} lon:{lon}\n"
                      "   of the station code: {code} was not added\n"
                      "   because the value of index is 'nan' (null) .").
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

        # save values to .INC file
        for value in matrix_vector:
            if int(value) == env.globals_vars.VALID_NULL[1]:
                open_file.write(str(int(value)) + '\n')
            else:
                open_file.write(str(value) + '\n')
        open_file.write('/')
        open_file.close()

        # make ordinary kriging interpolation with HPGL
        matrix_interpolation = interpolation.ordinary_kriging(grid, inc_file)

        # if all values are identical, change the last value for that ncl plot the color of value
        def are_all_values_identical_2d(L):
            return all(len(set(i)) <= 1 for i in L)

        if are_all_values_identical_2d(matrix_interpolation):
            matrix_interpolation[-1][-1] -= 5

        # TODO: test if interpolation worked

        #matrix_interpolation = np.matrix(matrix_interpolation)

        #matrix_interpolation_vector = np.asarray(matrix_interpolation.T).reshape(-1)

        # save .TSV interpolation file for NCL
        interpolation_file = open(tsv_interpolation_file, 'wb')
        tsv_file = csv.writer(interpolation_file, delimiter='\t')
        tsv_file.writerow([_('lat'), _('lon'), _('value')])

        for lon_index, lon_value in enumerate(grid.lon_coordinates):
            for lat_index, lat_value in enumerate(grid.lat_coordinates):
                tsv_file.writerow([lat_value, lon_value, matrix_interpolation[lat_index][lon_index]])

        interpolation_file.close()
        del tsv_file

        # save .TSV stations file for NCL (marks_stations)
        stations_file = open(tsv_stations_file, 'wb')
        tsv_file = csv.writer(stations_file, delimiter='\t')
        tsv_file.writerow([_('lat'), _('lon'), _('value')])

        for mark_station in marks_stations:
            tsv_file.writerow(mark_station)

        stations_file.close()
        del tsv_file

        # make ncl file for map
        base_path_file = os.path.join(base_path, base_file)
        # make and write ncl file for ncl process
        ncl_file = make_ncl_file(grid, base_path_file, env.globals_vars)
        devnull = os.open(os.devnull, os.O_WRONLY)

        ## COLORMAP
        # setting path to colormap
        path_to_colormap = os.path.join(env.globals_vars.JAZIKU_DIR, 'data', 'maps', 'colormaps')
        # set colormap ncl variable into variables system
        os.environ["NCARG_COLORMAPS"] = path_to_colormap

        ## NCL
        # call ncl command for make maps base on ncl_file
        call(["ncl", os.path.abspath(ncl_file)], shell=False, stdout=devnull)

        # TODO: test if ncl worked

        ## TRANSFORM IMAGE
        # trim png created
        image_file = os.path.join(os.path.abspath(base_path_file) + ".png").replace(" ", r"\ ")

        call(["convert", image_file, "-trim", image_file], shell=False)

        # stamp logo
        watermarking.logo(os.path.abspath(base_path_file) + ".png")

        # TODO: test if convert worked

        # delete files
        #os.remove(os.path.abspath(base_path_file) + ".INC")
        #os.remove(os.path.abspath(base_path_file) + ".ncl")
        #os.remove(os.path.abspath(base_path_file) + ".tsv")
        #os.remove(os.path.abspath(base_path_file) + "_stations.tsv")

        del matrix

    grid.if_running = {}

    # -------------------------------------------------------------------------
    # Process maps for CLIMATE

    if env.config_run.settings['maps']['climate']:

        grid.if_running["climate"] = True
        grid.if_running["correlation"] = False
        grid.if_running["forecast"] = False

        print _("Processing maps for climate:")

        # console message
        if env.config_run.settings['analysis_interval'] == 'trimester':
            console.msg("                {0} ..................... ".format(env.config_run.settings['analysis_interval']), newline=False)
        else:
            console.msg("                {0}\t....................... ".format(env.config_run.settings['analysis_interval']), newline=False)

        # walking file by file of maps directory and make interpolation and map for each file
        for lag in env.config_run.settings['lags']:

            # all months in year 1->12
            for month in range(1, 13):

                if env.config_run.settings['analysis_interval'] == 'trimester':
                    for var_I_idx, label in enumerate(var_I_category_labels_list):
                        label = label.strip().replace(' ','_')
                        # show only once
                        if lag == env.config_run.settings['lags'][0] and month == 1 and var_I_idx == 0:
                            message_warning = True
                        else:
                            message_warning = False

                        # file where saved points for plot map
                        file_map_points = env.globals_vars.maps_files_climate[lag][month - 1][var_I_idx]

                        # save matrix for interpolation
                        base_path = os.path.join(os.path.dirname(file_map_points), grid.grid_name)

                        # make dir with the name of grid
                        output.make_dirs(base_path)

                        base_file = _(u'Map_lag_{0}_{1}_{2}')\
                            .format(lag, format_out.trimester_in_initials(month - 1), label)

                        grid.date = format_out.trimester_in_initials(month - 1)
                        grid.lag = lag

                        # file for interpolation
                        inc_file = os.path.join(base_path, base_file + ".INC")

                        # save file for NCL
                        tsv_interpolation_file = os.path.join(base_path, base_file + ".tsv")
                        tsv_stations_file = os.path.join(base_path, base_file + "_stations.tsv")

                        process_map()

                else:
                    # range based on analysis interval
                    range_analysis_interval = get_range_analysis_interval()

                    for day in range(len(range_analysis_interval)):
                        for var_I_idx, label in enumerate(var_I_category_labels_list):
                            label = label.strip().replace(' ','_')
                            # show only once
                            if lag == env.config_run.settings['lags'][0] and month == 1 and var_I_idx == 0 and day == 0:
                                message_warning = True
                            else:
                                message_warning = False

                            # file where saved points for plot map
                            file_map_points = env.globals_vars.maps_files_climate[lag][month - 1][day][var_I_idx]

                            # save matrix for interpolation
                            base_path = os.path.join(os.path.dirname(file_map_points), grid.grid_name)

                            # make dir with the name of grid
                            output.make_dirs(base_path)

                            base_file = _(u'Map_lag_{0}_{1}_{2}')\
                                .format(lag,
                                        format_out.month_in_initials(month - 1) + "_" + str(range_analysis_interval[day]),
                                        label)

                            grid.date = format_out.month_in_initials(month - 1) + "_" + str(range_analysis_interval[day])
                            grid.lag = lag

                            # file for interpolation
                            inc_file = os.path.join(base_path, base_file + ".INC")

                            # save file for NCL
                            tsv_interpolation_file = os.path.join(base_path, base_file + ".tsv")
                            tsv_stations_file = os.path.join(base_path, base_file + "_stations.tsv")

                            process_map()

        console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # Process maps for CORRELATION

    if env.config_run.settings['maps']['correlation']:

        grid.if_running["climate"] = False
        grid.if_running["correlation"] = True
        grid.if_running["forecast"] = False

        print _("Processing maps for correlation:")

        # console message
        if env.config_run.settings['analysis_interval'] == 'trimester':
            console.msg("                {0} ..................... ".format(env.config_run.settings['analysis_interval']), newline=False)
        else:
            console.msg("                {0}\t....................... ".format(env.config_run.settings['analysis_interval']), newline=False)

        # walking file by file of maps directory and make interpolation and map for each file
        for lag in env.config_run.settings['lags']:

            # all months in year 1->12
            for month in range(1, 13):

                if env.config_run.settings['analysis_interval'] == 'trimester':
                    if env.config_run.settings['class_category_analysis'] == 3:
                        var_I_idx = 1  # normal
                    if env.config_run.settings['class_category_analysis'] == 7:
                        var_I_idx = 3  # normal

                    # show only once
                    if lag == env.config_run.settings['lags'][0] and month == 1:
                        message_warning = True
                    else:
                        message_warning = False

                    # file where saved points for plot map
                    file_map_points = env.globals_vars.maps_files_climate[lag][month - 1][var_I_idx]

                    # save matrix for interpolation
                    base_path = os.path.join(env.globals_vars.CLIMATE_DIR, _('maps'),
                        _('lag_{0}').format(lag),
                        _('Correlation'),
                        grid.grid_name)

                    # make dir with the name of grid
                    output.make_dirs(base_path)

                    base_file = _(u'Map_correlation_lag_{0}_{1}').format(lag, format_out.trimester_in_initials(month - 1))

                    grid.date = format_out.trimester_in_initials(month - 1)
                    grid.lag = lag

                    # file for interpolation
                    inc_file = os.path.join(base_path, base_file + ".INC")

                    # save file for NCL
                    tsv_interpolation_file = os.path.join(base_path, base_file + ".tsv")
                    tsv_stations_file = os.path.join(base_path, base_file + "_stations.tsv")

                    process_map()

                else:
                    # range based on analysis interval
                    range_analysis_interval = get_range_analysis_interval()

                    for day in range(len(range_analysis_interval)):
                        if env.config_run.settings['class_category_analysis'] == 3:
                            var_I_idx = 1  # normal
                        if env.config_run.settings['class_category_analysis'] == 7:
                            var_I_idx = 3  # normal

                        # show only once
                        if lag == env.config_run.settings['lags'][0] and month == 1 and day == 0:
                            message_warning = True
                        else:
                            message_warning = False

                        # file where saved points for plot map
                        file_map_points = env.globals_vars.maps_files_climate[lag][month - 1][day][var_I_idx]

                        # save matrix for interpolation
                        base_path = os.path.join(env.globals_vars.CLIMATE_DIR, _('maps'),
                            env.globals_vars.analysis_interval_i18n,
                            _('lag_{0}').format(lag),
                            _('Correlation'),
                            grid.grid_name)

                        # make dir with the name of grid
                        output.make_dirs(base_path)

                        base_file = _(u'Map_correlation_lag_{0}_{1}')\
                        .format(lag, format_out.month_in_initials(month - 1) + "_" + str(range_analysis_interval[day]))

                        grid.date = format_out.month_in_initials(month - 1) + "_" + str(range_analysis_interval[day])
                        grid.lag = lag

                        # file for interpolation
                        inc_file = os.path.join(base_path, base_file + ".INC")

                        # save file for NCL
                        tsv_interpolation_file = os.path.join(base_path, base_file + ".tsv")
                        tsv_stations_file = os.path.join(base_path, base_file + "_stations.tsv")

                        process_map()

        console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # Process maps for FORECAST

    if env.config_run.settings['forecast_process'] and  env.config_run.settings['maps']['forecast']:

        grid.if_running["climate"] = False
        grid.if_running["correlation"] = False
        grid.if_running["forecast"] = True

        print _("Processing maps for forecast:")

        # console message
        if env.config_run.settings['analysis_interval'] == 'trimester':
            console.msg("                {0} ..................... ".format(env.config_run.settings['analysis_interval']), newline=False)
        else:
            console.msg("                {0}\t....................... ".format(env.config_run.settings['analysis_interval']), newline=False)

        # walking file by file of maps directory and make interpolation and map for each file
        for forecast_date in env.globals_vars.maps_files_forecast:

            for lag in env.config_run.settings['lags']:
                # show only once
                if lag == env.config_run.settings['lags'][0]:
                    message_warning = True
                else:
                    message_warning = False

                # file where saved points for plot map
                file_map_points = env.globals_vars.maps_files_forecast[forecast_date][lag]
                # save matrix for interpolation
                base_path = os.path.join(os.path.dirname(file_map_points), grid.grid_name)

                # make dir with the name of grid
                output.make_dirs(base_path)

                base_file = _(u'Map_lag_{0}_{1}').format(lag, forecast_date)

                grid.date = forecast_date
                grid.lag = lag

                # file for interpolation
                inc_file = os.path.join(base_path, base_file + ".INC")

                # save file for NCL
                tsv_interpolation_file = os.path.join(base_path, base_file + ".tsv")
                tsv_stations_file = os.path.join(base_path, base_file + "_stations.tsv")

                process_map()

        console.msg(_("done"), color='green')

    del base_matrix
