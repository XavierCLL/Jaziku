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
import shutil
import tempfile
import numpy
from subprocess import call

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.modules.maps import interpolation
from jaziku.modules.maps.ncl import make_ncl_probabilistic_map, make_ncl_deterministic_map
from jaziku.modules.maps.grid import Grid
from jaziku.utils import console, watermarking, output, input
from jaziku.utils.text import slugify


def pre_process():
    """Check basic requirements for make maps
    """

    print _("\n\n"
        "############################# MAPS  ############################\n"
        "# Map Process, here is made the Kriging interpolation on the   #\n"
        "# results of historical scenarios and forecasts most probable  #\n"
        "# of the dependent variable, also interpolation of linear      #\n"
        "# correlations.                                                #\n"
        "################################################################")


    console.msg(_("\nChecking basic requirements for make maps:"), newline=False)

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
       not os.path.isfile(os.path.join(os.environ.get('NCARG_ROOT'),'lib/ncarg/nclscripts/csm/gsn_code.ncl')) or\
       not os.path.isfile(os.path.join(os.environ.get('NCARG_ROOT'),'lib/ncarg/nclscripts/csm/gsn_csm.ncl')) or\
       not os.path.isfile(os.path.join(os.environ.get('NCARG_ROOT'),'lib/ncarg/nclscripts/csm/contributed.ncl')):
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


