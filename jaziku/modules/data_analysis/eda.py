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
import copy
import matplotlib.dates as mdates
from math import log10
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot
from numpy import histogram
from pylab import xticks, bar, boxplot
from Image import open as img_open
from scipy.stats import shapiro
from calendar import monthrange

from jaziku.env import globals_vars, config_run
from jaziku.core.station import Station
from jaziku.core.variable import Variable
from jaziku.core.analysis_interval import get_values_in_range_analysis_interval, locate_day_in_analysis_interval, \
    get_range_analysis_interval, get_state_of_data, set_global_state_of_data
from jaziku.modules.climate import lags
from jaziku.modules.climate.contingency_table import get_category_of_phenomenon
from jaziku.modules.climate.lags import  calculate_lags
from jaziku.utils import  console, format_out, watermarking, array


def main(stations_list):

    # -------------------------------------------------------------------------
    # EXPLORATORY DATA ANALYSIS
    # -------------------------------------------------------------------------

    console.msg(_("\n################# EXPLORATORY DATA ANALYSIS:"))

    if not config_run.settings['graphics']:
        console.msg(_("\n > WARNING: The 'graphics' in 'output options' is disabled,\n"
                      "   all graphics for EDA module will not be created. The graphics\n"
                      "   in EDA module represents the vast majority of the results.\n"), color='yellow')

    global eda_dir
    eda_dir = os.path.join(globals_vars.DATA_ANALYSIS_DIR, 'EDA')

    # -------------------------------------------------------------------------
    # DESCRIPTIVE STATISTICS
    # -------------------------------------------------------------------------

    console.msg(_("Descriptive statistics ............................... "), newline=False)

    # -------------------------------------------------------------------------
    # FILES OF DESCRIPTIVE STATISTICS

    global shapiro_wilks_dir
    shapiro_wilks_dir = os.path.join(eda_dir, _('Descriptive_Statistic'))

    if not os.path.isdir(shapiro_wilks_dir):
        os.makedirs(shapiro_wilks_dir)

    file_descriptive_statistics_var_D\
    = os.path.join(shapiro_wilks_dir, _('Descriptive_Statistics_{0}.csv').format(config_run.settings['type_var_D']))

    file_descriptive_statistics_var_I\
    = os.path.join(shapiro_wilks_dir, _('Descriptive_Statistics_{0}.csv').format(config_run.settings['type_var_I']))

    open_file_D = open(file_descriptive_statistics_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

    open_file_I = open(file_descriptive_statistics_var_I, 'w')
    csv_file_I = csv.writer(open_file_I, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), _('SIZE DATA'), _('MAXIMUM'),
              _('MINIMUM'), _('AVERAGE'), _('MEDIAN'), _('STD DEVIATION'), _('SKEWNESS'), _('VARIANCE'), _('KURTOSIS'), _('COEFF VARIATION')]

    csv_file_D.writerow(header)
    csv_file_I.writerow(header)

    for station in stations_list:

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
            format_out.number(station.var_D.skewness, 4),
            format_out.number(station.var_D.variance, 4),
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
            format_out.number(station.var_I.skewness, 4),
            format_out.number(station.var_I.variance, 4),
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
    if config_run.settings['graphics']:
        if Station.stations_processed > 1:
            with console.redirectStdStreams():
                descriptive_statistic_graphs(stations_list)
            console.msg(_("done"), color='green')
        else:
            console.msg(_("partial\n > WARNING: There is only one station for process\n"
                          "   the graphs for descriptive statistic need more \n"
                          "   of one station."), color="yellow")
    else:
        console.msg(_("done"), color='green')


    # -------------------------------------------------------------------------
    # GRAPHS INSPECTION OF SERIES

    if config_run.settings['graphics']:
        console.msg(_("Graphs inspection of series .......................... "), newline=False)
        with console.redirectStdStreams():
            graphs_inspection_of_series(stations_list)
        console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # CLIMATOLOGY

    console.msg(_("Climatology .......................................... "), newline=False)
    with console.redirectStdStreams():
        climatology(stations_list)
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

    if config_run.settings['graphics']:

        console.msg(_("Scatter plots of series .............................. "), newline=False)

        if 1 < Station.stations_processed <= 10:
            with console.redirectStdStreams():
                scatter_plots_of_series(stations_list)
            console.msg(_("done"), color='green')
        else:
            if Station.stations_processed == 1:
                console.msg(_("partial\n > WARNING: There is only one station for process\n"
                              "   the scatter plots of series, this need more \n"
                              "   of one station."), color="yellow")
            else:
                console.msg(_("partial\n > WARNING: The maximum limit for make the scatter plots\n"
                              "   of series are 10 stations, if you want this diagram,\n"
                              "   please divide the stations in regions into different\n"
                              "   runfiles with maximum 10 stations per runfile, and\n"
                              "   rerun each runfile."), color="yellow")

    # -------------------------------------------------------------------------
    # FREQUENCY HISTOGRAM

    if config_run.settings['graphics']:
        console.msg(_("Frequency histogram .................................. "), newline=False)
        with console.redirectStdStreams():
            frequency_histogram(stations_list)
        console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # SHAPIRO WILKS

    console.msg(_("Shapiro Wilks test ................................... "), newline=False)

    shapiro_wilks_test(stations_list)
    console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # OUTLIERS

    global outliers_dir
    outliers_dir = os.path.join(eda_dir, _('Outliers'))

    if not os.path.isdir(outliers_dir):
        os.makedirs(outliers_dir)

    console.msg(_("Outliers ............................................. "), newline=False)
    with console.redirectStdStreams():
        outliers(stations_list)

    if Station.stations_processed > 50:
        console.msg(_("partial\n > WARNING: The maximum limit for make the box-plot of\n"
                      "   outliers of all stations are 50 stations, if you want\n"
                      "   this box-plot, please divide the stations in regions\n"
                      "   into different runfiles with maximum 50 stations per\n"
                      "   runfile, and rerun each runfile."), color="yellow")
    else:
        console.msg(_("done"), color='green')


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



