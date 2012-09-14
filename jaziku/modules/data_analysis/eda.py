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
import csv
from datetime import date
from matplotlib import pyplot
from pylab import xticks, setp, bar, arange
from Image import open as img_open

from jaziku.modules.station import Station
from jaziku.utils import globals_vars, console, format_out


def main(stations):

    console.msg(_("Exploratory data analysis (EDA) .............. "), newline=False)

    # -------------------------------------------------------------------------
    # DESCRIPTIVE STATISTICS

    files_dir = os.path.join(globals_vars.data_analysis_dir, 'EDA', _('Descriptive_Statistic'))

    if not os.path.isdir(files_dir):
        os.makedirs(files_dir)

    file_descriptive_statistics_var_D \
        = os.path.join(files_dir, _('Descriptive_Statistics_{0}.csv').format(globals_vars.config_run['type_var_D']))

    file_descriptive_statistics_var_I\
        = os.path.join(files_dir, _('Descriptive_Statistics_{0}.csv').format(globals_vars.config_run['type_var_I']))

    open_file_D = open(file_descriptive_statistics_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=';')

    open_file_I = open(file_descriptive_statistics_var_I, 'w')
    csv_file_I = csv.writer(open_file_I, delimiter=';')

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), _('SIZE DATA'), _('MAXIMUM'),
              _('MINIMUM'), _('AVERAGE'), _('MEDIAN'), _('STD DEVIATION'), _('SLANT'), _('CURTOSIS'), _('C-VARIATION')]

    csv_file_D.writerow(header)
    csv_file_I.writerow(header)

    for station in stations:

        # var D
        eda_var_D = [
            station.code,
            station.name,
            format_out.number(station.lat, 4),
            format_out.number(station.lon, 4),
            format_out.number(station.alt, 4),
            '{0}-{1}'.format(station.process_period['start'], station.process_period['end']),
            station.var_D.size_data,
            format_out.number(station.var_D.maximum, 4),
            format_out.number(station.var_D.minimum, 4),
            format_out.number(station.var_D.average, 4),
            format_out.number(station.var_D.median, 4),
            format_out.number(station.var_D.std_dev, 4),
            format_out.number(station.var_D.skew, 4),
            format_out.number(station.var_D.kurtosis, 4),
            format_out.number(station.var_D.coef_variation, 4)
        ]

        csv_file_D.writerow(eda_var_D)

        # var I
        eda_var_I = [
            station.code,
            station.name,
            format_out.number(station.lat, 4),
            format_out.number(station.lon, 4),
            format_out.number(station.alt, 4),
            '{0}-{1}'.format(station.process_period['start'], station.process_period['end']),
            station.var_I.size_data,
            format_out.number(station.var_I.maximum, 4),
            format_out.number(station.var_I.minimum, 4),
            format_out.number(station.var_I.average, 4),
            format_out.number(station.var_I.median, 4),
            format_out.number(station.var_I.std_dev, 4),
            format_out.number(station.var_I.skew, 4),
            format_out.number(station.var_I.kurtosis, 4),
            format_out.number(station.var_I.coef_variation, 4)
        ]

        csv_file_I.writerow(eda_var_I)

    open_file_D.close()
    del csv_file_D

    open_file_I.close()
    del csv_file_I

    # only make graphs if there are more of one station
    if Station.stations_processed > 1:
        descriptive_statistic_graphs(stations)
        console.msg(_("done"), color='green')
    else:
        console.msg("Error\n > WARNING: There is only one station for process\n"
                    "   the graphs for descriptive statistic need more \n"
                    "   of one station.", color="yellow")

def zoom_graph(ax,x_scale_below=0, x_scale_above=0, y_scale_below=0, y_scale_above=0, abs_x=False, abs_y=False):
    """
    zoom in/out graph where ax is figure subplot and scale is the value for
    zoom in(+) out(-), if scale = 0 no zoom, scale = 1 double zoom in factor,
    scale = 2 triple zoom in factor, scale = -1 double zoom out factor
    """
    # get the current x and y limits
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
    cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5

    # set new limits
    if abs_x:
        ax.set_xlim([cur_xlim[0] + x_scale_below,
                     cur_xlim[1] - x_scale_above])
    else:
        ax.set_xlim([cur_xlim[0] + cur_xrange*x_scale_below,
                     cur_xlim[1] - cur_xrange*x_scale_above])
    if abs_y:
        ax.set_ylim([cur_ylim[0] + y_scale_below,
                     cur_ylim[1] - y_scale_above])
    else:
        ax.set_ylim([cur_ylim[0] + cur_yrange*y_scale_below,
                     cur_ylim[1] - cur_yrange*y_scale_above])



