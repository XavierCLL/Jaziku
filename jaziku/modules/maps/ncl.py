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

from jaziku import env

class MapProperties(object):
    pass


def range_color_bar(inf, sup, step):
    array = []
    n = abs(inf - sup) / step
    for i in range(0, int(n) + 1):
        array.append(str(round(inf + i * step, 3)))
    return ','.join(array)


def make_ncl_probabilistic_map(grid, base_path_file, globals_vars):
    try:
        map_properties = MapProperties()
        # define the shape file
        map_properties.shape = os.path.join(grid.shape_path, grid.grid_name + ".shp")
        map_properties.base_path_file = base_path_file
        map_properties.name = grid.grid_name
        map_properties.lat_size = grid.lat_size
        map_properties.lon_size = grid.lon_size
        map_properties.shape_mask = grid.shape_mask
        map_properties.subtitle = grid.subtitle

        # set other properties of ncl script for this map
        map_properties.particular_properties_probabilistic_map = grid.particular_properties_probabilistic_map

        if "_" in grid.date:
            map_properties.date = grid.date.replace("_", " ")
        else:
            map_properties.date = grid.date

        if grid.if_running["climate"]:
            map_properties.title = _('''"Scenario of affectation of the variable {typeVarD}~C~    under variations of {typeVarI} to lag {lag} in {date}"''')\
                     .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)
            map_properties.color_bar_levels = "(/{array}/)".format(array=range_color_bar(-100, 100, 2.5))
            map_properties.color_bar_step = 2.5
            map_properties.color_bar_title_on = "True"
            map_properties.colormap = "Blue-Green-Red"
            map_properties.units = '''"%"'''
        if grid.if_running["correlation"]:
            map_properties.title = _('''"Lineal correlation between the variable {typeVarI}~C~              and {typeVarD} to lag {lag} in {date}"''')\
                     .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)
            map_properties.color_bar_levels = "(/{array}/)".format(array=range_color_bar(-1, 1, 0.025))
            map_properties.color_bar_step = 0.025
            map_properties.color_bar_title_on = "False"
            map_properties.colormap = "Green-White-Purple"
            map_properties.units = '''"Pearson"'''
        if grid.if_running["forecast"]:
            if env.config_run.settings['analysis_interval'] == 'trimester':
                map_properties.title = _('''"   Affectation forecast of the variable {typeVarD}~C~under variations of {typeVarI} to lag {lag} in {date}"''')\
                         .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)
            else:
                map_properties.title = _('''"Affectation forecast of the variable {typeVarD}~C~  under variations of {typeVarI} to lag {lag} in {date}"''')\
                         .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)
            map_properties.color_bar_levels = "(/{array}/)".format(array=range_color_bar(-100, 100, 2.5))
            map_properties.color_bar_step = 2.5
            map_properties.color_bar_title_on = "True"
            map_properties.colormap = "Blue-Green-Red"
            map_properties.units = '''"%"'''

        ### get ncl file in raw
        if grid.need_particular_ncl_script_probabilistic_map and os.path.isfile(os.path.join(grid.shape_path, "ncl_script_probabilistic_map.py")):
            # load the particular ncl if exist
            ncl_script = imp.load_source("ncl_script", os.path.join(grid.shape_path, "ncl_script_probabilistic_map.py"))
        elif grid.is_internal and os.path.isfile(os.path.join(os.path.dirname(grid.shape_path), "ncl_script_probabilistic_map.py")):
            # ncl_script file in parent directory (generic ncl script by region/country)  in internal grid
            ncl_script = imp.load_source("ncl_script", os.path.join(os.path.dirname(grid.shape_path), "ncl_script_probabilistic_map.py"))
        else:
            # load the generic ncl script
            ncl_script = imp.load_source("ncl_script", os.path.join(globals_vars.JAZIKU_DIR, 'data', 'maps', 'shapes', "ncl_script_probabilistic_map.py"))

        ncl_file_raw = ncl_script.code(map_properties)
        # define ncl file
        ncl_file = os.path.join(os.path.abspath(base_path_file) + ".ncl")

        #print ncl_file_raw
        open_ncl_file = open(ncl_file, 'wb')
        open_ncl_file.write(ncl_file_raw)
        open_ncl_file.close()

        return ncl_file
    except Exception as error:
        print error