def descriptive_statistic_graphs(stations_list):
    """
    Graphs statistics vs stations and statistics vs altitude for var D
    """
    statistics = ['size_data', 'maximum', 'minimum', 'average', 'median', 'std_dev','skewness', 'kurtosis', 'coef_variation']
    statistics_to_graphs = [_('Sizes_data'), _('Maximums'), _('Minimums'), _('Averages'), _('Medians'),
                            _('Std_deviations'), _('skewness'), _('Kurtosis'), _('Coeff_variations')]
    graph_options = {'size_data':'bars', 'maximum':'bars', 'minimum':'bars', 'average':'bars', 'median':'bars',
                     'std_dev':'dots','skewness':'dots', 'kurtosis':'dots', 'coef_variation':'dots'}

    # directory for save graphs of descriptive statistic
    graphs_dir = os.path.join(shapiro_wilks_dir, _('Graphs_for_{0}').format(config_run.settings['type_var_D']))

    if not os.path.isdir(graphs_dir):
        os.makedirs(graphs_dir)

    #for type, var in [[config_run.get['type_var_D'],'var_D'], [config_run.get['type_var_I'],'var_I']]:
    for graph in [_('vs_Stations'), _('vs_Altitude')]:

        for enum, statistic in enumerate(statistics_to_graphs):
            x = []
            y = []
            for station in stations_list:
                get_statistic = {'size_data':station.var_D.size_data, 'maximum':station.var_D.maximum,
                                 'minimum':station.var_D.minimum, 'average':station.var_D.average,
                                 'median':station.var_D.median, 'std_dev':station.var_D.std_dev,
                                 'skewness':station.var_D.skewness, 'kurtosis':station.var_D.kurtosis,
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

            name_graph = _("{0}_({1})_{2}").format(statistic, config_run.settings['type_var_D'], graph)
            # dynamic with based of number of stations
            with_fig = Station.stations_processed/5+4
            fig = pyplot.figure(figsize=(with_fig, 6), dpi=100)
            ax = fig.add_subplot(111)
            #tfs = 18.5 - 10/(Station.stations_processed)

            if Station.stations_processed <= 5:
                title = _("{0} ({1})\n{2}").format(statistic.replace('_',' '), config_run.settings['type_var_D'], graph.replace('_',' '))
            else:
                title = name_graph.replace('_',' ')

            ax.set_title(unicode(title, 'utf-8'), globals_vars.graphs_title_properties())

            if graph == _('vs_Stations'):
                if graph_options[statistics[enum]] == 'dots':
                    ax.plot(range(1, len(x)+1), y, 'o', color="#638786", markersize=8.5)
                if graph_options[statistics[enum]] == 'bars':
                    bar(range(1, len(x)+1), y, width=0.8, align='center', color="#638786")
            if graph == _('vs_Altitude'):
                ax.plot(x, y, 'o', color="#638786", markersize=8.5)

            ## X
            if graph == _('vs_Stations'):
                ax.set_xlabel(unicode(_('Stations'), 'utf-8'), globals_vars.graphs_axis_properties())
                xticks(range(1, len(x)+1), x, rotation='vertical')
            if graph == _('vs_Altitude'):
                ax.set_xlabel(_('Altitude (m)'), globals_vars.graphs_axis_properties())
                #locs, labels = xticks(range(1, len(x)+1), x)
                #setp(labels, 'rotation', 'vertical')
            ## Y
            # get units os type of var D or I
            if statistics[enum] not in ['skewness', 'kurtosis', 'coef_variation']:
                units = globals_vars.units_var_D
            else:
                units = '--'
            ax.set_ylabel(unicode('{0} ({1})'.format(statistic.replace('_',' '),units), 'utf-8'), globals_vars.graphs_axis_properties())

            pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)
            if graph == _('vs_Stations'):
                if graph_options[statistics[enum]] == 'dots':
                    zoom_graph(ax=ax, x_scale_below=-0.3,x_scale_above=-0.3, y_scale_below=-0.1, y_scale_above=-0.1, abs_x=True)
                if graph_options[statistics[enum]] == 'bars':
                    zoom_graph(ax=ax, x_scale_below=-0.3,x_scale_above=-0.3, y_scale_above=-0.1, abs_x=True)
            if graph == _('vs_Altitude'):
                zoom_graph(ax=ax, x_scale_below=-0.07,x_scale_above=-0.07, y_scale_below=-0.08, y_scale_above=-0.08)

            fig.tight_layout()

            # save image
            image = os.path.join(graphs_dir, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')


# types graphs based on type of var D
types_var_D = {'PPT':{'graph':'bar','color':'#578ECE'}, 'NDPPT':{'graph':'bar','color':'#578ECE'},
               'TMIN':{'graph':'o-','color':'#C08A1C'}, 'TMAX':{'graph':'o-','color':'#C08A1C'},
               'TEMP':{'graph':'o-','color':'#C08A1C'}, 'PATM':{'graph':'*-','color':'#287F2A'},
               'RH':{'graph':'s-','color':'#833680'}, 'RUNOFF':{'graph':'s-','color':'#833680'}}

def graphs_inspection_of_series(stations_list):
    """
    Graphs for inspection of series, part of EDA.
    """

    # directory for save graphs of descriptive statistic

    graphs_dir = os.path.join(shapiro_wilks_dir, _('Graphs_Inspection_of_Series'))

    if not os.path.isdir(graphs_dir):
        os.makedirs(graphs_dir)


    for station in stations_list:
        image_list = []

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

            # number of year for process
            num_years = station.process_period['end'] - station.process_period['start']

            if type != 'special_I' and type != 'special_D':
                type_var = config_run.settings['type_var_'+type]
                name_graph = _("Station_{0}-{1}_({2}_vs_Time)").format(station.code, station.name, type_var)
                len_x = len(x)
            else:
                type_var = config_run.settings['type_var_'+type[-1::]]
                name_graph = _("_Station_{0}-{1}_({2}_vs_Time)_").format(station.code, station.name, type_var)

                # add point in end of X-axis
                x.append(x[-1]+relativedelta(months=1))
                y.append(var.data[var.date.index(x[-1])])

                if type == 'special_I':
                    len_x = len(station.var_D.date_in_process_period)
                if type == 'special_D':
                    len_x = len(station.var_I.date_in_process_period)
                # dynamic with based of number of stations
            if var.frequency_data == "monthly":
                with_fig = 8 + len_x/150
            if var.frequency_data == "daily" or type == 'special_I' or type == 'special_D':
                #with_fig = len_x/20+4
                with_fig = 12

            fig = pyplot.figure(figsize=(with_fig, 5))
            #fig = pyplot.figure()
            ax = fig.add_subplot(111)
            ax.set_title(unicode(name_graph.replace('_',' '), 'utf-8'), globals_vars.graphs_title_properties())

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
                        ax.plot(x, y, '-', color="#638786")
                    else:
                        if types_var_D[type_var]['graph'] == 'bar':
                            bar(x, y, align='center', color=types_var_D[type_var]['color'], width=1+num_years/5, edgecolor='none')
                            y_scale_below=0
                        else:
                            #ax.plot(x, y, TYPES_VAR_D[type_var]['graph'], color=TYPES_VAR_D[type_var]['color'])
                            ax.plot(x, y, '-', color=types_var_D[type_var]['color'])
                if var.frequency_data == "monthly" and not type == 'special_D':
                    if type_var not in types_var_D:
                        # default for generic type for var D
                        ax.plot(x, y, '-', color="#638786")
                    else:
                        if types_var_D[type_var]['graph'] == 'bar':
                            bar(x, y, align='center', color=types_var_D[type_var]['color'], width=20+num_years/5, edgecolor='none')
                            y_scale_below=0
                        else:
                            ax.plot(x, y, '-', color=types_var_D[type_var]['color'])

            if type == 'I' or type == 'special_I':
                ax.plot(x, y, '-', color="#638786")

            ## X
            ax.set_xlabel(_('Time'), globals_vars.graphs_axis_properties())
            ax.xaxis.set_major_locator(mdates.YearLocator())  # every year
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            if num_years < 20:
                ax.xaxis.set_minor_locator(mdates.MonthLocator())  # every month
            xticks(rotation='vertical')

            ## Y
            # set units type of var D or I
            if type in ['special_D', 'D']:
                units = globals_vars.units_var_D
            if type in ['special_I', 'I']:
                units = globals_vars.units_var_I

            ax.set_ylabel(unicode('{0} ({1})'.format(type_var,units), 'utf-8'), globals_vars.graphs_axis_properties())

            pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)
            zoom_graph(ax=ax, x_scale_below=x_scale_below,x_scale_above=x_scale_above,
                y_scale_below=y_scale_below, y_scale_above=y_scale_above)

            fig.tight_layout()

            image_path = os.path.join(station_image_path, name_graph + '.png')

            # save image
            pyplot.savefig(image_path, dpi=75)

            image_list.append(image_path)

            pyplot.close('all')


        ## create mosaic
        if station.var_D.frequency_data == "daily" and station.var_I.frequency_data == "monthly":
            image_var_D = img_open(image_list[0])
            image_var_I = img_open(image_list[2])
        elif station.var_D.frequency_data == "monthly" and station.var_I.frequency_data == "daily":
            image_var_D = img_open(image_list[2])
            image_var_I = img_open(image_list[1])
        else:
            image_var_D = img_open(image_list[0])
            image_var_I = img_open(image_list[1])

        # definition height and width of individual image
        width, height = image_var_D.size
        mosaic_dir_save = os.path.join(station_image_path, _('mosaic_station_{0}-{1}.png').format(station.code, station.name))

        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        mosaic_plots = pyplot.figure(figsize=((width) / 75, (height * 2) / 75))
        mosaic_plots.savefig(mosaic_dir_save, dpi=75)
        mosaic = img_open(mosaic_dir_save)

        mosaic.paste(image_var_I, (0, 0))
        mosaic.paste(image_var_D, (0, height))

        mosaic.save(mosaic_dir_save)

        # stamp logo
        watermarking.logo(mosaic_dir_save)

        # delete stretched special image for mosaic
        if len(image_list) == 3:
            os.remove(image_list[2])
            del image_list[2]

        # stamp logo
        for image in image_list:
            watermarking.logo(image)

        pyplot.close('all')

        #from guppy import hpy; h=hpy()
        #print h.heap()
        #h.iso(1,[],{})

