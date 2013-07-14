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
import imp
import math
from  numpy import linspace

from jaziku import env
from jaziku.utils import  console, array, input
from jaziku.core.station import Station

class Grid(object):
    """Grid class for maps
    """

    fields = ["grid",
              "latitude",
              "longitude",
              "shape_path",
              "grid_resolution",
              "semivariogram_type",
              "radiuses",
              "max_neighbours"]

    # all instances of grid class
    all_grids = []

    # all maps created in this grid
    maps_created_in_grid = 0

    # iterator of number of grids
    iter_grid = 0

    def __init__(self):
        # append instance to static variable all_grids
        Grid.all_grids.append(self)
        # number of grid created
        self.num = Grid.iter_grid
        Grid.iter_grid += 1
        # initialized lat and lon
        self.minlat = None
        self.maxlat = None
        self.minlon = None
        self.maxlon = None

    def  grid_properties(self):
        """Set values and default values for grid variables
        """

        # set the radiuses for interpolation
        if self.grid_resolution == "auto":
            # set grid resolution based in 70 division of grid for minimum side
            self.grid_resolution = min([abs(self.maxlat - self.minlat),
                                        abs(self.maxlon - self.minlon)]) / 80
        else:
            if not isinstance(self.grid_resolution, (int, float)):
                console.msg_error_configuration("grid_resolution",
                    _("The grid_resolution '{0}' is wrong, the options are:\n"
                    "'default' or valid number.").format(self.grid_resolution), stop_in_grid=self.num)
            self.grid_resolution = input.to_float(self.grid_resolution)

        env.globals_vars.input_settings["grid_resolution"].append(self.grid_resolution)

        # number of decimal from grid resolution
        self.decimal_resolution = len(str(self.grid_resolution).split('.')[1])

        # adjust extreme latitude and longitude values in rounded decimal point
        # to decimal resolution (defined in runfile)
        self.minlat = round(self.minlat, self.decimal_resolution)
        self.maxlat = round(self.maxlat, self.decimal_resolution)
        self.minlon = round(self.minlon, self.decimal_resolution)
        self.maxlon = round(self.maxlon, self.decimal_resolution)

        # calculate the number of values of grid (height and width based on grid resolution)
        # this is equal to height(lat) and width(lon) of matrix
        self.lat_size = int(abs(self.maxlat - self.minlat) / self.grid_resolution + 1)
        self.lon_size = int(abs(self.maxlon - self.minlon) / self.grid_resolution + 1)

        # make list of coordinate of latitude, this is a list of latitude for this grid
        lat_coordinates_list = linspace(max(self.maxlat, self.minlat),
            min(self.maxlat, self.minlat),
            self.lat_size).tolist()
        self.lat_coordinates = [round(item, self.decimal_resolution) for item in lat_coordinates_list]

        # make list of coordinate of longitude, this is a list of longitude for this grid
        lon_coordinates_list = linspace(min(self.maxlon, self.minlon),
            max(self.maxlon, self.minlon),
            self.lon_size).tolist()
        self.lon_coordinates = [round(item, self.decimal_resolution) for item in lon_coordinates_list]

        # interpolation type TODO:
        self.interpolation_type = _("ordinary kriging")

        # set the semivariogram type for interpolation
        #     0 – spherical, 1 – exponential, 2 – gaussian;
        self.all_semivariogram_type = {'spherical':0, 'exponential':1, 'gaussian':2}
        if self.semivariogram_type == "default":
            self.semivariogram_type = 'spherical'
        if self.semivariogram_type not in self.all_semivariogram_type:
            console.msg_error_configuration("semivariogram_type",
                _("The semivariogram type '{0}' is wrong, the options are:\n"
                  "default, {1}").format(self.semivariogram_type, ', '.join(self.all_semivariogram_type.keys())),
                stop_in_grid=self.num)

        env.globals_vars.input_settings["semivariogram_type"].append(self.semivariogram_type)
        self.num_semivariogram_type = self.all_semivariogram_type[self.semivariogram_type]


        # set the radiuses for interpolation
        if self.radiuses == "auto":
            radius = max([self.lat_size, self.lon_size]) * 3
            self.radiuses = [radius, radius]
        else:
            try:
                self.radiuses = [int(self.radiuses[0]), int(self.radiuses[1])]
            except:
                console.msg_error_configuration("radiuses",
                    _("The radiuses '{0}' is wrong, the options are:\n"
                      "'auto' or radius1 and radius2 in different column.").format(self.radiuses), stop_in_grid=self.num)

        env.globals_vars.input_settings["radiuses"].append(', '.join([str(x) for x in self.radiuses]))

        # set the max_neighbours
        if self.max_neighbours == "auto":
            self.max_neighbours = Station.stations_processed
        elif isinstance(self.max_neighbours, (int, float)):
            self.max_neighbours = int(self.max_neighbours)
        else:
            console.msg_error_configuration("max_neighbours",
                _("The max_neighbours '{0}' is wrong, the options are:\n"
                  "'auto' or valid number").format(self.max_neighbours), stop_in_grid=self.num)

        env.globals_vars.input_settings["max_neighbours"].append(self.max_neighbours)

        ## what do with data outside of boundary shape
        self.shape_mask = False
        # delete data outside of shape in mesh data
        # if grid_resolution is thin, the shape mask is better
        if env.config_run.settings['shape_boundary']:
            self.shape_mask = True

        ## set subtitle on maps
        if env.config_run.settings['analog_year']:
            self.subtitle = _("\"Analysis with {0} as analog year\"").format(env.config_run.settings['analog_year'])
        else:
            self.subtitle = "\"\""

    def  print_grid_properties(self):
        console.msg(_("   Mesh size: {0}x{1}").format(self.lat_size, self.lon_size), color='cyan')

        # interpolation type TODO:
        console.msg(_("   Interpolation type: {0}").format(self.interpolation_type), color='cyan')

        # the semivariogram type for interpolation
        #     0 – spherical, 1 – exponential, 2 – gaussian;
        if self.semivariogram_type == "spherical":
            console.msg(_("   Semivariogram type: spherical"), color='cyan')
        if self.semivariogram_type == "exponential":
            console.msg(_("   Semivariogram type: exponential"), color='cyan')
        if self.semivariogram_type == "gaussian":
            console.msg(_("   Semivariogram type: gaussian"), color='cyan')

        # print radiuses
        console.msg(_("   Radiuses: {0} {1}").format(self.radiuses[0], self.radiuses[1]), color='cyan')

        # max_neighbours:
        console.msg(_("   Max neighbours: {0}").format(self.max_neighbours), color='cyan')

    def set_point_on_grid(self, matrix, lat, lon, value):

        # round decimal point to decimal resolution
        lat = round(lat, self.decimal_resolution)
        lon = round(lon, self.decimal_resolution)

        # check if value is "nan", this is when the station has few values
        # and the thresholds are inadequate
        if math.isnan(value):
            return matrix, "nan"

        # check if point is outside of the grid
        if lat < min(self.lat_coordinates) or\
           lat > max(self.lat_coordinates) or\
           lon < min(self.lon_coordinates) or\
           lon > max(self.lon_coordinates):
            return matrix, "point not added"

        def closest(target, collection):
            return min((abs(target - i), i) for i in collection)[1]

        # search the closest value in coordinates list
        lat_closest = closest(lat, self.lat_coordinates)
        lon_closest = closest(lon, self.lon_coordinates)

        # set the location in coordinates list
        lat_location = self.lat_coordinates.index(lat_closest)
        lon_location = self.lon_coordinates.index(lon_closest)

        ## put value in the base matrix
        # first check if already exist value in this point on matrix (overlapping)
        if int(matrix[lat_location, lon_location]) != env.globals_vars.OLD_VALID_NULL[1]:
            if env.config_run.settings['overlapping'] == "average":
                matrix[lat_location, lon_location] = array.mean([matrix[lat_location, lon_location], value])
                return matrix, _("average")
            if env.config_run.settings['overlapping'] == "maximum":
                matrix[lat_location, lon_location] = max([matrix[lat_location, lon_location], value])
                return matrix, _("maximum")
            if env.config_run.settings['overlapping'] == "minimum":
                matrix[lat_location, lon_location] = min([matrix[lat_location, lon_location], value])
                return matrix, _("minimum")
            if env.config_run.settings['overlapping'] == "neither":
                return matrix, _("neither")
        else:
            matrix[lat_location, lon_location] = value

        return matrix, True


