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
import gc
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot
from pylab import xticks, setp, bar
import matplotlib.dates as mdates
from Image import open as img_open

from jaziku.modules.station import Station
from jaziku.modules.variable import Variable
from jaziku.utils import globals_vars, console, format_out
from jaziku.utils.mean import mean


def main(stations):

    # -------------------------------------------------------------------------
    # EXPLORATORY DATA ANALYSIS
    # -------------------------------------------------------------------------

    console.msg(_("################# EXPLORATORY DATA ANALYSIS:"))

    global eda_dir
    eda_dir = os.path.join(globals_vars.data_analysis_dir, 'EDA')

    # -------------------------------------------------------------------------
    # DESCRIPTIVE STATISTICS
    # -------------------------------------------------------------------------

    console.msg(_("Descriptive statistics ............................... "), newline=False)

    # -------------------------------------------------------------------------
    # FILES OF DESCRIPTIVE STATISTICS

    global descriptive_statistic_dir
    descriptive_statistic_dir = os.path.join(eda_dir, _('Descriptive_Statistic'))

    if not os.path.isdir(descriptive_statistic_dir):
        os.makedirs(descriptive_statistic_dir)

    file_descriptive_statistics_var_D \
        = os.path.join(descriptive_statistic_dir, _('Descriptive_Statistics_{0}.csv').format(globals_vars.config_run['type_var_D']))

    file_descriptive_statistics_var_I\
        = os.path.join(descriptive_statistic_dir, _('Descriptive_Statistics_{0}.csv').format(globals_vars.config_run['type_var_I']))

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

    # -------------------------------------------------------------------------
    # GRAPHS OF DESCRIPTIVE STATISTICS

    # only make graphs if there are more of one station
    if Station.stations_processed > 1:
        descriptive_statistic_graphs(stations)
        console.msg(_("done"), color='green')
    else:
        console.msg(_("fail\n > WARNING: There is only one station for process\n"
                    "   the graphs for descriptive statistic need more \n"
                    "   of one station."), color="yellow")

    # -------------------------------------------------------------------------
    # GRAPHS INSPECTION OF SERIES

    console.msg(_("Graphs inspection of series .......................... "), newline=False)
    graphs_inspection_of_series(stations)
    console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # CLIMATOLOGY

    console.msg(_("Climatology .......................................... "), newline=False)
    climatology(stations)
    console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # DISTRIBUTION TEST
    # -------------------------------------------------------------------------

    global distribution_test_dir
    distribution_test_dir = os.path.join(eda_dir, _('Distribution_Test'))

    if not os.path.isdir(distribution_test_dir):
        os.makedirs(distribution_test_dir)

    # -------------------------------------------------------------------------
    # SCATTER PLOTS OF SERIES

    console.msg(_("Scatter plots of series .............................. "), newline=False)

    if Station.stations_processed > 1:
        scatter_plots_of_series(stations)
        console.msg(_("done"), color='green')
    else:
        console.msg(_("fail\n > WARNING: There is only one station for process\n"
                      "   the scatter plots of series, this need more \n"
                      "   of one station."), color="yellow")

    # -------------------------------------------------------------------------
    # FREQUENCY HISTOGRAM

    console.msg(_("Frequency histogram .................................. "), newline=False)

    if Station.stations_processed > 1:
        frequency_histogram(stations)
        console.msg(_("done"), color='green')
    else:
        console.msg(_("fail\n > WARNING: There is only one station for process\n"
                      "   the scatter plots of series, this need more \n"
                      "   of one station."), color="yellow")


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
    """
    Graphs statistics vs stations and statistics vs altitude for var D
    """
    statistics = ['size_data', 'maximum', 'minimum', 'average', 'median', 'std_dev','skew', 'kurtosis', 'coef_variation']
    statistics_to_graphs = [_('Sizes_data'), _('Maximums'), _('Minimums'), _('Averages'), _('Medians'),
                            _('Std_deviations'), _('Skews'), _('Kurtosis'), _('Coef_variations')]
    graph_options = {'size_data':'bars', 'maximum':'bars', 'minimum':'bars', 'average':'bars', 'median':'bars',
                     'std_dev':'dots','skew':'dots', 'kurtosis':'dots', 'coef_variation':'dots'}

    # directory for save graphs of descriptive statistic
    graphs_dir = os.path.join(descriptive_statistic_dir, _('Graphs_for_{0}').format(globals_vars.config_run['type_var_D']))

    if not os.path.isdir(graphs_dir):
        os.makedirs(graphs_dir)

    #for type, var in [[globals_vars.config_run['type_var_D'],'var_D'], [globals_vars.config_run['type_var_I'],'var_I']]:
    for graph in [_('vs_Stations'), _('vs_Altitude')]:

        for enum, statistic in enumerate(statistics_to_graphs):
            x = []
            y = []
            for station in stations:
                get_statistic = {'size_data':station.var_D.size_data, 'maximum':station.var_D.maximum,
                                 'minimum':station.var_D.minimum, 'average':station.var_D.average,
                                 'median':station.var_D.median, 'std_dev':station.var_D.std_dev,
                                 'skew':station.var_D.skew, 'kurtosis':station.var_D.kurtosis,
                                 'coef_variation':station.var_D.coef_variation}
                if graph == _('vs_Stations'):
                    x.append(station.code)
                if graph == _('vs_Altitude'):
                    x.append(float(station.alt))
                y.append(get_statistic[statistics[enum]])

            # do that matplotlib plot zeros in extreme values
            for value in y:
                if value == 0:
                    y[y.index(value)] = 0.0001

            name_graph = _("{0}_({1})_{2}").format(statistic, globals_vars.config_run['type_var_D'], graph)
            # dynamic with based of number of stations
            with_fig = Station.stations_processed/5+4
            fig = pyplot.figure(figsize=(with_fig, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.set_title(name_graph.replace('_',' '))

            if graph == _('vs_Stations'):
                if graph_options[statistics[enum]] == 'dots':
                    ax.plot(range(1, len(x)+1), y, 'o', color="#638786")
                if graph_options[statistics[enum]] == 'bars':
                    bar(range(1, len(x)+1), y, width=0.8, align='center', color="#638786")
            if graph == _('vs_Altitude'):
                ax.plot(x, y, 'o', color="#638786")

            ## X
            if graph == _('vs_Stations'):
                ax.set_xlabel(_('Stations'))
                locs, labels = xticks(range(1, len(x)+1), x)
                setp(labels, 'rotation', 'vertical')
            if graph == _('vs_Altitude'):
                ax.set_xlabel(_('Altitude (m)'))
                #locs, labels = xticks(range(1, len(x)+1), x)
                #setp(labels, 'rotation', 'vertical')
            ## Y
            # get units os type of var D or I
            if globals_vars.config_run['type_var_D'] in globals_vars.units_of_types_var_D and\
               statistics[enum] not in ['skew', 'kurtosis', 'coef_variation']:
                units = globals_vars.units_of_types_var_D[globals_vars.config_run['type_var_D']]
            else:
                units = '--'
            ax.set_ylabel('{0} ({1})'.format(statistic.replace('_',' '),units))

            pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)
            if graph == _('vs_Stations'):
                if graph_options[statistics[enum]] == 'dots':
                    zoom_graph(ax=ax, x_scale_below=-0.3,x_scale_above=-0.3, y_scale_below=-0.1, y_scale_above=-0.1, abs_x=True)
                if graph_options[statistics[enum]] == 'bars':
                    zoom_graph(ax=ax, x_scale_below=-0.3,x_scale_above=-0.3, y_scale_above=-0.1, abs_x=True)
            if graph == _('vs_Altitude'):
                zoom_graph(ax=ax, x_scale_below=-0.05,x_scale_above=-0.05, y_scale_below=-0.08, y_scale_above=-0.08)

            fig.tight_layout()

            pyplot.savefig(os.path.join(graphs_dir, name_graph + '.png'), dpi=75)

            pyplot.close('all')


# types graphs based on type of var D
types_var_D = {'PPT':{'graph':'bar','color':'#578ECE'}, 'NDPPT':{'graph':'bar','color':'#578ECE'},
               'TMIN':{'graph':'o-','color':'#C08A1C'}, 'TMAX':{'graph':'o-','color':'#C08A1C'},
               'TEMP':{'graph':'o-','color':'#C08A1C'}, 'PATM':{'graph':'*-','color':'#287F2A'},
               'RH':{'graph':'s-','color':'#833680'}, 'RUNOFF':{'graph':'s-','color':'#833680'}}

def graphs_inspection_of_series(stations):
    """
    Graphs for inspection of series, part of EDA.
    """

    # directory for save graphs of descriptive statistic

    graphs_dir = os.path.join(descriptive_statistic_dir, _('Graphs_Inspection_of_Series'))

    if not os.path.isdir(graphs_dir):
        os.makedirs(graphs_dir)


    for station in stations:
        image_open_list = []

        station_image_path = os.path.join(graphs_dir, station.code +'-'+station.name)

        if not os.path.isdir(station_image_path):
            os.makedirs(station_image_path)

        list_graphs = [[station.var_D,'D'], [station.var_I,'I']]

        # add special plot for make mosaic when the frequency off var D and var I are different
        if station.var_D.frequency_data == "daily" and station.var_I.frequency_data == "monthly":
            list_graphs.append([station.var_I, 'special_I'])
        if station.var_D.frequency_data == "monthly" and station.var_I.frequency_data == "daily":
            list_graphs.append([station.var_D, 'special_D'])

        for var, type in list_graphs:
            x = var.date_in_process_period
            y = var.data_in_process_period

            if type != 'special_I' and type != 'special_D':
                type_var = globals_vars.config_run['type_var_'+type]
                name_graph = _("station_{0}-{1}_({2} vs Time)").format(station.code, station.name, type_var)
                len_x = len(x)
            else:
                type_var = globals_vars.config_run['type_var_'+type[-1::]]
                name_graph = _("station_{0}-{1}_({2} vs Time)_stretched").format(station.code, station.name, type_var)

                # add point in end of X-axis
                x.append(x[-1]+relativedelta(months=1))
                y.append(var.data[var.date.index(x[-1])])

                if type == 'special_I':
                    len_x = len(station.var_D.date_in_process_period)
                if type == 'special_D':
                    len_x = len(station.var_I.date_in_process_period)
            # dynamic with based of number of stations
            if var.frequency_data == "monthly":
                with_fig = len_x/10+4
            if var.frequency_data == "daily" or type == 'special_I' or type == 'special_D':
                with_fig = len_x/20+4

            if with_fig > 300:
                with_fig = 300

            fig = pyplot.figure(figsize=(with_fig, 6))
            #fig = pyplot.figure()
            ax = fig.add_subplot(111)
            ax.set_title(name_graph.replace('_',' '))

            # default zoom values
            x_scale_below=-1.0/len_x
            x_scale_above=-2.7/len_x
            y_scale_below=-0.04
            y_scale_above=-0.04

            if var.frequency_data == "daily" or type == 'special_I' or type == 'special_D':
                x_scale_below=-3.0/len_x
                x_scale_above=-6.0/len_x

            if type == 'D' or type == 'special_D':
                if var.frequency_data == "daily" or type == 'special_D':
                    if type_var not in types_var_D:
                        # default for generic type for var D
                        bar(x, y, width=1, align='center', color='#578ECE')
                        y_scale_below=0
                    else:
                        if types_var_D[type_var]['graph'] == 'bar':
                            bar(x, y, width=1, align='center', color=types_var_D[type_var]['color'])
                            y_scale_below=0
                        else:
                            ax.plot(x, y, types_var_D[type_var]['graph'], color=types_var_D[type_var]['color'])
                if var.frequency_data == "monthly" and not type == 'special_D':
                    if type_var not in types_var_D:
                        # default for generic type for var D
                        bar(x, y, width=20, align='center', color='#578ECE')
                        y_scale_below=0
                    else:
                        if types_var_D[type_var]['graph'] == 'bar':
                            bar(x, y, width=20, align='center', color=types_var_D[type_var]['color'])
                            y_scale_below=0
                        else:
                            ax.plot(x, y, types_var_D[type_var]['graph'], color=types_var_D[type_var]['color'])

            if type == 'I' or type == 'special_I':
                ax.plot(x, y, 'o-', color="#638786")

            ## X
            ax.set_xlabel(_('Time'))
            if var.frequency_data == "daily" or type == 'special_I' or type == 'special_D':
                ax.xaxis.set_major_locator(mdates.MonthLocator())  # every month
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                #ax.xaxis.set_minor_locator(mdates.MonthLocator())  # every month
            if var.frequency_data == "monthly" and not type == 'special_I' and not type == 'special_D':
                ax.xaxis.set_major_locator(mdates.YearLocator())  # every year
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.xaxis.set_minor_locator(mdates.MonthLocator())  # every month
            ## Y
            # get units os type of var D or I
            if type_var in globals_vars.units_of_types_var_D:
                units = globals_vars.units_of_types_var_D[type_var]
            elif type_var in globals_vars.units_of_types_var_I:
                units = globals_vars.units_of_types_var_I[type_var]
            else:
                units = '--'
            ax.set_ylabel('{0} ({1})'.format(type_var,units))

            pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)
            zoom_graph(ax=ax, x_scale_below=x_scale_below,x_scale_above=x_scale_above,
                       y_scale_below=y_scale_below, y_scale_above=y_scale_above)

            fig.tight_layout()

            image_path = os.path.join(station_image_path, name_graph + '.png')

            pyplot.savefig(image_path, dpi=75)
            image_open_list.append(image_path)

            pyplot.close('all')


        ## create mosaic
        if station.var_D.frequency_data == "daily" and station.var_I.frequency_data == "monthly":
            image_var_D = img_open(image_open_list[0])
            image_var_I = img_open(image_open_list[2])
        elif station.var_D.frequency_data == "monthly" and station.var_I.frequency_data == "daily":
            image_var_D = img_open(image_open_list[2])
            image_var_I = img_open(image_open_list[1])
        else:
            image_var_D = img_open(image_open_list[0])
            image_var_I = img_open(image_open_list[1])

        # definition height and width of individual image
        width, height = image_var_D.size
        mosaic_dir_save\
            = os.path.join(station_image_path, _('mosaic_station_{0}-{1}.png').format(station.code, station.name))

        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        mosaic_plots = pyplot.figure(figsize=((width) / 75, (height * 2) / 75))
        mosaic_plots.savefig(mosaic_dir_save, dpi=75)
        mosaic = img_open(mosaic_dir_save)

        mosaic.paste(image_var_I, (0, 0))
        mosaic.paste(image_var_D, (0, height))

        mosaic.save(mosaic_dir_save)

        # delete stretched special image for mosaic
        if len(image_open_list) == 3:
            os.remove(image_open_list[2])

        pyplot.close('all')

        #from guppy import hpy; h=hpy()
        #print h.heap()
        #h.iso(1,[],{})