def climatology(stations_list):
    """
    Climatology table and graphs, part of EDA.
    """

    graphs_dir = os.path.join(shapiro_wilks_dir, _('Graphs_Inspection_of_Series'))

    if not os.path.isdir(graphs_dir):
        os.makedirs(graphs_dir)

    # climatology table file
    open_file_climatology_table\
        = open(os.path.join(graphs_dir, _('Climatology_table_{0}').format(config_run.settings['type_var_D'])+'.csv'), 'w')
    csv_climatology_table = csv.writer(open_file_climatology_table, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), globals_vars.get_month_in_text(0), globals_vars.get_month_in_text(1),
              globals_vars.get_month_in_text(2), globals_vars.get_month_in_text(3), globals_vars.get_month_in_text(4), globals_vars.get_month_in_text(5),
              globals_vars.get_month_in_text(6), globals_vars.get_month_in_text(7), globals_vars.get_month_in_text(8), globals_vars.get_month_in_text(9),
              globals_vars.get_month_in_text(10), globals_vars.get_month_in_text(11)]

    csv_climatology_table.writerow(header)

    for station in stations_list:
        # -------------------------------------------------------------------------
        ## for climatology table
        line = [station.code, station.name, station.lat, station.lon, station.alt,
                '{0}-{1}'.format(station.process_period['start'], station.process_period['end'])]

        var_D = Variable('D')
        var_D.data = station.var_D.data_in_process_period
        var_D.date = station.var_D.date_in_process_period

        y_mean = []
        y_max = [] # value to add to mean for max value
        y_min = [] # value to subtract to mean for min value
        if station.var_D.frequency_data == "monthly":
            for month in range(1,13):
                values = []
                for iter, value in  enumerate(var_D.data):
                    if var_D.date[iter].month == month:
                        values.append(value)
                values = array.clean(values)
                y_mean.append(array.mean(values))
                y_max.append(array.maximum(values) - y_mean[-1])
                y_min.append(y_mean[-1] - array.minimum(values))

        if station.var_D.frequency_data == "daily":
            for month in range(1,13):
                years_values_mean = []
                years_values_max = []
                years_values_min = []
                for year in range(station.process_period['start'], station.process_period['end']+1):
                    month_values = []
                    for iter, value in  enumerate(var_D.data):
                        if var_D.date[iter].year == year and var_D.date[iter].month == month:
                            month_values.append(value)
                    month_values = array.clean(month_values)
                    years_values_mean.append(array.mean(month_values))
                    years_values_max.append(array.maximum(month_values))
                    years_values_min.append(array.minimum(month_values))
                y_mean.append(array.mean(years_values_mean))
                y_max.append(array.mean(years_values_max) - y_mean[-1])
                y_min.append(y_mean[-1] - array.mean(years_values_min))

        csv_climatology_table.writerow(line + [format_out.number(i) for i in y_mean])

        if not config_run.settings['graphics']:
            continue

        # -------------------------------------------------------------------------
        # for climatology graphs, month by month (base)

        station_climatology_path = os.path.join(graphs_dir, station.code +'-'+station.name, _('Climatology'))

        if not os.path.isdir(station_climatology_path):
            os.makedirs(station_climatology_path)

        x = range(1, 13)
        x_labels = [globals_vars.get_month_in_text(i) for i in range(12)]

        # do that matplotlib plot zeros in extreme values
        for value in y_mean:
            if value == 0:
                y_mean[y_mean.index(value)] = 0.0001

        title=_("Multiyear climatology (monthly)\n{0} {1} - {2} ({3}-{4})").format(station.code, station.name,
                config_run.settings['type_var_D'], station.process_period['start'], station.process_period['end'])

        # -------------------------------------------------------------------------
        # climatology monthly without whiskers

        name_graph = _("Multiyear_climatology_(monthly)_{0}_{1}_{2}").format(station.code, station.name, config_run.settings['type_var_D'])

        fig = pyplot.figure(figsize=(8, 5.5))
        ax = fig.add_subplot(111)

        ax.set_title(unicode(title, 'utf-8'), globals_vars.graphs_title_properties())

        type_var = config_run.settings['type_var_D']

        ## X
        ax.set_xlabel(_('Months'), globals_vars.graphs_axis_properties())
        xticks(x, x_labels)

        ## Y
        # get units os type of var D or I
        ax.set_ylabel(unicode('{0} ({1}) - '.format(type_var, globals_vars.units_var_D) + _('[mean]'), 'utf-8'), globals_vars.graphs_axis_properties())

        #pyplot.subplots_adjust(bottom=0.2)
        ax.grid(True)
        ax.autoscale(tight=True)

        if type_var not in types_var_D:
            # default for generic type for var D
            #ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color='#638786', mec='#638786', mew=3, linewidth=2.5, elinewidth=1)
            ax.plot(x, y_mean, '-o', color='#638786', mec='#638786', linewidth=2.5, markersize=8)
            zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_below=-0.04, y_scale_above=-0.04)
        else:
            if types_var_D[type_var]['graph'] == 'bar':
                bar(x, y_mean, align='center', color=types_var_D[type_var]['color'])
                #ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_above=-0.04)
            else:
                #ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=TYPES_VAR_D[type_var]['color'],
                #    mec=TYPES_VAR_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                ax.plot(x, y_mean, '-o', color=types_var_D[type_var]['color'], mec=types_var_D[type_var]['color'], linewidth=2.5, markersize=8)
                zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_below=-0.04, y_scale_above=-0.04)


        # labels on both sides
        #ax.tick_params(labeltop=False, labelright=True)

        fig.tight_layout()

        # save image
        image = os.path.join(station_climatology_path, name_graph + '.png')
        pyplot.savefig(image, dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')

        # -------------------------------------------------------------------------
        # climatology monthly with whiskers

        name_graph = _("Multiyear_climatology_(monthly+whiskers)_{0}_{1}_{2}").format(station.code, station.name, config_run.settings['type_var_D'])

        fig = pyplot.figure(figsize=(8, 5.5))
        ax = fig.add_subplot(111)

        ax.set_title(unicode(title, 'utf-8'), globals_vars.graphs_title_properties())

        type_var = config_run.settings['type_var_D']

        ## X
        ax.set_xlabel(_('Months'), globals_vars.graphs_axis_properties())
        xticks(x, x_labels)

        ## Y
        # get units os type of var D or I
        ax.set_ylabel(unicode(('{0} ({1}) - ' + _('[min-mean-max]')).format(type_var, globals_vars.units_var_D), 'utf-8'), globals_vars.graphs_axis_properties())

        #pyplot.subplots_adjust(bottom=0.2)
        ax.grid(True)
        ax.autoscale(tight=True)

        if type_var not in types_var_D:
            # default for generic type for var D
            ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color='#638786', mec='#638786', mew=3, linewidth=2.5, elinewidth=1)
            #bar(x, y_mean, align='center', color='#638786')
            zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_below=-0.04, y_scale_above=-0.04)
        else:
            if types_var_D[type_var]['graph'] == 'bar':
                bar(x, y_mean, align='center', color=types_var_D[type_var]['color'])
                ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_above=-0.04)
            else:
                ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=types_var_D[type_var]['color'],
                    mec=types_var_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                #ax.plot(x, y_mean, TYPES_VAR_D[type_var]['graph'], color=TYPES_VAR_D[type_var]['color'])
                zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_below=-0.04, y_scale_above=-0.04)


        # labels on both sides
        #ax.tick_params(labeltop=False, labelright=True)

        fig.tight_layout()
        # save image
        image = os.path.join(station_climatology_path, name_graph + '.png')
        pyplot.savefig(image, dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')

        # -------------------------------------------------------------------------
        # climatology monthly table (csv)

        name_csv_table = _("Multiyear_climatology_table_{0}_{1}_{2}.csv").format(station.code, station.name, config_run.settings['type_var_D'])
        open_file = open(os.path.join(station_climatology_path,name_csv_table), 'w')
        csv_table = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

        # print header
        header = [''] + x_labels
        csv_table.writerow(header)

        # max values
        csv_table.writerow( [_('max')] + [ format_out.number(x + y_max[i]) for i,x in enumerate(y_mean) ] )

        # mean values
        csv_table.writerow( [_('mean')] + [ format_out.number(x) for x in y_mean ] )

        # min values
        csv_table.writerow( [_('min')] + [ format_out.number(x - y_min[i]) for i,x in enumerate(y_mean) ] )

        open_file.close()
        del csv_table

        # -------------------------------------------------------------------------
        ## for climatology graphs, every 5, 10 or 15 days based to analysis interval

        if station.var_D.frequency_data == "daily" and not config_run.settings['analysis_interval'] == "trimester":
            y_mean = []
            y_max = [] # value to add to mean for max value
            y_min = [] # value to subtract to mean for min value
            range_analysis_interval = get_range_analysis_interval()
            for month in range(1, 13):
                for day in range_analysis_interval:
                    range_analysis_mean = []
                    range_analysis_max = []
                    range_analysis_min = []

                    iter_year = station.process_period['start']
                    # iteration for years from first-year +1 to end-year -1 inside
                    # range common_period
                    while iter_year <= station.process_period['end']:
                        # test if day exist in month and year
                        if day > monthrange(iter_year, month)[1]:
                            iter_year += relativedelta(years= +1)
                            continue

                        values = get_values_in_range_analysis_interval(station,'D', iter_year, month, day)
                        values = array.clean(values)
                        range_analysis_mean.append(array.mean(values))
                        range_analysis_max.append(array.maximum(values))
                        range_analysis_min.append(array.minimum(values))

                        iter_year += 1
                    y_mean.append(array.mean(range_analysis_mean))
                    y_max.append(array.mean(range_analysis_max) - y_mean[-1])
                    y_min.append(y_mean[-1] - array.mean(range_analysis_min))

            x = range(1, len(y_mean)+1)
            x_step_label = len(y_mean)/12
            x_labels = []
            for i in range(len(y_mean)):
                if i%x_step_label == 0:
                    x_labels.append(globals_vars.get_month_in_text(i/x_step_label))
                else:
                    x_labels.append('')

            title = _("Multiyear climatology (each {0} days)\n{1} {2} - {3} ({4}-{5})").format(globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, config_run.settings['type_var_D'], station.process_period['start'],
                station.process_period['end'])

            # -------------------------------------------------------------------------
            # climatology N days without whiskers

            name_graph = _("Multiyear_climatology_({0}days)_{1}_{2}_{3}").format(globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, config_run.settings['type_var_D'])

            with_fig = 5 + len(y_mean)/9
            fig = pyplot.figure(figsize=(with_fig, 5.5))
            ax = fig.add_subplot(111)
            ax.set_title(unicode(title, 'utf-8'), globals_vars.graphs_title_properties())

            type_var = config_run.settings['type_var_D']

            ## X
            ax.set_xlabel(_('Months'), globals_vars.graphs_axis_properties())
            xticks(x, x_labels)

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode('{0} ({1}) - '.format(type_var, globals_vars.units_var_D) + _('[mean]'), 'utf-8'), globals_vars.graphs_axis_properties())

            #pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)

            x_scale_value = -0.013 - globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL/600.0

            if type_var not in types_var_D:
                # default for generic type for var D
                #ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color='#638786', mec='#638786', mew=3, linewidth=2.5, elinewidth=1)
                ax.plot(x, y_mean, '-o', color='#638786', mec='#638786', linewidth=2.5, markersize=8)
                zoom_graph(ax=ax, x_scale_below=x_scale_value,x_scale_above=x_scale_value, y_scale_below=-0.04, y_scale_above=-0.04)
            else:
                if types_var_D[type_var]['graph'] == 'bar':
                    bar(x, y_mean, align='center', color=types_var_D[type_var]['color'])
                    #ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value,x_scale_above=x_scale_value, y_scale_above=-0.04)
                else:
                    ax.plot(x, y_mean, '-o', color=types_var_D[type_var]['color'], mec=types_var_D[type_var]['color'], linewidth=2.5, markersize=8)
                    #ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=TYPES_VAR_D[type_var]['color'],
                    #    mec=TYPES_VAR_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value,x_scale_above=x_scale_value, y_scale_below=-0.04, y_scale_above=-0.04)

            # labels on both sides
            #ax.tick_params(labeltop=False, labelright=True)

            fig.tight_layout()

            # save image
            image = os.path.join(station_climatology_path, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

            # -------------------------------------------------------------------------
            # climatology N days with whiskers

            name_graph = _("Multiyear_climatology_({0}days+whiskers)_{1}_{2}_{3}").format(globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, config_run.settings['type_var_D'])

            with_fig = 5 + len(y_mean)/9
            fig = pyplot.figure(figsize=(with_fig, 5.5))
            ax = fig.add_subplot(111)
            ax.set_title(unicode(title, 'utf-8'), globals_vars.graphs_title_properties())

            type_var = config_run.settings['type_var_D']

            ## X
            ax.set_xlabel(_('Months'), globals_vars.graphs_axis_properties())
            xticks(x, x_labels)

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode(('{0} ({1}) - ' + _('[min-mean-max]')).format(type_var, globals_vars.units_var_D), 'utf-8'), globals_vars.graphs_axis_properties())

            #pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)

            x_scale_value = -0.013 - globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL/600.0

            if type_var not in types_var_D:
                # default for generic type for var D
                ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color='#638786', mec='#638786', mew=3, linewidth=2.5, elinewidth=1)
                zoom_graph(ax=ax, x_scale_below=x_scale_value,x_scale_above=x_scale_value, y_scale_below=-0.04, y_scale_above=-0.04)
                #bar(x, y_mean, align='center', color='#638786')
            else:
                if types_var_D[type_var]['graph'] == 'bar':
                    bar(x, y_mean, align='center', color=types_var_D[type_var]['color'])
                    ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value,x_scale_above=x_scale_value, y_scale_above=-0.04)
                else:
                    #ax.plot(x, y_mean, TYPES_VAR_D[type_var]['graph'], color=TYPES_VAR_D[type_var]['color'])
                    ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=types_var_D[type_var]['color'],
                        mec=types_var_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value,x_scale_above=x_scale_value, y_scale_below=-0.04, y_scale_above=-0.04)

            # labels on both sides
            #ax.tick_params(labeltop=False, labelright=True)

            fig.tight_layout()

            # save image
            image = os.path.join(station_climatology_path, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

            # -------------------------------------------------------------------------
            # climatology N days table (csv)

            name_csv_table = _("Multiyear_climatology_table_{0}days_{1}_{2}_{3}.csv").format(globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL, station.code, station.name, config_run.settings['type_var_D'])
            open_file = open(os.path.join(station_climatology_path,name_csv_table), 'w')
            csv_table = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

            # print header
            header = ['']
            for month in range(1, 13):
                for day in get_range_analysis_interval():
                    header.append(globals_vars.get_month_in_text(month-1) +' '+str(day))

            csv_table.writerow(header)

            # max values
            csv_table.writerow( [_('max')] + [ format_out.number(x + y_max[i]) for i,x in enumerate(y_mean) ] )

            # mean values
            csv_table.writerow( [_('mean')] + [ format_out.number(x) for x in y_mean ] )

            # min values
            csv_table.writerow( [_('min')] + [ format_out.number(x - y_min[i]) for i,x in enumerate(y_mean) ] )

            open_file.close()
            del csv_table

    open_file_climatology_table.close()
    del csv_climatology_table


def global_common_process(stations_list, var):
    """
    Calculate the global common period of all stations
    based on all common process period of all series var D or I

    :arg:
        stations: list of all stations
        var: 'D' or 'I'
    :return:
        chronological order list of all date (monthly or daily)
        inside of global common process
    """

    if var == 'D':
        firsts = True
        for station in stations_list:
            if firsts:
                global_common_date = set(station.var_D.date_in_process_period)
                firsts = False
            else:
                global_common_date = global_common_date & set(station.var_D.date_in_process_period)
    if var == 'I':
        firsts = True
        for station in stations_list:
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

def scatter_plots_of_series(stations_list):

    # calculate the common period of all common process
    global_common_date_process_var_D = global_common_process(stations_list, 'D')

    fig_height = 3.2*len(stations_list)/1.5
    fig_with = 4*len(stations_list)/1.5

    pyplot.figure(figsize=(fig_with,fig_height))

    name_plot = _("scatter_plots_of_series") + "_{0}_{2}-{3}".format(config_run.settings['type_var_D'],
        globals_vars.units_var_D,
        global_common_date_process_var_D[0].year, global_common_date_process_var_D[-1].year)

    title_plot = _("Scatter plots of series") + "\n{0} ({1}) {2}-{3}".format(config_run.settings['type_var_D'],
        globals_vars.units_var_D,
        global_common_date_process_var_D[0].year, global_common_date_process_var_D[-1].year)

    pyplot.suptitle(unicode(title_plot, 'utf-8'), y=(fig_height-0.1)/fig_height, fontsize=14)

    for iter_v, station_v in enumerate(stations_list):
        for iter_h, station_h in enumerate(stations_list):
            x = station_h.var_D.data[station_h.var_D.date.index(global_common_date_process_var_D[0]):\
            station_h.var_D.date.index(global_common_date_process_var_D[-1])+1]

            y = station_v.var_D.data[station_v.var_D.date.index(global_common_date_process_var_D[0]):\
            station_v.var_D.date.index(global_common_date_process_var_D[-1])+1]

            ax = pyplot.subplot2grid((len(stations_list),len(stations_list)),(iter_v,iter_h))

            ax.scatter(x,y, marker='o', color="#638786", edgecolors="#3C5250")

            if iter_h == 0:
                ax.set_ylabel(station_v.code, globals_vars.graphs_axis_properties())
            else:
                ax.set_yticklabels([])
            if iter_v == len(stations_list)-1:
                ax.set_xlabel(unicode(station_h.code, 'utf-8'), globals_vars.graphs_axis_properties())
            else:
                ax.set_xticklabels([])

            ax.grid(True)
            ax.autoscale(tight=True)

            pyplot.tight_layout(pad=0.8)

    # adjust title plot
    pyplot.subplots_adjust(top=(fig_height-0.6)/fig_height)

    image_path = os.path.join(distribution_test_dir, name_plot + '.png')

    # save image
    pyplot.savefig(image_path, dpi=75)

    # stamp logo
    watermarking.logo(image_path)

    pyplot.close('all')


def frequency_histogram(stations_list):

    frequency_histogram_dir = os.path.join(distribution_test_dir, _('Frequency_histogram'))

    if not os.path.isdir(frequency_histogram_dir):
        os.makedirs(frequency_histogram_dir)

    for station in stations_list:

        n = station.var_D.size_data

        # bins based on sturges formula
        bins = 1 + 3.3*log10(n)

        hist, bin_edges = histogram(station.var_D.data_filtered_in_process_period, bins=bins)

        name_graph = _("frequency_histogram_{0}_{1}_{2}").format(station.code, station.name, config_run.settings['type_var_D'])

        fig = pyplot.figure()
        ax = fig.add_subplot(111)
        ax.set_title(unicode(_("Frequency histogram\n{0} {1} - {2} ({3}-{4})").format(station.code, station.name,
            config_run.settings['type_var_D'], station.process_period['start'], station.process_period['end']), 'utf-8'), globals_vars.graphs_title_properties())


        ## X
        type_var = config_run.settings['type_var_D']
        ax.set_xlabel(unicode('{0} ({1})'.format(type_var, globals_vars.units_var_D), 'utf-8'), globals_vars.graphs_axis_properties())

        ## Y
        ax.set_ylabel(_('Frequency'), globals_vars.graphs_axis_properties())

        width = 0.7 * (bin_edges[1] - bin_edges[0])
        center = (bin_edges[:-1] + bin_edges[1:]) / 2
        bar(center,hist,align='center', color='#638786', width=width)

        ax.grid(True)
        ax.autoscale(tight=True)

        zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_above=-0.04)

        fig.tight_layout()

        # save image
        image = os.path.join(frequency_histogram_dir, name_graph + '.png')
        pyplot.savefig(image, dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')


def shapiro_wilks_test(stations_list):

    file_shapiro_wilks_var_D\
    = os.path.join(distribution_test_dir, _('shapiro_wilks_test_{0}.csv').format(config_run.settings['type_var_D']))

    open_file_D = open(file_shapiro_wilks_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), 'W', 'P_value', 'Ho?']

    csv_file_D.writerow(header)

    for station in stations_list:

        with console.redirectStdStreams():
            W, p_value = shapiro(station.var_D.data_filtered_in_process_period)

        # Ho?
        if p_value < 0.5:
            Ho = _('rejected')
        else:
            Ho = _('accepted')

        # var D
        shapiro_line_station_var_D = [
            station.code,
            station.name,
            format_out.number(station.lat, 4),
            format_out.number(station.lon, 4),
            format_out.number(station.alt, 4),
            '{0}-{1}'.format(station.process_period['start'], station.process_period['end']),
            format_out.number(W, 4),
            format_out.number(p_value, 4),
            Ho
        ]

        csv_file_D.writerow(shapiro_line_station_var_D)


    open_file_D.close()
    del csv_file_D