def search_and_set_internal_grid(grid):

    grid.is_internal = True

    grid.shape_path = os.path.join(env.globals_vars.JAZIKU_DIR, 'data', 'maps', 'shapes', grid.grid_path)
    dir_to_list = os.path.join(env.globals_vars.JAZIKU_DIR, 'data', 'maps', 'shapes', grid.country)

    try:
        listdir = [name for name in os.listdir(dir_to_list) if os.path.isdir(os.path.join(dir_to_list, name))]

        if grid.grid_name in listdir:
            internal_grid = imp.load_source("internal_grid", os.path.join(grid.shape_path, grid.grid_name + ".py"))

            # set extreme lat and lon values when the 'latitude' or 'longitude'
            # defined in runfile is equal to 'internal' with values inside
            # python shape file
            if grid.latitude == "internal":
                grid.minlat = internal_grid.minlat
                grid.maxlat = internal_grid.maxlat
            if grid.longitude == "internal":
                grid.minlon = internal_grid.minlon
                grid.maxlon = internal_grid.maxlon

            grid.need_particular_ncl_script_probabilistic_map = internal_grid.need_particular_ncl_script_probabilistic_map
            grid.need_particular_ncl_script_deterministic_map = internal_grid.need_particular_ncl_script_deterministic_map

            try:
                grid.particular_properties_probabilistic_map = internal_grid.particular_properties_probabilistic_map
            except:
                grid.particular_properties_probabilistic_map = {}

            try:
                grid.particular_properties_deterministic_map = internal_grid.particular_properties_deterministic_map
            except:
                grid.particular_properties_deterministic_map = {}
        else:
            raise
    except:
        raise ValueError(_("The 'shape_path' was defined as 'internal' but\n"
                           "jaziku can't set internal shape for '{0}',\n"
                           "please check the 'grid' parameter in runfile;\n"
                           "this must be a valid area/region and country name\n"
                           "in different column or only country name. If you\n"
                           "want know the list of available internal shapes,\n"
                           "please check the manual.\n\n"
                           "For example: Colombia, Vaupes;Colombia, Caldas;Colombia.\n").format(grid.grid_fullname))