def make_ncl_deterministic_map(grid, base_path_file, globals_vars):
    try:
        map_properties = MapProperties()
        # define the shape file
        map_properties.shape = os.path.join(grid.shape_path, grid.grid_name + ".shp")
        map_properties.base_path_file = base_path_file
        map_properties.name = grid.grid_name
        map_properties.subtitle = ''
        map_properties.colormap = "Colors-7-Categories"
        map_properties.minlat = grid.minlat
        map_properties.maxlat = grid.maxlat
        map_properties.minlon = grid.minlon
        map_properties.maxlon = grid.maxlon

        # thresholds
        thresholds_var_D = env.config_run.settings['thresholds_var_D']
        if thresholds_var_D == "default":
            thresholds_var_D = env.var_D.get_default_thresholds()
        map_properties.thresholds = ','.join('\"{0}\"'.format(x) for x in thresholds_var_D)

        # set other properties of ncl script for this map
        map_properties.particular_properties_deterministic_map = grid.particular_properties_deterministic_map

        if "_" in grid.date:
            map_properties.date = grid.date.replace("_", " ")
        else:
            map_properties.date = grid.date

        if grid.if_running["climate"]:
            map_properties.title = _('''"Scenario of affectation of the variable {typeVarD}~C~    under variations of {typeVarI} to lag {lag} in {date}"''')\
                     .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)

        if grid.if_running["correlation"]:
            map_properties.title = _('''"Lineal correlation between the variable {typeVarI}~C~              and {typeVarD} to lag {lag} in {date}"''')\
                     .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)

        if grid.if_running["forecast"]:
            if env.config_run.settings['analysis_interval'] == 'trimester':
                map_properties.title = _('''"   Affectation forecast of the variable {typeVarD}~C~under variations of {typeVarI} to lag {lag} in {date}"''')\
                         .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)
            else:
                map_properties.title = _('''"Affectation forecast of the variable {typeVarD}~C~  under variations of {typeVarI} to lag {lag} in {date}"''')\
                         .format(typeVarD=env.var_D.TYPE_SERIES, typeVarI=env.var_I.TYPE_SERIES, lag=grid.lag, date=map_properties.date)

        ### get ncl file in raw
        if grid.need_particular_ncl_script_deterministic_map and os.path.isfile(os.path.join(grid.shape_path, "ncl_script_deterministic_map.py")):
            # load the particular ncl if exist
            ncl_script = imp.load_source("ncl_script", os.path.join(grid.shape_path, "ncl_script_deterministic_map.py"))
        elif grid.is_internal and os.path.isfile(os.path.join(os.path.dirname(grid.shape_path), "ncl_script_deterministic_map.py")):
            # ncl_script file in parent directory (generic ncl script by region/country)  in internal grid
            ncl_script = imp.load_source("ncl_script", os.path.join(os.path.dirname(grid.shape_path), "ncl_script_deterministic_map.py"))
        else:
            # load the generic ncl script
            ncl_script = imp.load_source("ncl_script", os.path.join(globals_vars.JAZIKU_DIR, 'data', 'maps', 'shapes', "ncl_script_deterministic_map.py"))

        ncl_file_raw = ncl_script.code(map_properties)

        # define ncl file
        ncl_file = os.path.join(os.path.abspath(base_path_file) + ".ncl")

        #print ncl_file_raw
        open_ncl_file = open(ncl_file, 'wb')
        open_ncl_file.write(ncl_file_raw)
        open_ncl_file.close()

        return ncl_file
    except Exception as error:
        print error