def descriptive_statistic_graphs(stations):


    statistics = ['size_data', 'maximum', 'minimum', 'average', 'median', 'std_dev','skew', 'kurtosis', 'coef_variation']
    statistics_to_graphs = [_('Sizes_data'), _('Maximums'), _('Minimums'), _('Averages'), _('Medians'),
                            _('Std_deviations'), _('Skews'), _('Kurtosis'), _('Coef_variations')]
    graph_options = {'size_data':'bars', 'maximum':'bars', 'minimum':'bars', 'average':'bars', 'median':'bars',
                     'std_dev':'dots','skew':'dots', 'kurtosis':'dots', 'coef_variation':'dots'}

    # directory for save graphs of descriptive statistic
    graphs_dir = os.path.join(globals_vars.data_analysis_dir, 'EDA',
        _('Descriptive_Statistic'), _('Graphs_for_{0}').format(globals_vars.config_run['type_var_D']))

    if not os.path.isdir(graphs_dir):
        os.makedirs(graphs_dir)

    #for type, var in [[globals_vars.config_run['type_var_D'],'var_D'], [globals_vars.config_run['type_var_I'],'var_I']]:
    for graph in ['vs_Stations', 'vs_Altitude']:

        for enum, statistic in enumerate(statistics_to_graphs):
            x = []
            y = []
            for station in stations:
                get_statistic = {'size_data':station.var_D.size_data, 'maximum':station.var_D.maximum,
                                 'minimum':station.var_D.minimum, 'average':station.var_D.average,
                                 'median':station.var_D.median, 'std_dev':station.var_D.std_dev,
                                 'skew':station.var_D.skew, 'kurtosis':station.var_D.kurtosis,
                                 'coef_variation':station.var_D.coef_variation}
                if graph == 'vs_Stations':
                    x.append(station.code)
                if graph == 'vs_Altitude':
                    x.append(float(station.alt))
                y.append(get_statistic[statistics[enum]])

            # do that matplotlib plot zeros in extreme values
            for value in y:
                if value == 0:
                    y[y.index(value)] = 0.0001

            name_graph = _("{0}_({1})_{2}").format(statistic, globals_vars.config_run['type_var_D'], graph)
            # dynamic with based of number of stations
            with_fig = Station.stations_processed/5+4
            fig = pyplot.figure(figsize=(with_fig, 6), dpi=80)
            ax = fig.add_subplot(111)
            ax.set_title(name_graph.replace('_',' '))

            if graph == 'vs_Stations':
                if graph_options[statistics[enum]] == 'dots':
                    ax.plot(range(1, len(x)+1), y, 'o', color="#638786")
                if graph_options[statistics[enum]] == 'bars':
                    bar(range(1, len(x)+1), y, width=0.8, align='center', color="#638786")
            if graph == 'vs_Altitude':
                ax.plot(x, y, 'o', color="#638786")

            ## X
            if graph == 'vs_Stations':
                ax.set_xlabel(_('Stations'))
                locs, labels = xticks(range(1, len(x)+1), x)
                setp(labels, 'rotation', 'vertical')
            if graph == 'vs_Altitude':
                ax.set_xlabel(_('Altitude'))
                #locs, labels = xticks(range(1, len(x)+1), x)
                #setp(labels, 'rotation', 'vertical')
            ## Y
            # get units os type of var D or I
            if globals_vars.config_run['type_var_D'] in globals_vars.units_of_types_var_D:
                units = globals_vars.units_of_types_var_D[globals_vars.config_run['type_var_D']]
            else:
                units = '--'
            ax.set_ylabel('{0} ({1})'.format(statistic.replace('_',' '),units))

            pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)
            if graph == 'vs_Stations':
                if graph_options[statistics[enum]] == 'dots':
                    zoom_graph(ax=ax, x_scale_below=-0.3,x_scale_above=-0.3, y_scale_below=-0.1, y_scale_above=-0.1, abs_x=True)
                if graph_options[statistics[enum]] == 'bars':
                    zoom_graph(ax=ax, x_scale_below=-0.3,x_scale_above=-0.3, y_scale_above=-0.1, abs_x=True)
            if graph == 'vs_Altitude':
                zoom_graph(ax=ax, x_scale_below=-0.05,x_scale_above=-0.05, y_scale_below=-0.08, y_scale_above=-0.08)

            fig.tight_layout()

            pyplot.savefig(os.path.join(graphs_dir, name_graph + '.png'), dpi=75)
            del fig, ax
            pyplot.clf()