def outliers(stations_list):

    data_stations = []
    codes_stations = []

    outliers_all_stations = []

    for station in stations_list:

        # -------------------------------------------------------------------------
        ## Outliers graph per station

        if config_run.settings['graphics']:

            outliers_per_stations_dir = os.path.join(outliers_dir, _("Outliers_per_station"))

            if not os.path.isdir(outliers_per_stations_dir):
                os.makedirs(outliers_per_stations_dir)

            name_graph = _("Outliers")+"_{0}_{1}_{2}_({3}-{4})".format(station.code, station.name,
            config_run.settings['type_var_D'], station.process_period['start'], station.process_period['end'])

            fig = pyplot.figure(figsize=(3,6))
            ax = fig.add_subplot(111)
            ax.set_title(unicode(_("Outliers")+"\n{0} ({1}-{2})".format(config_run.settings['type_var_D'],
                station.process_period['start'], station.process_period['end']), 'utf-8'), globals_vars.graphs_title_properties())

            ## X
            x_labels = [station.code]
            xticks([1], x_labels)
            ax.set_xlabel(unicode(_('Station'), 'utf-8'), globals_vars.graphs_axis_properties())

            ## Y
            type_var = config_run.settings['type_var_D']
            ax.set_ylabel(unicode('{0} ({1})'.format(type_var, globals_vars.units_var_D), 'utf-8'), globals_vars.graphs_axis_properties())
            #ax.set_ylabel(_('Frequency'))

            boxplot_station = boxplot(station.var_D.data_filtered_in_process_period)

            #pyplot.setp(boxplot_station['boxes'], color='black')
            #pyplot.setp(boxplot_station['whiskers'], color='black', linestyle='-')
            pyplot.setp(boxplot_station['fliers'], color='red', marker='+')
            #pyplot.setp(boxplot_station['fliers'], markersize=3.0)

            #ax.grid(True)
            ax.autoscale(tight=True)

            zoom_graph(ax=ax, x_scale_below=-2.5,x_scale_above=-2.5, y_scale_below=-0.04, y_scale_above=-0.04)

            fig.tight_layout()

            # save image
            image = os.path.join(outliers_per_stations_dir, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

            # variables for mosaic
            data_stations.append(station.var_D.data_filtered_in_process_period)
            codes_stations.append(station.code)
        else:
            boxplot_station = boxplot(station.var_D.data_filtered_in_process_period)

        # -------------------------------------------------------------------------
        ## Prepare variables for report all outliers of all stations

        outliers_station = {}

        outliers_station['station'] = station

        outliers_station['whiskers_below'] = boxplot_station['whiskers'][0].get_data()[1][1]
        outliers_station['whiskers_above'] = boxplot_station['whiskers'][1].get_data()[1][1]

        # prepare data if:
        if station.var_D.frequency_data == "monthly" and station.var_I.frequency_data == "daily":
            # TODO: move this in prepare_all_stations or use station_copy
            station = copy.deepcopy(station)
            station.var_I.daily2monthly()
            station.var_I.frequency_data = "monthly"
            station.var_I.data_and_null_in_process_period(station)

            # temporally change global STATE_OF_DATA
            globals_vars.STATE_OF_DATA = get_state_of_data(station)

        # special cases with analysis_interval equal to trimester
        if station.var_D.frequency_data == "daily" and station.var_I.frequency_data == "daily" and \
           config_run.settings['analysis_interval'] == "trimester":
                station_copy = copy.deepcopy(station)
                station_copy.var_D.daily2monthly()
                station_copy.var_D.frequency_data = "monthly"
                station_copy.var_D.data_and_null_in_process_period(station)

                station_copy.var_I.daily2monthly()
                station_copy.var_I.frequency_data = "monthly"
                station_copy.var_I.data_and_null_in_process_period(station)

                # temporally change global STATE_OF_DATA
                globals_vars.STATE_OF_DATA = get_state_of_data(station_copy)
        elif station.var_D.frequency_data == "daily" and station.var_I.frequency_data == "monthly" and\
           config_run.settings['analysis_interval'] == "trimester":
            station_copy = copy.deepcopy(station)
            station_copy.var_D.daily2monthly()
            station_copy.var_D.frequency_data = "monthly"
            station_copy.var_D.data_and_null_in_process_period(station)

            # temporally change global STATE_OF_DATA
            globals_vars.STATE_OF_DATA = get_state_of_data(station_copy)

        calculate_lags(station, makes_files=False)

        outliers_list = []

        for index, value in enumerate(station.var_D.data_in_process_period):
            # detect all outliers in the process period, save in outliers_list
            # the value, the date and the categorize the outliers inside phenomenos
            # of independent variable

            # TODO: translate
            # para categorizar los atípicos en las fases del fenómeno, Jaziku evalúa atípico por atípico haciendo lo siguiente:
            #
            # 1.primero evalua en que rango de intervalo de analisis se encuentra el atipico, ejemplo: si el atipico
            #   es de la fecha 17 del mes (M) y el  intervalo de analisis es de 5 dias, se encuentra en el rango de
            #   intervalo de analisis de 16-21 dias
            # 2.luego obtiene todos los valores de la variable independiente para todos los años del periodo a procesar
            #   dentro del intervalo de analisis encontrado (1) del mes (M) del atipico
            # 3.calcula la media de los valores del punto (2)
            # 4.calcula los umbrales de la variable independiente para todos los años del periodo a procesar para el
            #   analisis del periodo (1) del atípico
            # 5.ubica el valor medio calculado (3) dentro (por debajo, normal, por encima) de los dos umbrales calculados (4)
            # 6.categorizar el atípico segun (5)
            #
            # Tener en cuenta que:
            # * cuando la variable dependiente es mensual y la independiente diaria, la variable independiente es
            #   convertida a mensual antes de evaluar las fases del fenómeno de los atípicos
            # * si la variable dependiente es diaria y la independiente mensual, la variable dependiente se convierte
            #   a mensual si el intervalo de análisis es trimestral antes de evaluar las fases del fenómeno de los atípicos
            # * si las dos variables son diarias y el intervalo de análisis es trimestral, ambas variables son
            #   convertidas a mensuales antes de evaluar las fases del fenómeno de los atípicos

            if (value < outliers_station['whiskers_below'] or
                value > outliers_station['whiskers_above']) and \
                not globals_vars.is_valid_null(value):
                # date of outlier
                outlier_date = station.var_D.date_in_process_period[index]

                if station.var_D.frequency_data == "daily" and station.var_I.frequency_data == "daily":
                    if config_run.settings['analysis_interval'] == "trimester":
                        # get I values for outliers date
                        station.var_I_values = lags.get_lag_values(station_copy, 'var_I', 0, outlier_date.month)
                        # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                        values_var_I = get_values_in_range_analysis_interval(station_copy, 'I', outlier_date.year, outlier_date.month, None, 0)
                    else:
                        # get the corresponding start day of analysis interval
                        day = locate_day_in_analysis_interval(outlier_date.day)
                        # get I values for outliers date
                        station.var_I_values = lags.get_lag_values(station, 'var_I', 0, outlier_date.month, day)
                        # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                        values_var_I = get_values_in_range_analysis_interval(station, 'I', outlier_date.year, outlier_date.month, day, 0)
                if station.var_D.frequency_data == "daily" and station.var_I.frequency_data == "monthly":
                    if config_run.settings['analysis_interval'] == "trimester":
                        # get I values for outliers date
                        station.var_I_values = lags.get_lag_values(station_copy, 'var_I', 0, outlier_date.month)
                        # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                        values_var_I = get_values_in_range_analysis_interval(station_copy, 'I', outlier_date.year, outlier_date.month, None, 0)
                    else:
                        # get the corresponding start day of analysis interval
                        day = locate_day_in_analysis_interval(outlier_date.day)
                        # get I values for outliers date
                        station.var_I_values = lags.get_lag_values(station, 'var_I', 0, outlier_date.month, day)
                        # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                        values_var_I = get_values_in_range_analysis_interval(station, 'I', outlier_date.year, outlier_date.month, day, 0)
                if station.var_D.frequency_data == "monthly" and station.var_I.frequency_data == "monthly":
                    # get I values for outliers date
                    station.var_I_values = lags.get_lag_values(station, 'var_I', 0, outlier_date.month)
                    # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                    values_var_I = get_values_in_range_analysis_interval(station, 'I', outlier_date.year, outlier_date.month, None, 0)

                # SPECIAL CASE 1: when var_I is ONI1, ONI2 or CAR, don't calculate trimesters because the ONI and CAR
                # series was calculated by trimesters from original source
                if station.var_I.frequency_data == "monthly" and station.var_I.type_series in ['ONI1', 'ONI2', 'CAR']:
                    # take the first month (in this case, it is the mean of trimester)
                    values_var_I = values_var_I[0]

                # get the mean of all values of var I in analysis interval in the corresponding period of outlier (var_D)
                value_var_I = array.mean(values_var_I)

                # get categorize of phenomenon for the value_var_I
                category_of_phenomenon = get_category_of_phenomenon(value_var_I, station)

                # save outlier
                outliers_list.append([outlier_date, value, category_of_phenomenon])

        outliers_station['outliers'] = outliers_list

        outliers_all_stations.append(outliers_station)

    # -------------------------------------------------------------------------
    ## Outliers graph all in one

    if config_run.settings['graphics'] and ( 1 < Station.stations_processed <= 50 ):
        if config_run.settings['process_period']:
            name_graph = _("Outliers")+"_{0}_({1}-{2})".format(
                config_run.settings['type_var_D'], config_run.settings['process_period']['start'],
                config_run.settings['process_period']['end'])
        else:
            name_graph = _("Outliers")+"_{0}".format(config_run.settings['type_var_D'])

        fig = pyplot.figure(figsize=(2.5+len(stations_list)/2.5,6))
        ax = fig.add_subplot(111)
        if config_run.settings['process_period']:
            ax.set_title(unicode(_("Outliers")+" - {0} ({1}-{2})".format(config_run.settings['type_var_D'],
                config_run.settings['process_period']['start'], config_run.settings['process_period']['end']), 'utf-8'), globals_vars.graphs_title_properties())
        else:
            ax.set_title(unicode(_("Outliers")+" - {0}".format(config_run.settings['type_var_D']), 'utf-8'), globals_vars.graphs_title_properties())

        ## X
        xticks(range(len(stations_list)), codes_stations, rotation='vertical')
        ax.set_xlabel(unicode(_('Stations'), 'utf-8'), globals_vars.graphs_axis_properties())

        ## Y
        type_var = config_run.settings['type_var_D']
        ax.set_ylabel(unicode('{0} ({1})'.format(type_var, globals_vars.units_var_D), 'utf-8'), globals_vars.graphs_axis_properties())
        #ax.set_ylabel(_('Frequency'))

        boxplot_station = boxplot(data_stations)

        #pyplot.setp(boxplot_station['boxes'], color='black')
        #pyplot.setp(boxplot_station['whiskers'], color='black', linestyle='-')
        pyplot.setp(boxplot_station['fliers'], color='red', marker='+')
        #pyplot.setp(boxplot_station['fliers'], markersize=3.0)

        #ax.grid(True)
        ax.autoscale(tight=True)
        #pyplot.subplots_adjust(bottom=) #(len(array.max(codes_stations))/30.0))

        zoom_graph(ax=ax, x_scale_below=-0.2,x_scale_above=-0.2, y_scale_below=-0.04, y_scale_above=-0.04, abs_x=True)

        fig.tight_layout()

        # save image
        image = os.path.join(outliers_dir, name_graph + '.png')
        pyplot.savefig(os.path.join(outliers_dir, name_graph + '.png'), dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')


    # -------------------------------------------------------------------------
    ## Report all Outliers of all stations in file

    if config_run.settings['process_period']:
        file_outliers_var_D\
        = os.path.join(outliers_dir, _("Outliers_table")+"_{0}_({1}-{2}).csv".format(
            config_run.settings['type_var_D'], config_run.settings['process_period']['start'],
            config_run.settings['process_period']['end']))
    else:
        file_outliers_var_D\
        = os.path.join(outliers_dir, _("Outliers_table")+"_{0}.csv".format(
            config_run.settings['type_var_D']))

    open_file_D = open(file_outliers_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

    num_max_outliers = 0
    for outliers_station in outliers_all_stations:
        if len(outliers_station['outliers']) > num_max_outliers:
            num_max_outliers = len(outliers_station['outliers'])

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), _('WHISKERS BELOW'),
              _('WHISKERS ABOVE'), _('# OUTLIERS'),'']

    header_outliers = [_('DATE'), _('VALUE'), _('PHEN_CAT')]

    header = header + header_outliers*num_max_outliers

    csv_file_D.writerow(header)

    for outliers_station in outliers_all_stations:

        num_outliers = len(outliers_station['outliers'])

        outliers_station_line = [
            outliers_station['station'].code,
            outliers_station['station'].name,
            format_out.number(outliers_station['station'].lat),
            format_out.number(outliers_station['station'].lon),
            format_out.number(outliers_station['station'].alt),
            '{0}-{1}'.format(outliers_station['station'].process_period['start'], outliers_station['station'].process_period['end']),
            format_out.number(outliers_station['whiskers_below']),
            format_out.number(outliers_station['whiskers_above']),
            num_outliers,  _('OUTLIERS LIST:')
        ]

        # sort the outliers list base on outlier value
        outliers_station['outliers'] = sorted(outliers_station['outliers'], key=itemgetter(1))

        for outlier in outliers_station['outliers']:

            outliers_station_line.append('{0}-{1}-{2}'.format(outlier[0].year,outlier[0].month,outlier[0].day))
            outliers_station_line.append(format_out.number(outlier[1]))
            outliers_station_line.append(outlier[2])
            #outliers_station_line.append('|')

        csv_file_D.writerow(outliers_station_line)

    open_file_D.close()
    del csv_file_D

    # return to original global STATE_OF_DATA variable
    globals_vars.STATE_OF_DATA = None
    set_global_state_of_data(stations_list)