def climatology(stations):
    """
    Climatology table and graphs, part of EDA.
    """

    graphs_dir = os.path.join(descriptive_statistic_dir, _('Graphs_Inspection_of_Series'))

    if not os.path.isdir(graphs_dir):
        os.makedirs(graphs_dir)

    # climatology table file
    open_file_climatology_table\
        = open(os.path.join(graphs_dir, _('Climatology_table_{0}').format(globals_vars.config_run['type_var_D'])+'.csv'), 'w')
    csv_climatology_table = csv.writer(open_file_climatology_table, delimiter=';')

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), globals_vars.month_text[0], globals_vars.month_text[1],
              globals_vars.month_text[2], globals_vars.month_text[3], globals_vars.month_text[4], globals_vars.month_text[5],
              globals_vars.month_text[6], globals_vars.month_text[7], globals_vars.month_text[8], globals_vars.month_text[9],
              globals_vars.month_text[10], globals_vars.month_text[11]]

    csv_climatology_table.writerow(header)

    for station in stations:
        # -------------------------------------------------------------------------
        ## for climatology table
        line = [station.code, station.name, station.lat, station.lon, station.alt,
                '{0}-{1}'.format(station.process_period['start'], station.process_period['end'])]

        var_D = Variable('D')
        var_D.data = station.var_D.data_in_process_period
        var_D.date = station.var_D.date_in_process_period

        if station.var_D.frequency_data == "daily":
            var_D.daily2monthly()

        months = []
        for m in range(1,13):
            values = []
            for iter, value in  enumerate(var_D.data):
                if var_D.date[iter].month == m:
                    values.append(value)
            months.append(mean(values))

        csv_climatology_table.writerow(line + [format_out.number(i) for i in months])

        # -------------------------------------------------------------------------
        ## for climatology graphs
        station_image_path = os.path.join(graphs_dir, station.code +'-'+station.name)

        x = range(1, 13)
        x_labels = [globals_vars.month_text[i] for i in range(12)]
        y = months

        # do that matplotlib plot zeros in extreme values
        for value in y:
            if value == 0:
                y[y.index(value)] = 0.0001

        name_graph = _("climatology"+"_{0}_{1}_{2}").format(station.code, station.name, globals_vars.config_run['type_var_D'])
        # dynamic with based of number of stations
        fig = pyplot.figure()
        ax = fig.add_subplot(111)
        ax.set_title(_("Climatology"+" {0} {1} - {2} ({3}-{4})").format(station.code, station.name,
            globals_vars.config_run['type_var_D'], station.process_period['start'], station.process_period['end']))

        type_var = globals_vars.config_run['type_var_D']

        ## X
        ax.set_xlabel(_('Months'))
        xticks(x, x_labels)

        ## Y
        # get units os type of var D or I
        units = globals_vars.units_of_types_var_D[type_var]
        ax.set_ylabel('{0} ({1})'.format(type_var, units))

        pyplot.subplots_adjust(bottom=0.2)
        ax.grid(True)
        ax.autoscale(tight=True)

        if type_var not in types_var_D:
            # default for generic type for var D
            bar(x, y, align='center', color='#578ECE')
            zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_above=-0.04)
        else:
            if types_var_D[type_var]['graph'] == 'bar':
                bar(x, y, align='center', color=types_var_D[type_var]['color'])
                zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_above=-0.04)
            else:
                ax.plot(x, y, types_var_D[type_var]['graph'], color=types_var_D[type_var]['color'])
                zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_below=-0.04, y_scale_above=-0.04)

        fig.tight_layout()

        pyplot.savefig(os.path.join(station_image_path, name_graph + '.png'), dpi=75)

        pyplot.close('all')

    open_file_climatology_table.close()
    del csv_climatology_table


