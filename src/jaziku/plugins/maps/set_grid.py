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
import imp
from clint.textui import colored


def search_and_set_internal_grid(grid):
    grid.shape_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'shapes', grid.grid_path)
    dir_to_list = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'shapes', grid.country)

    try:
        listdir = [name for name in os.listdir(dir_to_list) if os.path.isdir(os.path.join(dir_to_list, name))]

        if grid.grid_name in listdir:
            internal_grid = imp.load_source("internal_grid", os.path.join(grid.shape_path, grid.grid_name + ".py"))

            # set extreme lat and lon values from internal grid
            # but if is defined by user will not reset
            if not grid.minlat:
                grid.minlat = internal_grid.minlat
            if not grid.maxlat:
                grid.maxlat = internal_grid.maxlat
            if not grid.minlon:
                grid.minlon = internal_grid.minlon
            if not grid.maxlon:
                grid.maxlon = internal_grid.maxlon

            grid.need_particular_ncl_script = internal_grid.need_particular_ncl_script

            try:
                grid.particular_properties_map = internal_grid.particular_properties_map
            except:
                grid.particular_properties_map = {}

            return grid
        else:
            raise
    except:
        print colored.red(_("\nCan't set internal shape \"{0}\",\n"
                            "please check the grid parameter; area,\n"
                            "region and/or country name are wrong.\n").format(grid.grid_fullname))
        exit()


def set_particular_grid(grid):

    grid.shape_path = os.path.realpath(grid.shape_path)

    if not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".shp")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".prj")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".sbn")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".sbx")) or \
       not os.path.isfile(os.path.join(grid.shape_path, grid.grid_name + ".shx")):
        print colored.red(_("Can't set particular shape, please check files in shape path\n"
                            "this should be contain inside .shp .prj .sbn .sbx .shx"))
        exit()

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

        grid.need_particular_ncl_script = particular_grid.need_particular_ncl_script

        try:
            grid.particular_properties_map = particular_grid.particular_properties_map
        except:
            grid.particular_properties_map = {}
    else:
            grid.particular_properties_map = {}
            grid.need_particular_ncl_script = False

    return grid