def process(grid):
    """In Maps, jaziku in order to predict variable values in sites not sampled, through Kriging
    spatial interpolation method displays the general trends and spatial continuity of affectation
    scenarios results of Climate and Forecast Modules.

    Graphs two types of maps:
        Probabilistic map: First make grid of dimension of map, put all station inside grid,
        after interpolate the grid values and graphs it with NCL

        Deterministic maps: only for 7 categories and climate and forecast (no correlation) maps,
        this map graphs the position of index (inside of the 7 categories) by each station, and
        graphs this station as color point, not graphs interpolation values.
    """

    # restart counter
    Grid.maps_created_in_grid = 0

    print "\n################# {0}: {1}".format(_("MAP"), grid.grid_fullname)

    # show the mainly properties
    grid.print_grid_properties()

    ## Matrix with real data and null value for empty value
    # base_matrix[lat, lon]
    global base_matrix
    base_matrix = numpy.matrix(numpy.empty([grid.lat_size, grid.lon_size]))
    # initialize matrix with null value
    base_matrix.fill(env.globals_vars.OLD_VALID_NULL[1])

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
            latitude = input.to_float(line[1])
            longitude = input.to_float(line[2])

            # get index and index_position from Map_Data file
            if env.config_run.settings['class_category_analysis'] == 3:
                if grid.if_running["climate"] or grid.if_running["forecast"]:
                    index = input.to_float(line[8])  # get index value
                if grid.if_running["correlation"]:
                    index = input.to_float(line[3])  # get pearson value
                # get index position:
                index_position = line[9]
            if env.config_run.settings['class_category_analysis'] == 7:
                if grid.if_running["climate"] or grid.if_running["forecast"]:
                    index = input.to_float(line[12])  # get index value
                if grid.if_running["correlation"]:
                    index = input.to_float(line[3])  # get pearson value
                # get index position:
                index_position = line[13]

            if map_type == _("probabilistic"):
                # set the index value on matrix

                matrix, point_state = grid.set_point_on_grid(matrix, latitude, longitude, index)

                if point_state == "nan" and message_warning:
                    console.msg(
                        _("\n > WARNING: The point lat:{lat} lon:{lon}\n"
                          "   of the station code: {code} was not added\n"
                          "   because the value of index is 'nan' (null).").
                        format(lat=latitude, lon=longitude, code=line[0]), color='yellow', newline=False)
                if point_state == "point not added" and message_warning:
                    console.msg(
                        _("\n > WARNING: The point lat:{lat} lon:{lon}\n"
                          "   of the station code: {code} was not added\n"
                          "   because the point is outside of the grid.").
                        format(lat=latitude, lon=longitude, code=line[0]), color='yellow', newline=False)
                if point_state in [_("average"), _("maximum"), _("minimum")] and message_warning:
                    console.msg(
                        _("\n > WARNING: for the point lat:{lat} lon:{lon}\n"
                          "   Jaziku detect overlapping of two values, it\n"
                          "   will put the {state} value.").
                        format(lat=latitude, lon=longitude, state=point_state), color='yellow', newline=False)
                if point_state == _("neither") and message_warning:
                    console.msg(
                        _("\n > WARNING: for the point lat:{lat} lon:{lon}\n"
                          "   Jaziku detect overlapping of two values, Jaziku\n"
                          "   will not put the {state} values.").
                        format(lat=latitude, lon=longitude, state=point_state), color='yellow', newline=False)

            # if index_position is not 'nan', replace index_position to not translate category text
            if index_position != 'nan':
                idx_cat = env.globals_vars.categories(as_list=True).index(index_position)
                index_position = env.globals_vars.categories(translated=False, as_list=True)[idx_cat]

            marks_stations.append([latitude, longitude, index, index_position])

        open_file.close()
        del csv_file

        if map_type == _("probabilistic"):

            # save matrix for interpolation
            open_file = open(inc_file, 'wb')
            open_file.write("Cont_data" + '\n')

            # convert matrix (column per column) to linear values
            matrix_vector = numpy.asarray(matrix.T).reshape(-1)

            # save values to .INC file
            for value in matrix_vector:
                if int(value) == env.globals_vars.OLD_VALID_NULL[1]:
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
        tsv_file.writerow([_('lat'), _('lon'), _('index'), _('index position')])

        for mark_station in marks_stations:
            tsv_file.writerow(mark_station)

        stations_file.close()
        del tsv_file

        # make ncl file for map
        tmp_path_file = os.path.join(tmp_dir, base_file)
        base_path_file = os.path.join(base_path, base_file)
        # make and write ncl file for ncl process
        if map_type == _("probabilistic"):
            ncl_file = make_ncl_probabilistic_map(grid, tmp_path_file, env.globals_vars)
        if map_type == _("deterministic"):
            ncl_file = make_ncl_deterministic_map(grid, tmp_path_file, env.globals_vars)
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
        image_file = (tmp_path_file + ".png").replace(" ", r"\ ")

        call(["convert", image_file, "-trim", "-bordercolor", "white", "-border", "4", image_file], shell=False)

        # TODO: test if convert worked

        # stamp logo
        watermarking.logo(tmp_path_file + ".png")

        # copy map
        if os.path.isfile(base_path_file + ".png"):
            os.remove(base_path_file + ".png")
        shutil.move(tmp_path_file + ".png", base_path)

        # delete temporal directory
        shutil.rmtree(tmp_dir)

        del matrix

    grid.if_running = {"climate":False, "correlation":False, "forecast":False}

    # -------------------------------------------------------------------------
    # Process maps for CLIMATE

    if env.config_run.settings['maps']['climate']:

        grid.if_running["climate"] = True

        if env.config_run.settings['class_category_analysis'] == 3:
            types_of_maps = [_("probabilistic")]
        if env.config_run.settings['class_category_analysis'] == 7:
            types_of_maps = [_("probabilistic"), _("deterministic")]

        for map_type in types_of_maps:

            print _("Processing {map_type} maps for climate:").format(map_type=map_type)

            # console message
            console.msg("   {0} ... ".format(env.config_run.settings['analysis_interval']), newline=False)

            # walking file by file of maps directory and make interpolation and map for each file
            for lag in env.config_run.settings['lags']:

                # all months in year 1->12
                for month in range(1, 13):

                    if env.config_run.settings['analysis_interval'] in ['monthly', 'bimonthly', 'trimonthly']:
                        for var_I_idx, label in enumerate(env.config_run.get_CATEGORIES_LABELS_VAR_I()):
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
                            if env.config_run.settings['class_category_analysis'] == 7:
                                base_path = os.path.join(base_path, map_type)

                            # create the temporal directory
                            tmp_dir = tempfile.mkdtemp()

                            # make dir with the name of grid
                            output.make_dirs(base_path)

                            if map_type == _("probabilistic"):
                                base_file = _(u'Prob_Map_lag_{0}_{1}_{2}')\
                                    .format(lag, output.analysis_interval_text(month, join_result=True), label)
                            if map_type == _("deterministic"):
                                base_file = _(u'Deter_Map_lag_{0}_{1}_{2}')\
                                    .format(lag, output.analysis_interval_text(month, join_result=True), label)

                            grid.date = output.analysis_interval_text(month)
                            grid.lag = lag

                            if map_type == _("probabilistic"):
                                # file for interpolation
                                inc_file = os.path.join(tmp_dir, base_file + ".INC")

                                # save file for NCL
                                tsv_interpolation_file = os.path.join(tmp_dir, base_file + ".tsv")

                            # file where saved stations with lat, lon, index and index_position
                            tsv_stations_file = os.path.join(tmp_dir, base_file + "_stations.tsv")

                            process_map()

                    else:
                        # range based on analysis interval
                        range_analysis_interval = get_range_analysis_interval()

                        for day in range(len(range_analysis_interval)):
                            for var_I_idx, label in enumerate(env.config_run.get_CATEGORIES_LABELS_VAR_I()):
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
                                if env.config_run.settings['class_category_analysis'] == 7:
                                    base_path = os.path.join(base_path, map_type)

                                # create the temporal directory
                                tmp_dir = tempfile.mkdtemp()

                                # make dir with the name of grid
                                output.make_dirs(base_path)

                                if map_type == _("probabilistic"):
                                    base_file = _(u'Prob_Map_lag_{0}_{1}_{2}')\
                                        .format(lag,
                                                output.analysis_interval_text(month, range_analysis_interval[day], join_result=True),
                                                label)
                                if map_type == _("deterministic"):
                                    base_file = _(u'Deter_Map_lag_{0}_{1}_{2}')\
                                        .format(lag,
                                                output.analysis_interval_text(month, range_analysis_interval[day], join_result=True),
                                                label)

                                grid.date = output.analysis_interval_text(month, range_analysis_interval[day])
                                grid.lag = lag

                                if map_type == _("probabilistic"):
                                    # file for interpolation
                                    inc_file = os.path.join(tmp_dir, base_file + ".INC")

                                    # save file for NCL
                                    tsv_interpolation_file = os.path.join(tmp_dir, base_file + ".tsv")

                                # file where saved stations with lat, lon, index and index_position
                                tsv_stations_file = os.path.join(tmp_dir, base_file + "_stations.tsv")

                                process_map()

            console.msg(_("done"), color='green')
        grid.if_running["climate"] = False

    # -------------------------------------------------------------------------
    # Process maps for CORRELATION

    if env.config_run.settings['maps']['correlation']:

        grid.if_running["correlation"] = True
        map_type = _("probabilistic")

        print _("Processing maps for correlation:")

        # console message
        console.msg("   {0} ... ".format(env.config_run.settings['analysis_interval']), newline=False)

        # walking file by file of maps directory and make interpolation and map for each file
        for lag in env.config_run.settings['lags']:

            # all months in year 1->12
            for month in range(1, 13):

                if env.config_run.settings['analysis_interval'] in ['monthly', 'bimonthly', 'trimonthly']:
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

                    # create the temporal directory
                    tmp_dir = tempfile.mkdtemp()

                    # make dir with the name of grid
                    output.make_dirs(base_path)

                    base_file = _(u'Map_correlation_lag_{0}_{1}').format(lag, output.analysis_interval_text(month, join_result=True))

                    grid.date = output.analysis_interval_text(month)
                    grid.lag = lag

                    # file for interpolation
                    inc_file = os.path.join(tmp_dir, base_file + ".INC")

                    # save file for NCL
                    tsv_interpolation_file = os.path.join(tmp_dir, base_file + ".tsv")
                    tsv_stations_file = os.path.join(tmp_dir, base_file + "_stations.tsv")

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
                            _('lag_{0}').format(lag),
                            _('Correlation'),
                            grid.grid_name)

                        # create the temporal directory
                        tmp_dir = tempfile.mkdtemp()

                        # make dir with the name of grid
                        output.make_dirs(base_path)

                        base_file = _(u'Map_correlation_lag_{0}_{1}')\
                            .format(lag, output.analysis_interval_text(month, range_analysis_interval[day], join_result=True))

                        grid.date = output.analysis_interval_text(month, range_analysis_interval[day])
                        grid.lag = lag

                        # file for interpolation
                        inc_file = os.path.join(tmp_dir, base_file + ".INC")

                        # save file for NCL
                        tsv_interpolation_file = os.path.join(tmp_dir, base_file + ".tsv")
                        tsv_stations_file = os.path.join(tmp_dir, base_file + "_stations.tsv")

                        process_map()

        grid.if_running["correlation"] = False
        console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # Process maps for FORECAST

    if env.config_run.settings['forecast_process'] and  env.config_run.settings['maps']['forecast']:

        grid.if_running["forecast"] = True

        if env.config_run.settings['class_category_analysis'] == 3:
            types_of_maps = [_("probabilistic")]
        if env.config_run.settings['class_category_analysis'] == 7:
            types_of_maps = [_("probabilistic"), _("deterministic")]

        for map_type in types_of_maps:

            print _("Processing {map_type} maps for forecast:").format(map_type=map_type)

            # console message
            console.msg("   {0} ... ".format(env.config_run.settings['forecast_date']['text']), newline=False)

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
                    if env.config_run.settings['class_category_analysis'] == 7:
                        base_path = os.path.join(base_path, map_type)

                    # create the temporal directory
                    tmp_dir = tempfile.mkdtemp()

                    # make dir with the name of grid
                    output.make_dirs(base_path)

                    if map_type == _("probabilistic"):
                        base_file = _(u'Prob_Map_lag_{0}_{1}').format(lag, slugify(forecast_date))
                    if map_type == _("deterministic"):
                        base_file = _(u'Deter_Map_lag_{0}_{1}').format(lag, slugify(forecast_date))

                    grid.date = forecast_date
                    grid.lag = lag

                    if map_type == _("probabilistic"):
                        # file for interpolation
                        inc_file = os.path.join(tmp_dir, base_file + ".INC")

                        # save file for NCL
                        tsv_interpolation_file = os.path.join(tmp_dir, base_file + ".tsv")

                    # file where saved stations with lat, lon, index and index_position
                    tsv_stations_file = os.path.join(tmp_dir, base_file + "_stations.tsv")

                    process_map()

            console.msg(_("done"), color='green')
        grid.if_running["forecast"] = False

    del base_matrix