def global_common_process(stations, var):
    """
    calculate the global common period based on all common process of all series
    """

    if var == 'D':
        firsts = True
        for station in stations:
            if firsts:
                global_common_date = set(station.var_D.date_in_process_period)
                firsts = False
            else:
                global_common_date = global_common_date & set(station.var_D.date_in_process_period)
    if var == 'I':
        firsts = True
        for station in stations:
            if firsts:
                global_common_date = set(station.var_I.date_in_process_period)
                firsts = False
            else:
                global_common_date = global_common_date & set(station.var_I.date_in_process_period)

    global_common_date = list(global_common_date)
    global_common_date.sort()

    # calculate the process period
    #return {'start': global_common_date[0].year, 'end': global_common_date[-1].year}
    return global_common_date

def scatter_plots_of_series(stations):

    # calculate the common period of all common process
    global_common_date_process_var_D = global_common_process(stations, 'D')

    pyplot.figure(figsize=(4*len(stations)/1.5, 3*len(stations)/1.5))

    name_plot = _("scatter_plots_of_series_{0}_{2}-{3}").format(globals_vars.config_run['type_var_D'],
        globals_vars.units_of_types_var_D[globals_vars.config_run['type_var_D']],
        global_common_date_process_var_D[0].year, global_common_date_process_var_D[-1].year)

    title_plot = _("Scatter plots of series - {0} ({1}) {2}-{3}").format(globals_vars.config_run['type_var_D'],
        globals_vars.units_of_types_var_D[globals_vars.config_run['type_var_D']],
        global_common_date_process_var_D[0].year, global_common_date_process_var_D[-1].year)

    pyplot.suptitle(title_plot, y=0.99, fontsize=14)

    for iter_v, station_v in enumerate(stations):
        for iter_h, station_h in enumerate(stations):
            x = station_h.var_D.data[station_h.var_D.date.index(global_common_date_process_var_D[0]):\
            station_h.var_D.date.index(global_common_date_process_var_D[-1])+1]

            y = station_v.var_D.data[station_v.var_D.date.index(global_common_date_process_var_D[0]):\
            station_v.var_D.date.index(global_common_date_process_var_D[-1])+1]

            ax = pyplot.subplot2grid((len(stations),len(stations)),(iter_v,iter_h))

            ax.scatter(x,y, marker='o', color="#638786", edgecolors="#3C5250")

            if iter_h == 0:
                ax.set_ylabel(station_v.code)
            else:
                ax.set_yticklabels([])
            if iter_v == len(stations)-1:
                ax.set_xlabel(station_h.code)
            else:
                ax.set_xticklabels([])

            ax.grid(True)
            ax.autoscale(tight=True)

            pyplot.tight_layout()

    pyplot.subplots_adjust(top=0.002*len(stations)+0.95)

    image_path = os.path.join(distribution_test_dir, name_plot + '.png')

    pyplot.savefig(image_path, dpi=75)

    pyplot.close('all')


def frequency_histogram(stations):
    pass
