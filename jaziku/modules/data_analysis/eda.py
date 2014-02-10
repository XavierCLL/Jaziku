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
from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot
from numpy import histogram
from pylab import xticks, bar, boxplot
from PIL import Image
from scipy import stats

from jaziku import env
from jaziku.core.station import Station
from jaziku.core.analysis_interval import get_values_in_range_analysis_interval, locate_day_in_analysis_interval, \
    get_range_analysis_interval, adjust_data_of_variables, get_text_of_frequency_data
from jaziku.core.stations import global_process_period
from jaziku.modules.climate import time_series
from jaziku.modules.climate.contingency_table import get_label_of_var_I_category
from jaziku.modules.climate.time_series import  calculate_time_series
from jaziku.utils import  console, output, watermarking, array


def main(stations_list):

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # EXPLORATORY DATA ANALYSIS
    # -------------------------------------------------------------------------

    console.msg(_("\n################# EXPLORATORY DATA ANALYSIS:"))

    if not env.config_run.settings['graphics']:
        console.msg(_("\n > WARNING: The 'graphics' in 'output options' is disabled,\n"
                      "   all graphics for EDA module will not be created. The graphics\n"
                      "   in EDA module represents the vast majority of the results.\n"), color='yellow')

    global eda_dir
    eda_dir = os.path.join(env.globals_vars.DATA_ANALYSIS_DIR, 'EDA')

    # -------------------------------------------------------------------------
    # DESCRIPTIVE STATISTICS
    # -------------------------------------------------------------------------

    console.msg(_("Descriptive statistics ............................... "), newline=False)

    # -------------------------------------------------------------------------
    # FILES OF DESCRIPTIVE STATISTICS

    global shapiro_wilks_dir
    shapiro_wilks_dir = os.path.join(eda_dir, _('Descriptive_Statistic'))

    output.make_dirs(shapiro_wilks_dir)

    file_descriptive_statistics_var_D\
    = os.path.join(shapiro_wilks_dir, _('Descriptive_Statistics_{0}.csv').format(env.var_D.TYPE_SERIES))

    file_descriptive_statistics_var_I\
    = os.path.join(shapiro_wilks_dir, _('Descriptive_Statistics_{0}.csv').format(env.var_I.TYPE_SERIES))

    open_file_D = open(file_descriptive_statistics_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    open_file_I = open(file_descriptive_statistics_var_I, 'w')
    csv_file_I = csv.writer(open_file_I, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), _('TOTAL DATA'), _('VALID DATA'),
              _('LOST DATA'), _('MAXIMUM'), _('MINIMUM'), _('AVERAGE'), _('MEDIAN'), _('STD DEVIATION'), _('SKEWNESS'),
              _('VARIANCE'), _('KURTOSIS'), _('COEFF VARIATION')]

    csv_file_D.writerow(header)
    csv_file_I.writerow(header)

    for station in stations_list:

        # var D
        eda_var_D = [
            station.code,
            station.name,
            output.number(station.lat),
            output.number(station.lon),
            output.number(station.alt),
            '{0}-{1}'.format(station.process_period['start'], station.process_period['end']),
            len(station.var_D.data_in_process_period),
            station.var_D.size_data,
            station.var_D.nulls_in_process_period,
            output.number(station.var_D.maximum),
            output.number(station.var_D.minimum),
            output.number(station.var_D.average),
            output.number(station.var_D.median),
            output.number(station.var_D.std_dev),
            output.number(station.var_D.skewness),
            output.number(station.var_D.variance),
            output.number(station.var_D.kurtosis),
            output.number(station.var_D.coef_variation)
        ]

        csv_file_D.writerow(eda_var_D)

        # var I
        eda_var_I = [
            station.code,
            station.name,
            output.number(station.lat),
            output.number(station.lon),
            output.number(station.alt),
            '{0}-{1}'.format(station.process_period['start'], station.process_period['end']),
            len(station.var_I.data_in_process_period),
            station.var_I.size_data,
            station.var_I.nulls_in_process_period,
            output.number(station.var_I.maximum),
            output.number(station.var_I.minimum),
            output.number(station.var_I.average),
            output.number(station.var_I.median),
            output.number(station.var_I.std_dev),
            output.number(station.var_I.skewness),
            output.number(station.var_I.variance),
            output.number(station.var_I.kurtosis),
            output.number(station.var_I.coef_variation)
        ]

        csv_file_I.writerow(eda_var_I)

    open_file_D.close()
    del csv_file_D

    open_file_I.close()
    del csv_file_I

    # -------------------------------------------------------------------------
    # GRAPHS OF DESCRIPTIVE STATISTICS

    # only make graphs if there are more of one station
    if env.config_run.settings['graphics']:
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
    # THE BEST PERIODS TO PROCESS
    #
    # TODO: disable because this need more review and this need more theoretical support

    #if not env.config_run.settings['process_period']:
    #    console.msg(_("Analysis the best periods to process ................. "), newline=False)
    #
    #    # TODO: Fixes the equation for process several stations, use threads or PyMPI
    #    if len(stations_list) < 50:
    #        analysis_the_best_periods_to_process(stations_list)
    #        console.msg(_("done"), color='green')
    #    else:
    #        console.msg("?", color='yellow')
    #        query_check_continue = query.yes_no(_("  Analysis the best periods to process for many\n"
    #                                              "  stations can take several minutes to complete,\n"
    #                                              "  'y' for do it, 'n' for continue"), default="n")
    #        if query_check_continue:
    #            console.msg(_("Analysis the best periods to process ................. "), newline=False)
    #            analysis_the_best_periods_to_process(stations_list)
    #            console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # GRAPHS INSPECTION OF SERIES

    if env.config_run.settings['graphics']:
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

    output.make_dirs(distribution_test_dir)

    # -------------------------------------------------------------------------
    # SCATTER PLOTS OF SERIES

    if env.config_run.settings['graphics']:
        console.msg(_("Scatter plots of series .............................. "), newline=False)
        with console.redirectStdStreams():
            return_msg = scatter_plots_of_series(stations_list)
        if return_msg is True:
            console.msg(_("done"), color='green')
        else:
            console.msg(return_msg, color="yellow")

    # -------------------------------------------------------------------------
    # FREQUENCY HISTOGRAM

    if env.config_run.settings['graphics']:
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

    output.make_dirs(outliers_dir)

    console.msg(_("Outliers ............................................. "), newline=False)
    #with console.redirectStdStreams():  #TODO maybe this no need activade, need when check thresholds
    outliers(stations_list)

    if Station.stations_processed > 50:
        console.msg(_("partial\n > WARNING: The maximum limit for make the box-plot of\n"
                      "   outliers of all stations are 50 stations, if you want\n"
                      "   this box-plot, please divide the stations in regions\n"
                      "   into different runfiles with maximum 50 stations per\n"
                      "   runfile, and rerun each runfile."), color="yellow")
    else:
        console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # CORRELATION
    # -------------------------------------------------------------------------

    global correlation_dir
    correlation_dir = os.path.join(eda_dir, _('Correlation'))
    output.make_dirs(correlation_dir)

    # -------------------------------------------------------------------------
    # AUTOCORRELATION

    console.msg(_("AutoCorrelation ...................................... "), newline=False)
    with console.redirectStdStreams():
        correlation(stations_list, type_correlation='auto')
    console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # CROSSCORRELATION

    console.msg(_("CrossCorrelation ..................................... "), newline=False)
    with console.redirectStdStreams():
        return_msg = correlation(stations_list, type_correlation='cross')
    if return_msg is True:
        console.msg(_("done"), color='green')
    else:
        console.msg(return_msg, color="yellow")

    # -------------------------------------------------------------------------
    # HOMOGENEITY

    global homogeneity_dir
    homogeneity_dir = os.path.join(eda_dir, _('Homogeneity'))
    output.make_dirs(homogeneity_dir)

    console.msg(_("Homogeneity .......................................... "), newline=False)
    with console.redirectStdStreams():
        return_msg = homogeneity(stations_list)
    if return_msg is True:
        console.msg(_("done"), color='green')
    else:
        console.msg(return_msg, color="yellow")

    # -------------------------------------------------------------------------
    # ANOMALY

    global anomaly_dir
    anomaly_dir = os.path.join(eda_dir, _('Anomaly'))
    output.make_dirs(anomaly_dir)

    console.msg(_("Anomaly .............................................. "), newline=False)
    anomaly(stations_list)
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
    graphs_dir = os.path.join(shapiro_wilks_dir, _('Graphs_for_{0}').format(env.var_D.TYPE_SERIES))

    output.make_dirs(graphs_dir)

    #for type, var in [[env.config_run.get['type_var_D'],'var_D'], [env.config_run.get['type_var_I'],'var_I']]:
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

            name_graph = _("{0}_({1})_{2}").format(statistic, env.var_D.TYPE_SERIES, graph)
            # dynamic with based of number of stations
            with_fig = Station.stations_processed/5+4
            fig = pyplot.figure(figsize=(with_fig, 6), dpi=100)
            ax = fig.add_subplot(111)
            #tfs = 18.5 - 10/(Station.stations_processed)

            if Station.stations_processed <= 5:
                title = _("{0} ({1})\n{2}").format(statistic.replace('_',' '), env.var_D.TYPE_SERIES, graph.replace('_',' '))
            else:
                title = name_graph.replace('_',' ')

            ax.set_title(unicode(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            if graph == _('vs_Stations'):
                if graph_options[statistics[enum]] == 'dots':
                    ax.plot(range(1, len(x)+1), y, 'o', color="#638786", markersize=8.5)
                if graph_options[statistics[enum]] == 'bars':
                    bar(range(1, len(x)+1), y, width=0.8, align='center', color="#638786")
            if graph == _('vs_Altitude'):
                ax.plot(x, y, 'o', color="#638786", markersize=8.5)

            ## X
            if graph == _('vs_Stations'):
                ax.set_xlabel(unicode(_('Stations'), 'utf-8'), env.globals_vars.graphs_axis_properties())
                xticks(range(1, len(x)+1), x, rotation='vertical')
            if graph == _('vs_Altitude'):
                ax.set_xlabel(_('Altitude (m)'), env.globals_vars.graphs_axis_properties())
                #locs, labels = xticks(range(1, len(x)+1), x)
                #setp(labels, 'rotation', 'vertical')
            ## Y
            # get units os type of var D or I
            if statistics[enum] not in ['skewness', 'kurtosis', 'coef_variation']:
                units = env.var_D.UNITS
            else:
                units = '--'
            ax.set_ylabel(unicode('{0} ({1})'.format(statistic.replace('_',' '),units), 'utf-8'), env.globals_vars.graphs_axis_properties())

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


def analysis_the_best_periods_to_process(stations_list):
    """Analysis the best periods to be process, off all stations
    inside the runfile, and are ranked and organized in based
    on number of stations, number of years and number of nulls.
    Writes a csv file of all possible periods from best to worst
    (in based of ranking) with its corresponding list of stations
    included for the analysis period.

    (Jaziku only show these ranked period for the user to select the
    best possible period and put in "process_period" in the runfile to
    be processed with it, but Jaziku no process with this period
    automatically)
    """

    start_periods = []
    end_periods = []
    for station in stations_list:
        start_periods.append(station.var_D.date[0].year)
        end_periods.append(station.var_D.date[-1].year)

    min_start_periods = min(start_periods)+1
    max_end_periods = max(end_periods)-1

    min_years_for_range_period = 8
    list_of_periods = []

    for _start_year in range(min_start_periods, max_end_periods-min_years_for_range_period+1):
        for _end_year in range(min_start_periods+min_years_for_range_period, max_end_periods+1):
            if (_end_year-_start_year) < min_years_for_range_period:
                continue
            list_of_one_period = []
            num_stations_in_before_nulls_permitted_value = 0
            for max_percentage_nulls_permitted in range(0,17,4):
                period = {}
                period["start_year"] = _start_year
                period["end_year"] = _end_year
                period["num_stations"] = 0
                period["side_valid_data"] = 0
                period["total_nulls"] = 0
                period["max_percentage_nulls_permitted"] = max_percentage_nulls_permitted
                period["stations_included"] = []

                for station in stations_list:
                    # start year for period to process (not common period)
                    station_start_year = station.var_D.date[0].year + 1
                    # end year for period to process (not common period)
                    station_end_year = station.var_D.date[-1].year - 1
                    if station_start_year > period["start_year"] or \
                       station_end_year < period["end_year"]:
                        # no included this station when the period of the data of var D
                        # not is inside of analysis period
                        continue

                    start_date_var = date(period["start_year"], 1, 1)
                    if env.var_D.is_daily():
                        end_date_var = date(period["end_year"], 12, 31)
                    else:
                        end_date_var = date(period["end_year"], 12, 1)

                    station_data = station.var_D.data[station.var_D.date.index(start_date_var):station.var_D.date.index(end_date_var) + 1]

                    # number of valid nulls for var D of the station
                    nulls_in_analysis_period, \
                    percentage_of_nulls_in_analysis_period \
                        = array.check_nulls(station_data)

                    if percentage_of_nulls_in_analysis_period > max_percentage_nulls_permitted:
                        # no included this station when the percentage of
                        # nulls values is greater of permitted.
                        continue

                    period["total_nulls"] += nulls_in_analysis_period

                    period["side_valid_data"] += len(array.clean(station_data))

                    period["num_stations"] += 1
                    period["stations_included"].append("{0}-{1}".format(station.code, station.name))

                # ranking
                # TODO: improve the ranking equation
                period["rank"] = (((period["side_valid_data"]*(period["num_stations"]**2)*(period["end_year"]-period["start_year"])))/
                                  ((period["total_nulls"]+1)/float(period["side_valid_data"]+1))**0.2)/10000.0
                if period["num_stations"] > num_stations_in_before_nulls_permitted_value:
                    list_of_one_period.append(period)
                num_stations_in_before_nulls_permitted_value = period["num_stations"]
                del period

            if len(list_of_one_period) > 0:
                list_of_periods += sorted(list_of_one_period, key=lambda x: x["rank"], reverse=True)

    periods_ranked = sorted(list_of_periods, key=lambda x: x["rank"], reverse=True)[0:len(list_of_periods)/3]
    # write into file the periods ranked with stations of each period
    file_name = os.path.join(eda_dir, _('Analysis_the_best_periods_to_process.csv'))
    open_file = open(file_name, 'w')
    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    header = [_('ANALYSIS PERIOD'), _('NUM. YEARS'), _('NUM. STATIONS INCLUDED FOR PERIOD'), _('MAX % OF NULLS PERMITTED PER STATION'),
              _('% OF NULLS INSIDE THE PERIOD OF ALL DATA'), _('RANKING*'), '--', _('LIST STATIONS INCLUDED FOR PERIOD:')]
    csv_file.writerow(header)

    for period_ranked in periods_ranked:
        csv_file.writerow(['{0}-{1}'.format(period_ranked["start_year"], period_ranked["end_year"]),
                           period_ranked["end_year"] - period_ranked["start_year"] + 1, period_ranked["num_stations"],
                           period_ranked["max_percentage_nulls_permitted"],
                           output.number(period_ranked["total_nulls"]*100/float(period_ranked["side_valid_data"])),
                           output.number(period_ranked["rank"]), '--'] + period_ranked["stations_included"])

    open_file.close()
    del csv_file, periods_ranked, list_of_periods


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

    output.make_dirs(graphs_dir)


    for station in stations_list:
        image_list = []

        station_image_path = os.path.join(graphs_dir, station.code +'-'+station.name)

        output.make_dirs(station_image_path)

        list_graphs = [[station.var_D,'D'], [station.var_I,'I']]

        # add special plot for make mosaic when the frequency off var D and var I are different
        if env.var_D.is_daily() and env.var_I.is_n_monthly():
            list_graphs.append([station.var_I, 'special_I'])
        if env.var_D.is_n_monthly() and env.var_I.is_daily():
            list_graphs.append([station.var_D, 'special_D'])

        for var, type in list_graphs:
            x = list(var.date_in_process_period)
            y = list(var.data_in_process_period)

            # number of year for process
            num_years = station.process_period['end'] - station.process_period['start']

            if type != 'special_I' and type != 'special_D':
                if type == 'D':
                    type_var = env.var_D.TYPE_SERIES
                if type == 'I':
                    type_var = env.var_I.TYPE_SERIES
                name_graph = _("Station_{0}-{1}_({2}_vs_Time)").format(station.code, station.name, type_var)
                len_x = len(x)
            else:
                if type[-1::] == 'D':
                    type_var = env.var_D.TYPE_SERIES
                if type[-1::] == 'I':
                    type_var = env.var_I.TYPE_SERIES
                name_graph = _("_Station_{0}-{1}_({2}_vs_Time)_").format(station.code, station.name, type_var)

                # add point in end of X-axis
                x.append(x[-1]+relativedelta(months=1))
                y.append(var.data[var.date.index(x[-1])])

                if type == 'special_I':
                    len_x = len(station.var_D.date_in_process_period)
                if type == 'special_D':
                    len_x = len(station.var_I.date_in_process_period)
                # dynamic with based of number of stations
            if env.var_[var.type].is_n_monthly():
                with_fig = 8 + len_x/150
            if env.var_[var.type].is_daily() or type == 'special_I' or type == 'special_D':
                #with_fig = len_x/20+4
                with_fig = 12

            fig = pyplot.figure(figsize=(with_fig, 5))
            #fig = pyplot.figure()
            ax = fig.add_subplot(111)
            ax.set_title(unicode(name_graph.replace('_',' '), 'utf-8'), env.globals_vars.graphs_title_properties())

            # default zoom values
            x_scale_below=-1.0/len_x
            x_scale_above=-2.7/len_x
            y_scale_below=-0.04
            y_scale_above=-0.04

            if env.var_[var.type].is_daily() or type == 'special_I' or type == 'special_D':
                x_scale_below=-3.0/len_x
                x_scale_above=-6.0/len_x

            if type == 'D' or type == 'special_D':
                if env.var_[var.type].is_daily() or type == 'special_D':
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
                if env.var_[var.type].is_n_monthly() and not type == 'special_D':
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
            ax.set_xlabel(_('Time'), env.globals_vars.graphs_axis_properties())
            ax.xaxis.set_major_locator(mdates.YearLocator())  # every year
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            if num_years < 20:
                ax.xaxis.set_minor_locator(mdates.MonthLocator())  # every month
            xticks(rotation='vertical')

            ## Y
            # set units type of var D or I
            if type in ['special_D', 'D']:
                units = env.var_D.UNITS
            if type in ['special_I', 'I']:
                units = env.var_I.UNITS

            ax.set_ylabel(unicode('{0} ({1})'.format(type_var, units), 'utf-8'), env.globals_vars.graphs_axis_properties())

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
        if env.var_D.is_daily() and env.var_I.is_n_monthly():
            image_var_D = Image.open(image_list[0])
            image_var_I = Image.open(image_list[2])
        elif env.var_D.is_n_monthly() and env.var_I.is_daily():
            image_var_D = Image.open(image_list[2])
            image_var_I = Image.open(image_list[1])
        else:
            image_var_D = Image.open(image_list[0])
            image_var_I = Image.open(image_list[1])

        # definition height and width of individual image
        width, height = image_var_D.size
        mosaic_dir_save = os.path.join(station_image_path, _('mosaic_station_{0}-{1}.png').format(station.code, station.name))

        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        mosaic_plots = pyplot.figure(figsize=((width) / 75, (height * 2) / 75))
        mosaic_plots.savefig(mosaic_dir_save, dpi=75)
        mosaic = Image.open(mosaic_dir_save)

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

# -------------------------------------------------------------------------


def get_climatology_data(station, freq = None):
    '''Calculate function for some variables need in climatology
    and others
    '''

    _station = copy.deepcopy(station)
    _station.var_D.convert2(freq)
    original_FREQUENCY_DATA = env.var_D.FREQUENCY_DATA

    if freq is None:
        freq = env.var_D.FREQUENCY_DATA
    env.var_D.set_FREQUENCY_DATA(freq, check=False)

    _station.var_D.calculate_data_date_and_nulls_in_period()
    var_D_data = _station.var_D.data_in_process_period
    var_D_date = _station.var_D.date_in_process_period

    env.var_D.set_FREQUENCY_DATA(original_FREQUENCY_DATA, check=False)

    y_mean = []
    y_max = [] # value to add to mean for max value
    y_min = [] # value to subtract to mean for min value

    if freq in ['monthly', 'bimonthly', 'trimonthly']:
        for month in range(1,13):
            values = []
            for iter, value in  enumerate(var_D_data):
                if var_D_date[iter].month == month:
                    values.append(value)
            values = array.clean(values)
            y_mean.append(array.mean(values))
            y_max.append(array.maximum(values) - y_mean[-1])
            y_min.append(y_mean[-1] - array.minimum(values))

        del _station
        return y_min, y_mean, y_max

    if freq not in ['monthly', 'bimonthly', 'trimonthly'] and env.var_D.is_daily():
        range_analysis_interval = get_range_analysis_interval()
        for month in range(1, 13):
            for day in range_analysis_interval:
                range_analysis_mean = []
                range_analysis_max = []
                range_analysis_min = []
                # iteration for all years inside process period
                for year in range(_station.process_period['start'], _station.process_period['end']+1):
                    # test if day exist in month and year
                    if day > monthrange(year, month)[1]:
                        continue

                    values = get_values_in_range_analysis_interval(_station.var_D, year, month, day)
                    values = array.clean(values)
                    range_analysis_mean.append(array.mean(values))
                    range_analysis_max.append(array.maximum(values))
                    range_analysis_min.append(array.minimum(values))

                y_mean.append(array.mean(range_analysis_mean))
                y_max.append(array.mean(range_analysis_max) - y_mean[-1])
                y_min.append(y_mean[-1] - array.mean(range_analysis_min))

        del _station
        return y_min, y_mean, y_max

def climatology(stations_list):
    """
    Make table and graphs of climatology, part of EDA.
    """

    graphs_dir = os.path.join(shapiro_wilks_dir, _('Graphs_Inspection_of_Series'))

    output.make_dirs(graphs_dir)

    # name climatology table of all stations
    if env.var_D.is_daily() or env.var_D.is_monthly():
        filename_climatology_table = _('Climatology_table_{0}_(monthly)').format(env.var_D.TYPE_SERIES)+'.csv'
    else:
        filename_climatology_table = _('Climatology_table_{0}_({1})').format(env.var_D.TYPE_SERIES,env.config_run.settings['analysis_interval_i18n'])+'.csv'
    # climatology table file
    open_file_climatology_table\
        = open(os.path.join(graphs_dir, filename_climatology_table), 'w')
    csv_climatology_table = csv.writer(open_file_climatology_table, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD')]
    if env.var_D.is_daily() or env.var_D.is_monthly():
        header += [output.months_in_initials(i) for i in range(12)]
    else:
        header += [output.analysis_interval_text(i) for i in range(1,13)]

    csv_climatology_table.writerow(header)

    for station in stations_list:
        # -------------------------------------------------------------------------
        ## for climatology table
        line = [station.code, station.name, output.number(station.lat), output.number(station.lon),
                output.number(station.alt), '{0}-{1}'.format(station.process_period['start'],
                                                             station.process_period['end'])]

        y_min, y_mean, y_max = get_climatology_data(station, 'monthly')

        csv_climatology_table.writerow(line + [output.number(i) for i in y_mean])

        if not env.config_run.settings['graphics']:
            continue

        # -------------------------------------------------------------------------
        # Mutliyear climatology monthly, bimonthly and trimonthly
        #
        #  - climatology monthly only for data daily and monthly
        #  - climatology bimonthly only for data or analysis interval bimonthly
        #  - climatology trimonthly only for data or analysis interval trimonthly

        climatology_n_monthly_list = []
        vars_n_monthly = {}
        if env.var_D.is_daily() or env.var_D.is_monthly():
            vars_n_monthly['freq'] = 'monthly'
            vars_n_monthly['label'] = _('monthly')
            vars_n_monthly['x_labels'] = [output.months_in_initials(i) for i in range(12)]
            vars_n_monthly['x_rotation'] = 'horizontal'
            climatology_n_monthly_list.append(vars_n_monthly)
        vars_n_monthly = {}
        if env.config_run.settings['analysis_interval'] in ['bimonthly', 'trimonthly']:
            vars_n_monthly['freq'] = env.config_run.settings['analysis_interval']
            if env.config_run.settings['analysis_interval'] in ['bimonthly']:
                vars_n_monthly['label'] = _('bimonthly')
                vars_n_monthly['x_rotation'] = 'vertical'
            if env.config_run.settings['analysis_interval'] in ['trimonthly']:
                vars_n_monthly['label'] = _('trimonthly')
                vars_n_monthly['x_rotation'] = 'horizontal'
            vars_n_monthly['x_labels'] = [output.analysis_interval_text(i) for i in range(1,13)]
            climatology_n_monthly_list.append(vars_n_monthly)

        for climatology_n_monthly in climatology_n_monthly_list:

            # first check if the variable need to be convert
            # if env.config_run.settings['analysis_interval'] in ['bimonthly', 'trimonthly']:
            y_min, y_mean, y_max = get_climatology_data(station, climatology_n_monthly['freq'])

            # -------------------------------------------------------------------------
            # for climatology graphs, N-month (base)

            station_climatology_path = os.path.join(graphs_dir, station.code +'-'+station.name, _('Climatology'))

            output.make_dirs(station_climatology_path)

            x = range(1, 13)
            x_labels = climatology_n_monthly['x_labels']

            # do that matplotlib plot zeros in extreme values
            for value in y_mean:
                if value == 0:
                    y_mean[y_mean.index(value)] = 0.0001

            title=_("Multiyear climatology ({0})\n{1} {2} - {3} ({4}-{5})").format(climatology_n_monthly['label'],
                    station.code, station.name, env.var_D.TYPE_SERIES, station.process_period['start'],
                    station.process_period['end'])

            # -------------------------------------------------------------------------
            # climatology N-monthly without whiskers

            name_graph = _("Multiyear_climatology_({0})_{1}_{2}_{3}").format(climatology_n_monthly['label'],
                            station.code, station.name, env.var_D.TYPE_SERIES)

            fig = pyplot.figure(figsize=(8, 5.5))
            ax = fig.add_subplot(111)

            ax.set_title(unicode(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            if climatology_n_monthly['freq'] == 'monthly':
                ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            else:
                ax.set_xlabel(climatology_n_monthly['label'].capitalize(), env.globals_vars.graphs_axis_properties())

            xticks(x, x_labels, rotation=climatology_n_monthly['x_rotation'])

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode('{0} ({1}) - '.format(type_var, env.var_D.UNITS) + _('[mean]'), 'utf-8'), env.globals_vars.graphs_axis_properties())

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
            # climatology N-monthly with whiskers

            name_graph = _("Multiyear_climatology_({0}+whiskers)_{1}_{2}_{3}").format(climatology_n_monthly['label'],
                station.code, station.name, env.var_D.TYPE_SERIES)

            fig = pyplot.figure(figsize=(8, 5.5))
            ax = fig.add_subplot(111)

            ax.set_title(unicode(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            if climatology_n_monthly['freq'] == 'monthly':
                ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            else:
                ax.set_xlabel(climatology_n_monthly['label'].capitalize(), env.globals_vars.graphs_axis_properties())

            xticks(x, x_labels, rotation=climatology_n_monthly['x_rotation'])

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode(('{0} ({1}) - ' + _('[min-mean-max]')).format(type_var, env.var_D.UNITS), 'utf-8'), env.globals_vars.graphs_axis_properties())

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
            # climatology N-monthly table (csv)

            name_csv_table = _("Multiyear_climatology_table_{0}_{1}_{2}_{3}.csv")\
                .format(climatology_n_monthly['label'], station.code, station.name, env.var_D.TYPE_SERIES)
            open_file = open(os.path.join(station_climatology_path,name_csv_table), 'w')
            csv_table = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

            # print header
            header = [''] + x_labels
            csv_table.writerow(header)

            # max values
            csv_table.writerow( [_('max')] + [ output.number(x + y_max[i]) for i,x in enumerate(y_mean) ] )

            # mean values
            csv_table.writerow( [_('mean')] + [ output.number(x) for x in y_mean ] )

            # min values
            csv_table.writerow( [_('min')] + [ output.number(x - y_min[i]) for i,x in enumerate(y_mean) ] )

            open_file.close()
            del csv_table

        # -------------------------------------------------------------------------
        # For climatology graphs based to analysis interval:
        # 5, 10 or 15 days climatology -> for data daily

        if env.var_D.is_daily() and env.config_run.settings['analysis_interval'] not in ['monthly', 'bimonthly', 'trimonthly']:

            y_min, y_mean, y_max = get_climatology_data(station, 'daily')

            x = range(1, len(y_mean)+1)
            x_step_label = len(y_mean)/12
            x_labels = []
            for i in range(len(y_mean)):
                if i%x_step_label == 0:
                    x_labels.append(output.months_in_initials(i/x_step_label))
                else:
                    x_labels.append('')

            title = _("Multiyear climatology (each {0} days)\n{1} {2} - {3} ({4}-{5})").format(env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, env.var_D.TYPE_SERIES, station.process_period['start'],
                station.process_period['end'])

            # -------------------------------------------------------------------------
            # climatology N days without whiskers

            name_graph = _("Multiyear_climatology_({0}days)_{1}_{2}_{3}").format(env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, env.var_D.TYPE_SERIES)

            with_fig = 5 + len(y_mean)/9
            fig = pyplot.figure(figsize=(with_fig, 5.5))
            ax = fig.add_subplot(111)
            ax.set_title(unicode(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            xticks(x, x_labels)

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode('{0} ({1}) - '.format(type_var, env.var_D.UNITS) + _('[mean]'), 'utf-8'), env.globals_vars.graphs_axis_properties())

            #pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)

            x_scale_value = -0.013 - env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL/600.0

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

            name_graph = _("Multiyear_climatology_({0}days+whiskers)_{1}_{2}_{3}").format(env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, env.var_D.TYPE_SERIES)

            with_fig = 5 + len(y_mean)/9
            fig = pyplot.figure(figsize=(with_fig, 5.5))
            ax = fig.add_subplot(111)
            ax.set_title(unicode(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            xticks(x, x_labels)

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode(('{0} ({1}) - ' + _('[min-mean-max]')).format(type_var, env.var_D.UNITS), 'utf-8'), env.globals_vars.graphs_axis_properties())

            #pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True)
            ax.autoscale(tight=True)

            x_scale_value = -0.013 - env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL/600.0

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

            name_csv_table = _("Multiyear_climatology_table_{0}days_{1}_{2}_{3}.csv").format(env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL, station.code, station.name, env.var_D.TYPE_SERIES)
            open_file = open(os.path.join(station_climatology_path,name_csv_table), 'w')
            csv_table = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

            # print header
            header = ['']
            for month in range(1, 13):
                for day in get_range_analysis_interval():
                    header.append(output.analysis_interval_text(month, day))

            csv_table.writerow(header)

            # max values
            csv_table.writerow( [_('max')] + [ output.number(x + y_max[i]) for i,x in enumerate(y_mean) ] )

            # mean values
            csv_table.writerow( [_('mean')] + [ output.number(x) for x in y_mean ] )

            # min values
            csv_table.writerow( [_('min')] + [ output.number(x - y_min[i]) for i,x in enumerate(y_mean) ] )

            open_file.close()
            del csv_table

    open_file_climatology_table.close()
    del csv_climatology_table


def scatter_plots_of_series(stations_list):

    return_msg = True

    if not (1 < Station.stations_processed <= 15):
        if Station.stations_processed == 1:
            return_msg = _("partial\n > WARNING: There is only one station for process\n"
                           "   the scatter plots of series, this need more \n"
                           "   of one station.")
        else:
            return_msg = _("partial\n > WARNING: The maximum limit for make the scatter plots\n"
                            "   of series are 10 stations, if you want this diagram,\n"
                            "   please divide the stations in regions into different\n"
                            "   runfiles with maximum 10 stations per runfile, and\n"
                            "   rerun each runfile.")
        return return_msg


    # calculate the common period of all common process
    global_period = global_process_period(stations_list)
    # if there is no a global period then exit
    if global_period is False:
        return_msg = _("impossible\n > WARNING: There is no a global period for all\n"
                       "   stations, the scatter plots of series need to be\n"
                       "   evaluated with the global period, continuing\n"
                       "   without make the scatter plots of series graph")
        return return_msg

    fig_height = 3.2*len(stations_list)/1.5
    fig_with = 4*len(stations_list)/1.5

    pyplot.figure(figsize=(fig_with,fig_height))

    name_plot = _("scatter_plots_of_series") + "_{0}_{2}-{3}".format(env.var_D.TYPE_SERIES,
        env.var_D.UNITS,
        global_period['start'], global_period['end'])

    title_plot = _("Scatter plots of series") + "\n{0} ({1}) {2}-{3}".format(env.var_D.TYPE_SERIES,
        env.var_D.UNITS,
        global_period['start'], global_period['end'])

    pyplot.suptitle(unicode(title_plot, 'utf-8'), y=(fig_height-0.1)/fig_height, fontsize=14)

    for iter_v, station_v in enumerate(stations_list):
        for iter_h, station_h in enumerate(stations_list):
            x = station_h.var_D.data[station_h.var_D.date.index(global_period['start_date']):\
            station_h.var_D.date.index(global_period['end_date'])+1]

            y = station_v.var_D.data[station_v.var_D.date.index(global_period['start_date']):\
            station_v.var_D.date.index(global_period['end_date'])+1]

            ax = pyplot.subplot2grid((len(stations_list),len(stations_list)),(iter_v,iter_h))

            ax.scatter(x,y, marker='o', color="#638786", edgecolors="#3C5250")

            if iter_h == 0:
                ax.set_ylabel(station_v.code, env.globals_vars.graphs_axis_properties())
            else:
                ax.set_yticklabels([])
            if iter_v == len(stations_list)-1:
                ax.set_xlabel(unicode(station_h.code, 'utf-8'), env.globals_vars.graphs_axis_properties())
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

    return return_msg


def get_frequency_histogram(data):

    n = len(data)

    # bins based on sturges formula
    bins = 1 + 3.3*log10(n)

    hist, bin_edges = histogram(data, bins=bins)

    return hist, bin_edges


def frequency_histogram(stations_list):

    frequency_histogram_dir = os.path.join(distribution_test_dir, _('Frequency_histogram'))

    output.make_dirs(frequency_histogram_dir)

    for station in stations_list:

        hist, bin_edges = get_frequency_histogram(station.var_D.data_filtered_in_process_period)

        name_graph = _("frequency_histogram_{0}_{1}_{2}").format(station.code, station.name, env.var_D.TYPE_SERIES)

        fig = pyplot.figure()
        ax = fig.add_subplot(111)
        ax.set_title(unicode(_("Frequency histogram\n{0} {1} - {2} ({3}-{4})").format(station.code, station.name,
            env.var_D.TYPE_SERIES, station.process_period['start'], station.process_period['end']), 'utf-8'), env.globals_vars.graphs_title_properties())


        ## X
        type_var = env.var_D.TYPE_SERIES
        ax.set_xlabel(unicode('{0} ({1})'.format(type_var, env.var_D.UNITS), 'utf-8'), env.globals_vars.graphs_axis_properties())

        ## Y
        ax.set_ylabel(_('Frequency'), env.globals_vars.graphs_axis_properties())

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
    = os.path.join(distribution_test_dir, _('shapiro_wilks_test_{0}.csv').format(env.var_D.TYPE_SERIES))

    open_file_D = open(file_shapiro_wilks_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), 'W', 'P_value', 'Ho?']

    csv_file_D.writerow(header)

    for station in stations_list:

        with console.redirectStdStreams():
            W, p_value = stats.shapiro(station.var_D.data_filtered_in_process_period)

        # Ho?
        if p_value < 0.5:
            Ho = _('rejected')
        else:
            Ho = _('accepted')

        # var D
        shapiro_line_station_var_D = [
            station.code,
            station.name,
            output.number(station.lat),
            output.number(station.lon),
            output.number(station.alt),
            '{0}-{1}'.format(station.process_period['start'], station.process_period['end']),
            output.number(W),
            output.number(p_value),
            Ho
        ]

        csv_file_D.writerow(shapiro_line_station_var_D)


    open_file_D.close()
    del csv_file_D


def outliers(stations_list):

    data_stations = []
    codes_stations = []

    outliers_all_stations = []

    # save original state of data for var D and I
    original_freq_data_var_D = env.var_D.FREQUENCY_DATA
    original_freq_data_var_I = env.var_I.FREQUENCY_DATA

    def clone_and_transform_station(station, convert_var_D_to, convert_var_I_to):
        station_copy = copy.deepcopy(station)
        if convert_var_D_to:
            station_copy.var_D.convert2(convert_var_D_to)
            env.var_D.set_FREQUENCY_DATA(convert_var_D_to, check=False)
            station_copy.var_D.calculate_data_date_and_nulls_in_period()
        if convert_var_I_to:
            station_copy.var_I.convert2(convert_var_I_to)
            env.var_I.set_FREQUENCY_DATA(convert_var_I_to, check=False)
            station_copy.var_I.calculate_data_date_and_nulls_in_period()

        return station_copy

    for station in stations_list:

        # -------------------------------------------------------------------------
        ## Outliers graph per station

        if env.config_run.settings['graphics']:

            outliers_per_stations_dir = os.path.join(outliers_dir, _("Outliers_per_station"))

            output.make_dirs(outliers_per_stations_dir)

            name_graph = _("Outliers")+"_{0}_{1}_{2}_({3}-{4})".format(station.code, station.name,
            env.var_D.TYPE_SERIES, station.process_period['start'], station.process_period['end'])

            fig = pyplot.figure(figsize=(3,6))
            ax = fig.add_subplot(111)
            ax.set_title(unicode(_("Outliers")+"\n{0} ({1}-{2})".format(env.var_D.TYPE_SERIES,
                station.process_period['start'], station.process_period['end']), 'utf-8'), env.globals_vars.graphs_title_properties())

            ## X
            x_labels = [station.code]
            xticks([1], x_labels)
            ax.set_xlabel(unicode(_('Station'), 'utf-8'), env.globals_vars.graphs_axis_properties())

            ## Y
            type_var = env.var_D.TYPE_SERIES
            ax.set_ylabel(unicode('{0} ({1})'.format(type_var, env.var_D.UNITS), 'utf-8'), env.globals_vars.graphs_axis_properties())
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

        ## prepare station for special case
        if env.config_run.settings['analysis_interval'] in ['monthly', 'bimonthly', 'trimonthly']:
            station_copy = clone_and_transform_station(station,
                                                       convert_var_D_to=env.config_run.settings['analysis_interval'],
                                                       convert_var_I_to=env.config_run.settings['analysis_interval'])
        else:
            station_copy = clone_and_transform_station(station, convert_var_D_to=False, convert_var_I_to=False)

        calculate_time_series(station_copy, lags=[0], makes_files=False)

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
            # 3.calcula la media o acumulado de los valores del punto (2)
            # 4.calcula los umbrales de la variable independiente para todos los años del periodo a procesar para el
            #   analisis del periodo (1) del atípico
            # 5.ubica el valor medio calculado (3) dentro (por debajo, normal, por encima) de los dos umbrales calculados (4)
            # 6.categorizar el atípico segun (5)
            #
            # Tener en cuenta que:
            # * las dos variables son convertidas al intervalo de analisis excepto cuando el intervalo de
            #   analisis es diario

            # check if the value is an outliers
            if (value < outliers_station['whiskers_below'] or
                value > outliers_station['whiskers_above']) and \
                not env.globals_vars.is_valid_null(value):
                
                # date of outlier
                outlier_date = station.var_D.date_in_process_period[index]

                ## categorize the outlier based on category of var I

                if env.config_run.settings['analysis_interval'] in ['monthly', 'bimonthly', 'trimonthly']:
                    # get I values for outliers date
                    station.var_I.specific_values = time_series.get_specific_values(station_copy, 'var_I', 0, outlier_date.month)
                    # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                    values_var_I = get_values_in_range_analysis_interval(station_copy.var_I, outlier_date.year, outlier_date.month, None, 0)
                else:
                    # get the corresponding start day of analysis interval
                    day = locate_day_in_analysis_interval(outlier_date.day)
                    # get I values for outliers date
                    station.var_I.specific_values = time_series.get_specific_values(station_copy, 'var_I', 0, outlier_date.month, day)
                    # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                    values_var_I = get_values_in_range_analysis_interval(station_copy.var_I, outlier_date.year, outlier_date.month, day, 0)
                # get the mean or sum (based on mode_calculation_series_I) of all values of var I
                # in analysis interval in the corresponding period of outlier (var_D)
                value_var_I = time_series.calculate_specific_values_of_time_series(station.var_I, values_var_I)

                # get categorize of phenomenon for the value_var_I
                category_of_phenomenon = get_label_of_var_I_category(value_var_I, station)

                # save outlier
                outliers_list.append([outlier_date, value, category_of_phenomenon])

        outliers_station['outliers'] = outliers_list

        outliers_all_stations.append(outliers_station)

        del station_copy

    # -------------------------------------------------------------------------
    ## Outliers graph all in one

    if env.config_run.settings['graphics'] and ( 1 < Station.stations_processed <= 50 ):
        if env.config_run.settings['process_period']:
            name_graph = _("Outliers")+"_{0}_({1}-{2})".format(
                env.var_D.TYPE_SERIES, env.config_run.settings['process_period']['start'],
                env.config_run.settings['process_period']['end'])
        else:
            name_graph = _("Outliers")+"_{0}".format(env.var_D.TYPE_SERIES)

        fig = pyplot.figure(figsize=(2.5+len(stations_list)/2.5,6))
        ax = fig.add_subplot(111)

        if len(stations_list) <= 3:
            _part_title = _("Outliers")+'\n'
        else:
            _part_title = _("Outliers")+' - '

        if env.config_run.settings['process_period']:
            ax.set_title(unicode(_part_title + "{0} ({1}-{2})".format(env.var_D.TYPE_SERIES,
                env.config_run.settings['process_period']['start'], env.config_run.settings['process_period']['end']), 'utf-8'), env.globals_vars.graphs_title_properties())
        else:
            ax.set_title(unicode(_part_title + "{0}".format(env.var_D.TYPE_SERIES), 'utf-8'), env.globals_vars.graphs_title_properties())

        ## X
        xticks(range(len(stations_list)), codes_stations, rotation='vertical')
        ax.set_xlabel(unicode(_('Stations'), 'utf-8'), env.globals_vars.graphs_axis_properties())

        ## Y
        type_var = env.var_D.TYPE_SERIES
        ax.set_ylabel(unicode('{0} ({1})'.format(type_var, env.var_D.UNITS), 'utf-8'), env.globals_vars.graphs_axis_properties())
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

    if env.config_run.settings['process_period']:
        file_outliers_var_D\
        = os.path.join(outliers_dir, _("Outliers_table")+"_{0}_({1}-{2}).csv".format(
            env.var_D.TYPE_SERIES, env.config_run.settings['process_period']['start'],
            env.config_run.settings['process_period']['end']))
    else:
        file_outliers_var_D\
        = os.path.join(outliers_dir, _("Outliers_table")+"_{0}.csv".format(
            env.var_D.TYPE_SERIES))

    open_file_D = open(file_outliers_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    num_max_outliers = 0
    for outliers_station in outliers_all_stations:
        if len(outliers_station['outliers']) > num_max_outliers:
            num_max_outliers = len(outliers_station['outliers'])

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), _('WHISKERS BELOW'),
              _('WHISKERS ABOVE'), _('NUM. OUTLIERS'),'']

    header_outliers = [_('DATE'), _('VALUE'), _('PHEN_CAT*')]

    header = header + header_outliers*num_max_outliers

    csv_file_D.writerow(header)

    for outliers_station in outliers_all_stations:

        num_outliers = len(outliers_station['outliers'])

        outliers_station_line = [
            outliers_station['station'].code,
            outliers_station['station'].name,
            output.number(outliers_station['station'].lat),
            output.number(outliers_station['station'].lon),
            output.number(outliers_station['station'].alt),
            '{0}-{1}'.format(outliers_station['station'].process_period['start'], outliers_station['station'].process_period['end']),
            output.number(outliers_station['whiskers_below']),
            output.number(outliers_station['whiskers_above']),
            num_outliers,  _('OUTLIERS LIST:')
        ]

        # sort the outliers list base on outlier value
        outliers_station['outliers'] = sorted(outliers_station['outliers'], key=lambda x: x[1])

        for outlier in outliers_station['outliers']:

            outliers_station_line.append('{0}-{1}-{2}'.format(outlier[0].year,
                                                              output.fix_zeros(outlier[0].month),
                                                              output.fix_zeros(outlier[0].day)))
            outliers_station_line.append(output.number(outlier[1]))
            outliers_station_line.append(outlier[2])
            #outliers_station_line.append('|')

        csv_file_D.writerow(outliers_station_line)

    # print footnote
    csv_file_D.writerow([])
    csv_file_D.writerow([_("*Calculated based on data {0}").format(env.config_run.get_analysis_interval())])

    open_file_D.close()
    del csv_file_D

    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)


def correlation(stations_list, type_correlation):
    """Make graphs ant tables of auto-correlation of var D and cross correlations
    between var D and var I
    """
    return_msg = True

    # save original state of data for var D and I
    original_freq_data_var_D = env.var_D.FREQUENCY_DATA
    original_freq_data_var_I = env.var_I.FREQUENCY_DATA

    # Adjust the same frequency data for the two time series
    stations_list_copy = copy.deepcopy(stations_list)
    if type_correlation == 'auto':
        adjust_data_of_variables(stations_list_copy, force_same_frequencies=False, messages=False)
    if type_correlation == 'cross':
        adjust_data_of_variables(stations_list_copy, force_same_frequencies=True, messages=False)

    stations_list_correlation = stations_list_copy

    for station in stations_list_correlation:

        station_path = os.path.join(correlation_dir, station.code +'-'+station.name)

        # recalculate data if is needed
        if env.var_D.was_converted:
            station.var_D.calculate_data_date_and_nulls_in_period()
        if env.var_I.was_converted:
            station.var_I.calculate_data_date_and_nulls_in_period()

        output.make_dirs(station_path)

        correlation_values = {'lags':[], 'pearson':[]}

        if type_correlation == 'auto':

            data_X = list(station.var_D.data_filtered_in_process_period)
            data_Y = list(station.var_D.data_filtered_in_process_period)

            # calculate pearson for 0 to 24 lags
            for lag in range(25):

                pearson = stats.pearsonr(data_X, data_Y)[0]

                correlation_values['lags'].append(lag)
                correlation_values['pearson'].append(pearson)

                # move the overlap between the same time series:
                # move up the data_Y lost the fist item (one month or one day)
                # so the data_X move down lost the last item (one month or one day)
                #
                # lag 1:
                #
                #   X  Y
                #  |x|
                #  |o||o|
                #  |o||o|
                #     |x|
                del data_X[0]
                del data_Y[-1]

            name_of_files = _("Auto_Correlation_{0}_{1}_{2}").format(station.code, station.name, env.var_D.TYPE_SERIES)

        if type_correlation == 'cross':
            # TODO: check if move overlaps between the series is correctly

            data_Y = list(station.var_I.data_in_process_period)
            data_X = list(station.var_D.data_in_process_period)

            # clear NaN values in par, if one of two series have a NaN value
            # delete this NaN and corresponding value in the other series in
            # the same location
            idx_to_clean = []
            for idx in range(len(data_X)):
                if env.globals_vars.is_valid_null(data_X[idx]) or env.globals_vars.is_valid_null(data_Y[idx]):
                    idx_to_clean.append(idx)
            idx_to_clean.reverse()
            for idx in idx_to_clean:
                del data_X[idx]
                del data_Y[idx]

            # -------------------------------------------------------------------------
            # calculate pearson for -1 to -24 lags
            _data_X = list(data_X)
            _data_Y = list(data_Y)

            for lag in range(1, 25):
                # move the overlap between the 2 series:
                # move up the data_Y lost the fist item (one month or one day)
                # so the data_X move down lost the last item (one month or one day)
                #
                # lag 1:
                #
                #   X  Y
                #  |x|
                #  |o||o|
                #  |o||o|
                #     |x|
                del _data_X[0]
                del _data_Y[-1]

                pearson = stats.pearsonr(_data_X, _data_Y)[0]

                correlation_values['lags'].append(-lag)
                correlation_values['pearson'].append(pearson)


            # fix order: -24 to -1
            correlation_values['lags'].reverse()
            correlation_values['pearson'].reverse()

            # -------------------------------------------------------------------------
            # calculate pearson for 0 to 24 lags
            _data_X = list(data_X)
            _data_Y = list(data_Y)
            for lag in range(25):

                pearson = stats.pearsonr(_data_X, _data_Y)[0]

                correlation_values['lags'].append(lag)
                correlation_values['pearson'].append(pearson)

                # move the overlap between the 2 series:
                # move up the data_Y lost the fist item (one month or one day)
                # so the data_X move down lost the last item (one month or one day)
                #
                # lag 1:
                #
                #   X  Y
                #     |x|
                #  |o||o|
                #  |o||o|
                #  |x|
                del _data_X[-1]
                del _data_Y[0]

            name_of_files = _("Cross_Correlation_{0}_{1}_{2}").format(station.code, station.name, env.var_D.TYPE_SERIES)

        # -------------------------------------------------------------------------
        # graphics result

        if env.config_run.settings['graphics']:

            if type_correlation == 'auto':
                fig = pyplot.figure(figsize=(6.5, 4.8))
                title = _("Auto Correlation - {0} {1}\n"
                          "{2} ({3}-{4})").format(station.code, station.name, env.var_D.TYPE_SERIES,
                                                  station.process_period['start'], station.process_period['end'])
            if type_correlation == 'cross':
                fig = pyplot.figure(figsize=(8.5, 4.8))
                title = _("Cross Correlation - {0} {1}\n"
                          "{2} vs {3} ({4}-{5})").format(station.code, station.name, env.var_D.TYPE_SERIES,
                                                         env.var_I.TYPE_SERIES, station.process_period['start'],
                                                         station.process_period['end'])

            ax = fig.add_subplot(111)

            ax.set_title(unicode(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            ## X
            ax.set_xlabel(unicode(_('Lags'), 'utf-8'), env.globals_vars.graphs_axis_properties())
            #xticks(correlation_values['lags'], x_labels)

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode(_("Correlation"), 'utf-8'), env.globals_vars.graphs_axis_properties())

            pyplot.axhline(linewidth=1, color='k')

            ax.autoscale(tight=True)

            #bar(correlation_values['lags'], correlation_values['pearson'], align='center', width=0.2, color='k')
            ax.plot(correlation_values['lags'], correlation_values['pearson'], 'ro', color='#638786', mec='#638786', linewidth=2.5, markersize=8)
            ax.vlines(correlation_values['lags'], [0], correlation_values['pearson'], linewidth=2.5, color='#638786')

            pyplot.ylim(-1, 1)

            ax.text(24, -1, get_text_of_frequency_data('D'), horizontalalignment='right', verticalalignment='center')

            zoom_graph(ax=ax, x_scale_below=-0.05,x_scale_above=-0.05, y_scale_below=-0.06, y_scale_above=-0.06)
            fig.tight_layout()

            # save image
            image = os.path.join(station_path, name_of_files + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

        # -------------------------------------------------------------------------
        # table result

        table_file = os.path.join(station_path, name_of_files + ".csv")

        open_file = open(table_file, 'w')
        csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

        # print header
        header = [_("LAGS"), _("CORRELATION")]

        csv_file.writerow(header)
        for _lag, _pearson in zip(correlation_values['lags'], correlation_values['pearson']):
            csv_file.writerow([_lag, output.number(_pearson)])

        open_file.close()
        del csv_file

    # -------------------------------------------------------------------------
    # cross-correlation matrix table

    if type_correlation == 'cross' and len(stations_list) > 1:

        global_period = global_process_period(stations_list)

        # if there is global period
        if global_period is not False:

            for station in stations_list_correlation:
                station.var_D.calculate_data_date_and_nulls_in_period(global_period['start'], global_period['end'])
                station.var_I.calculate_data_date_and_nulls_in_period(global_period['start'], global_period['end'])

            cross_correlation_matrix = []
            stations_code_and_name = []

            for station_My in stations_list_correlation:
                cross_correlation_matrix_line = []
                for station_Mx in stations_list_correlation:

                    data_My = list(station_My.var_D.data_in_period)
                    data_Mx = list(station_Mx.var_D.data_in_period)

                    # clear NaN values in par, if one of two series have a NaN value
                    # delete this NaN and corresponding value in the other series in
                    # the same location
                    idx_to_clean = []
                    for idx in range(len(data_My)):
                        if env.globals_vars.is_valid_null(data_My[idx]) or env.globals_vars.is_valid_null(data_Mx[idx]):
                            idx_to_clean.append(idx)
                    idx_to_clean.reverse()
                    for idx in idx_to_clean:
                        del data_My[idx]
                        del data_Mx[idx]
                    cross_correlation_matrix_line.append(stats.pearsonr(data_My, data_Mx)[0])
                cross_correlation_matrix.append(cross_correlation_matrix_line)
                stations_code_and_name.append('{0}-{1}'.format(station_My.code, station_My.name))

            table_file = os.path.join(correlation_dir, _("Cross_Correlation_Matrix_Table_({0}-{1}).csv")
                .format(global_period['start'], global_period['end']))
            open_file = open(table_file, 'w')
            csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

            # print header
            header = [_("PEARSON")] + stations_code_and_name
            csv_file.writerow(header)

            for station_idx, station_code in enumerate(stations_code_and_name):
                csv_file.writerow([station_code] + [output.number(p) for p in cross_correlation_matrix[station_idx]])

            # print footnote
            csv_file.writerow([])
            csv_file.writerow([get_text_of_frequency_data('D')])
            csv_file.writerow([_("*Data in global period {0}-{1}").format(global_period['start'], global_period['end'])])

            open_file.close()
            del csv_file

        else:
            return_msg = _("partial\n > WARNING: There is no a global period for all\n"
                            "   stations, the cross-correlation matrix table need\n"
                            "   this, continuing without make this matrix table")

    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)

    return return_msg


def homogeneity(stations_list):

    return_msg = True

    stations_list_copy = copy.deepcopy(stations_list)
    global_period = global_process_period(stations_list)

    # if there is no a global period then exit
    if global_period is False:
        return_msg = _("impossible\n > WARNING: There is no a global period for all\n"
                       "   stations, the tests of homogeneity need to be\n"
                       "   evaluated with the global period, continuing\n"
                       "   without make homogeneity tests")
        return return_msg

    for station in stations_list_copy:
        station.var_D.calculate_data_date_and_nulls_in_period(global_period['start'], global_period['end'])
        station.var_I.calculate_data_date_and_nulls_in_period(global_period['start'], global_period['end'])

    # -------------------------------------------------------------------------
    # Mann-Whitney-Wilcoxon Test (MWW)

    csv_name = os.path.join(homogeneity_dir, 'MWW_test.csv')
    open_file = open(csv_name, 'w')
    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
    # print header
    csv_file.writerow([_('NAME'), _('CODE'), _('U'), _('P-VALUE'), _('?')])

    for station in stations_list_copy:
        series = station.var_D.data_in_period
        series = array.clean(series)

        len_s = len(series)

        s1 = series[0:len_s/2]
        s2 = series[len_s/2::]

        # prevent identical values
        if s1 != s2:
            u, prob = stats.mannwhitneyu(s1,s2, use_continuity=False)

        p_value = prob*2.0

        if p_value > 0.05:
            is_homogeneous = _('yes')
        else:
            is_homogeneous = _('no')

        csv_file.writerow([station.name, station.code, output.number(u), output.number(p_value), is_homogeneous])

    # print footnote
    csv_file.writerow([])
    csv_file.writerow([_("*Calculated with {0} data").format(env.var_D.get_FREQUENCY_DATA())])
    csv_file.writerow([_("*Data in global period {0}-{1}").format(global_period['start'], global_period['end'])])

    open_file.close()
    del csv_file

    # -------------------------------------------------------------------------
    # T Test

    csv_name = os.path.join(homogeneity_dir, 'T_test.csv')
    open_file = open(csv_name, 'w')
    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
    # print header
    csv_file.writerow([_('NAME'), _('CODE'), _('T'), _('P-VALUE'), _('?')])

    for station in stations_list_copy:
        series = station.var_D.data_in_period
        series = array.clean(series)

        len_s = len(series)

        s1 = series[0:len_s/2]
        s2 = series[len_s/2::]

        t, p_value = stats.ttest_ind(s1,s2)

        if p_value > 0.05:
            is_homogeneous = _('yes')
        else:
            is_homogeneous = _('no')

        csv_file.writerow([station.name, station.code, output.number(t), output.number(p_value), is_homogeneous])

    # print footnote
    csv_file.writerow([])
    csv_file.writerow([_("*Calculated with {0} data").format(env.var_D.get_FREQUENCY_DATA())])
    csv_file.writerow([_("*Data in global period {0}-{1}").format(global_period['start'], global_period['end'])])

    open_file.close()
    del csv_file

    # -------------------------------------------------------------------------
    #  Levene Test

    csv_name = os.path.join(homogeneity_dir, 'Levene_test.csv')
    open_file = open(csv_name, 'w')
    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
    # print header
    csv_file.writerow([_('NAME'), _('CODE'), _('W'), _('P-VALUE'), _('?')])

    for station in stations_list_copy:
        series = station.var_D.data_in_period
        series = array.clean(series)

        len_s = len(series)

        s1 = series[0:len_s/2]
        s2 = series[len_s/2::]

        w, p_value = stats.levene(s1,s2)

        if p_value > 0.05:
            is_homogeneous = _('yes')
        else:
            is_homogeneous = _('no')
        csv_file.writerow([station.name, station.code, output.number(w), output.number(p_value), is_homogeneous])

    # print footnote
    csv_file.writerow([])
    csv_file.writerow([_("*Calculated with {0} data").format(env.var_D.get_FREQUENCY_DATA())])
    csv_file.writerow([_("*Data in global period {0}-{1}").format(global_period['start'], global_period['end'])])

    open_file.close()
    del csv_file

    # -------------------------------------------------------------------------
    # Mass Curve

    if env.var_D.TYPE_SERIES == 'PPT' and env.config_run.settings['graphics']:

        output.make_dirs(os.path.join(homogeneity_dir, _('Mass_Curve')))

        for station in stations_list_copy:
            series = station.var_D.data_in_period
            accumulate = []
            for value in series:
                if len(accumulate) == 0:
                    if env.globals_vars.is_valid_null(value):
                        value = 0
                    accumulate.append(value)
                else:
                    if env.globals_vars.is_valid_null(value):
                        value = 0
                    accumulate.append(accumulate[-1] + value)

            fig = pyplot.figure(figsize=(7, 5))
            ax = fig.add_subplot(111)

            titulo = _("{0} for {1}-{2}\nperiod {3}-{4}")\
                .format(_('Mass Curve'), station.code, station.name, global_period['start'], global_period['end'])
            ax.set_title(unicode(titulo, 'utf-8'), env.globals_vars.graphs_title_properties())

            ## X
            ax.set_xlabel(unicode(_("Time"), 'utf-8'), env.globals_vars.graphs_axis_properties())
            #xticks(correlation_values['lags'], x_labels)

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(unicode(_('{0} accumulated ({1})').format(env.var_D.TYPE_SERIES, env.var_D.UNITS), 'utf-8'), env.globals_vars.graphs_axis_properties())

            pyplot.axhline(linewidth=1, color='k')

            ax.autoscale(tight=True)

            pyplot.xlim(global_period['start_date'], global_period['end_date'])
            ax.grid(True, color='gray')

            #bar(correlation_values['lags'], correlation_values['pearson'], align='center', width=0.2, color='k')
            ax.plot(global_period['dates'], accumulate, color='#638786', mec='#638786', linewidth=5)

            fig.tight_layout()

            # save image
            image = os.path.join(homogeneity_dir, _('Mass_Curve'), _('Mass_Curve')+'_{0}-{1}.png'.format(station.code, station.name))
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

    return return_msg


def anomaly(stations_list):

    anomaly_time_series_dir = os.path.join(anomaly_dir, _('Anomaly_time_series'))
    output.make_dirs(anomaly_time_series_dir)

    if env.config_run.settings['graphics']:
        anomaly_frequency_histogram_dir = os.path.join(anomaly_dir, _('Anomaly_frequency_histogram'))
        output.make_dirs(anomaly_frequency_histogram_dir)

    # save original state of data for var D and I
    original_freq_data_var_D = env.var_D.FREQUENCY_DATA
    original_freq_data_var_I = env.var_I.FREQUENCY_DATA

    # Adjust the same frequency data for the two time series
    stations_list_adjusted = copy.deepcopy(stations_list)
    adjust_data_of_variables(stations_list_adjusted, messages=False)

    for station in stations_list_adjusted:
        station_copy = copy.deepcopy(station)
        calculate_time_series(station_copy, lags=[0], makes_files=False)

        # get the climatology values
        clim_min, clim_mean, clim_max = get_climatology_data(station)
        # get the time series values ordered
        time_series_ordered = sorted(station_copy.time_series['lag_0'], key=lambda x: x[0])
        time_series_var_D_values = [x[1] for x in time_series_ordered]

        # extend the climatology values to N years of time series
        climatology_var_D = clim_mean*(station.process_period['end']-station.process_period['start']+1)

        anomaly_values = [x1 - x2 for (x1, x2) in zip(time_series_var_D_values, climatology_var_D)]
        anomaly_values_cleaned = array.clean(anomaly_values)

        hist, bin_edges = get_frequency_histogram(anomaly_values_cleaned)

        ### Anomaly_time_series
        file_anomaly_time_series \
            = os.path.join(anomaly_time_series_dir, _('Anomaly_time_series_{0}_{1}_{2}.csv').format(env.var_D.TYPE_SERIES, station.code, station.name))
        open_file_anomaly_time_series = open(file_anomaly_time_series, 'w')
        csv_file_anomaly_time_series = csv.writer(open_file_anomaly_time_series, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

        # print header
        header = [_('DATE'), _('ANOMALIES')+' - {0} ({1})*'.format(station.var_D.type_series, env.var_D.UNITS)]
        csv_file_anomaly_time_series.writerow(header)

        for date_anomaly, anomaly in zip([x[0] for x in time_series_ordered], anomaly_values):
            if env.var_D.is_n_monthly():
                date_formated = str(date_anomaly.year)+' '+str(output.analysis_interval_text(date_anomaly.month))
            if env.var_D.is_daily():
                date_formated = str(date_anomaly.year)+' '+str(output.analysis_interval_text(date_anomaly.month, date_anomaly.day))
            csv_file_anomaly_time_series.writerow([date_formated, output.number(anomaly)])

        # print footnote
        csv_file_anomaly_time_series.writerow([])
        csv_file_anomaly_time_series.writerow([get_text_of_frequency_data('D', ndays=True)])

        open_file_anomaly_time_series.close()
        del csv_file_anomaly_time_series

        if env.config_run.settings['graphics']:

            name_graph = _("Anomaly_frequency_histogram_{0}_{1}_{2}").format(station.code, station.name, env.var_D.TYPE_SERIES)

            fig = pyplot.figure()
            ax = fig.add_subplot(111)
            ax.set_title(unicode(_("Anomaly frequency histogram\n{0} {1} - {2} ({3}-{4})").format(station.code, station.name,
                env.var_D.TYPE_SERIES, station.process_period['start'], station.process_period['end']), 'utf-8'), env.globals_vars.graphs_title_properties())

            ## X
            type_var = env.var_D.TYPE_SERIES
            ax.set_xlabel(unicode('{0} ({1}) {2}'
                .format(type_var, env.var_D.UNITS,
                        get_text_of_frequency_data('D', ndays=True)), 'utf-8'), env.globals_vars.graphs_axis_properties())

            ## Y
            ax.set_ylabel(_('Frequency'), env.globals_vars.graphs_axis_properties())

            width = 0.7 * (bin_edges[1] - bin_edges[0])
            center = (bin_edges[:-1] + bin_edges[1:]) / 2
            bar(center,hist,align='center', color='#638786', width=width)

            ax.grid(True)
            ax.axvline(x=0,color='#4A4A4A',ls='dashed')
            ax.autoscale(tight=True)
            #ax.text(0.99, 0.985, get_text_of_frequency_data('D', ndays=True), horizontalalignment='right',
            #        verticalalignment='top', transform = ax.transAxes, rotation="vertical")

            zoom_graph(ax=ax, x_scale_below=-0.04,x_scale_above=-0.04, y_scale_above=-0.04)

            fig.tight_layout()

            # save image
            image = os.path.join(anomaly_frequency_histogram_dir, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)