def set_particular_grid(grid):

    grid.is_internal = False

    grid.shape_path = os.path.realpath(grid.shape_path)

    if not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".shp")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".prj")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".sbn")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".sbx")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".shx")):
        raise ValueError(_("Can't set particular shape, please check files in shape path\n"
                            "this must be contain inside .shp .prj .sbn .sbx .shx\n"
                            "and each file must be named with the same name defined\n"
                            "for the 'grid' parameter.\n\n"
                            "For example, if you define in 'grid' as 'region_A' \n"
                            "the files inside shape_path directory must be named:\n"
                            "region_A.shp, region_A.prj, region_A.sbn,\n"
                            "region_A.sbx and region_A.shx."))

    if os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".py")):
        particular_grid = imp.load_source("particular_grid", os.path.join(grid.shape_path, grid.grid_name + ".py"))
        # set extreme lat and lon values from internal grid inside shape file
        # but if is defined by user will not reset
        if not grid.minlat:
            grid.minlat = particular_grid.minlat
        if not grid.maxlat:
            grid.maxlat = particular_grid.maxlat
        if not grid.minlon:
            grid.minlon = particular_grid.minlon
        if not grid.maxlon:
            grid.maxlon = particular_grid.maxlon

        grid.need_particular_ncl_script_probabilistic_map = particular_grid.need_particular_ncl_script_probabilistic_map
        grid.need_particular_ncl_script_deterministic_map = particular_grid.need_particular_ncl_script_deterministic_map

        try:
            grid.particular_properties_probabilistic_map = particular_grid.particular_properties_probabilistic_map
        except:
            grid.particular_properties_probabilistic_map = {}

        try:
            grid.particular_properties_deterministic_map = particular_grid.particular_properties_deterministic_map
        except:
            grid.particular_properties_deterministic_map = {}
    else:
        grid.particular_properties_probabilistic_map = {}
        grid.particular_properties_deterministic_map = {}
        grid.need_particular_ncl_script_probabilistic_map = False
        grid.need_particular_ncl_script_deterministic_map = False