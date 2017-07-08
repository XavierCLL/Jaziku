#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 IDEAM
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
from matplotlib import pyplot, gridspec
from numpy import histogram, meshgrid, unique, append
from numpy.ma import log2, floor
from numpy import array as np_array
from pylab import xticks, bar, boxplot
from scipy import signal
from PIL import Image
from scipy import stats

from jaziku import env
from jaziku.core.station import Station
from jaziku.core.analysis_interval import get_values_in_range_analysis_interval, locate_day_in_analysis_interval, \
    get_range_analysis_interval, adjust_data_of_variables, get_text_of_frequency_data
from jaziku.modules.climate import time_series
from jaziku.modules.climate.contingency_table import get_label_of_var_I_category
from jaziku.modules.climate.time_series import calculate_time_series
from jaziku.utils import console, output, watermarking, array
from jaziku.modules.data_analysis.wavelets import WaveletAnalysis


def main(stations_list):
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # EXPLORATORY DATA ANALYSIS
    # -------------------------------------------------------------------------

    console.msg(_("\n################# EXPLORATORY DATA ANALYSIS:"))

    if not env.config_run.settings['graphics']:
        console.msg(_("\n > WARNING: The 'graphics' in 'output options' is disabled,\n"
                      "   all graphics for EDA process will not be created. The graphics\n"
                      "   in EDA represents the vast majority of the results.\n"), color='yellow')

    global eda_dir
    eda_dir = os.path.join(env.globals_vars.DATA_ANALYSIS_DIR, _('Exploratory_Data_Analysis'))

    # -------------------------------------------------------------------------
    # DESCRIPTIVE STATISTICS
    # -------------------------------------------------------------------------

    console.msg(_("Descriptive statistics ............................... "), newline=False)

    # -------------------------------------------------------------------------
    # FILES OF DESCRIPTIVE STATISTICS

    global shapiro_wilks_dir
    shapiro_wilks_dir = os.path.join(eda_dir, _('Descriptive_Statistic'))

    output.make_dirs(shapiro_wilks_dir)

    file_descriptive_statistics_var_D \
        = os.path.join(shapiro_wilks_dir, _('Descriptive_Statistics_{0}.csv').format(env.var_D.TYPE_SERIES))

    file_descriptive_statistics_var_I \
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
            '{0}-{1}'.format(env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']),
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
            '{0}-{1}'.format(env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']),
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

    # if not env.config_run.settings['process_period']:
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
    # with console.redirectStdStreams():  #TODO maybe this no need activade, need when check thresholds
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
    # ANOMALY

    global anomaly_dir
    anomaly_dir = os.path.join(eda_dir, _('Anomaly'))
    output.make_dirs(anomaly_dir)

    console.msg(_("Anomaly .............................................. "), newline=False)
    anomaly(stations_list)
    console.msg(_("done"), color='green')


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # SPECTRAL ANALYSIS
    # -------------------------------------------------------------------------

    global spectral_analysis_dir
    spectral_analysis_dir = os.path.join(env.globals_vars.DATA_ANALYSIS_DIR, _('Spectral_Analysis'))
    output.make_dirs(spectral_analysis_dir)

    # -------------------------------------------------------------------------
    # PERIODOGRAM

    global periodogram_dir
    periodogram_dir = os.path.join(spectral_analysis_dir, _('Periodogram'))
    output.make_dirs(periodogram_dir)

    console.msg(_("Periodogram .......................................... "), newline=False)
    with console.redirectStdStreams():
        periodogram(stations_list)
    console.msg(_("done"), color='green')

    # -------------------------------------------------------------------------
    # WAVELETS

    global wavelets_dir
    wavelets_dir = os.path.join(spectral_analysis_dir, _('Wavelets'))
    output.make_dirs(wavelets_dir)

    console.msg(_("Wavelets ............................................. "), newline=False)
    with console.redirectStdStreams():
        wavelets(stations_list)
    console.msg(_("done"), color='green')


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # HOMOGENEITY
    # -------------------------------------------------------------------------

    global homogeneity_dir
    homogeneity_dir = os.path.join(env.globals_vars.DATA_ANALYSIS_DIR, _('Homogeneity'))
    output.make_dirs(homogeneity_dir)

    console.msg(_("Homogeneity .......................................... "), newline=False)
    with console.redirectStdStreams():
        return_msg = homogeneity(stations_list)
    if return_msg is True:
        console.msg(_("done"), color='green')
    else:
        console.msg(return_msg, color="yellow")


stations_list_adjusted = None
stations_list_adjusted_filling = None


def convert_stations(stations_list, filling=False, force_same_frequencies=False, messages=False):
    # save original state of data for var D and I
    original_freq_data_var_D = env.var_D.FREQUENCY_DATA
    original_freq_data_var_I = env.var_I.FREQUENCY_DATA

    global stations_list_adjusted
    global stations_list_adjusted_filling

    if not filling and stations_list_adjusted is not None:
        return stations_list_adjusted
    if filling and stations_list_adjusted_filling is not None:
        return stations_list_adjusted_filling

    if filling:
        stations_list_adjusted_filling = copy.deepcopy(stations_list)
        ## make periodogram for var D (all stations)
        # Filling the variables for all stations before convert
        for station in stations_list_adjusted_filling:
            station.var_D.rollback_to_origin()
            station.var_D.filling()
        # return to original FREQUENCY_DATA of the two variables
        env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
        # Adjust the same frequency data for the two time series
        adjust_data_of_variables(stations_list_adjusted_filling, force_same_frequencies=force_same_frequencies,
                                 messages=messages)
        return stations_list_adjusted_filling
    if not filling:
        stations_list_adjusted = copy.deepcopy(stations_list)
        # Adjust the same frequency data for the two time series
        adjust_data_of_variables(stations_list_adjusted, force_same_frequencies=force_same_frequencies,
                                 messages=messages)
        return stations_list_adjusted


def zoom_graph(ax, x_scale_below=0, x_scale_above=0, y_scale_below=0, y_scale_above=0, abs_x=False, abs_y=False):
    """
    zoom in/out graph where ax is figure subplot and scale is the value for
    zoom in(+) out(-), if scale = 0 no zoom, scale = 1 double zoom in factor,
    scale = 2 triple zoom in factor, scale = -1 double zoom out factor
    """
    # get the current x and y limits
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
    cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5

    # set new limits
    if abs_x:
        ax.set_xlim([cur_xlim[0] + x_scale_below,
                     cur_xlim[1] - x_scale_above])
    else:
        ax.set_xlim([cur_xlim[0] + cur_xrange * x_scale_below,
                     cur_xlim[1] - cur_xrange * x_scale_above])
    if abs_y:
        ax.set_ylim([cur_ylim[0] + y_scale_below,
                     cur_ylim[1] - y_scale_above])
    else:
        ax.set_ylim([cur_ylim[0] + cur_yrange * y_scale_below,
                     cur_ylim[1] - cur_yrange * y_scale_above])


def descriptive_statistic_graphs(stations_list):
    """
    Graphs statistics vs stations and statistics vs altitude for var D
    """
    statistics = ['size_data', 'maximum', 'minimum', 'average', 'median', 'std_dev', 'skewness', 'kurtosis',
                  'coef_variation']
    statistics_to_graphs = [_('Sizes_data'), _('Maximums'), _('Minimums'), _('Averages'), _('Medians'),
                            _('Std_deviations'), _('skewness'), _('Kurtosis'), _('Coeff_variations')]
    graph_options = {'size_data': 'bars', 'maximum': 'bars', 'minimum': 'bars', 'average': 'bars', 'median': 'bars',
                     'std_dev': 'dots', 'skewness': 'dots', 'kurtosis': 'dots', 'coef_variation': 'dots'}

    # directory for save graphs of descriptive statistic
    graphs_dir = os.path.join(shapiro_wilks_dir, _('Graphs_for_{0}').format(env.var_D.TYPE_SERIES))

    output.make_dirs(graphs_dir)

    # for type, var in [[env.config_run.get['type_var_D'],'var_D'], [env.config_run.get['type_var_I'],'var_I']]:
    for graph in [_('vs_Stations'), _('vs_Altitude')]:

        for enum, statistic in enumerate(statistics_to_graphs):
            x = []
            y = []
            for station in stations_list:
                get_statistic = {'size_data': station.var_D.size_data, 'maximum': station.var_D.maximum,
                                 'minimum': station.var_D.minimum, 'average': station.var_D.average,
                                 'median': station.var_D.median, 'std_dev': station.var_D.std_dev,
                                 'skewness': station.var_D.skewness, 'kurtosis': station.var_D.kurtosis,
                                 'coef_variation': station.var_D.coef_variation}
                if graph == _('vs_Stations'):
                    x.append(station.code)
                if graph == _('vs_Altitude'):
                    x.append(float(station.alt))
                y.append(get_statistic[statistics[enum]])

            name_graph = _("{0}_({1})_{2}").format(statistic, env.var_D.TYPE_SERIES, graph)
            # dynamic with based of number of stations
            with_fig = Station.stations_processed / 5 + 4
            if with_fig < 5:
                with_fig = 4.4
            fig = pyplot.figure(figsize=(with_fig, 6.5), dpi=100)
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
            # tfs = 18.5 - 10/(Station.stations_processed)

            if Station.stations_processed <= 20:
                title = _("{0} ({1})\n{2}").format(statistic.replace('_', ' '), env.var_D.TYPE_SERIES,
                                                   graph.replace('_', ' '))
            else:
                title = name_graph.replace('_', ' ')

            title += ' ({0}-{1})'.format(env.globals_vars.PROCESS_PERIOD['start'],
                                         env.globals_vars.PROCESS_PERIOD['end'])

            ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            if graph == _('vs_Stations'):
                if graph_options[statistics[enum]] == 'dots':
                    ax.plot(list(range(1, len(x) + 1)), y, 'o', **env.globals_vars.figure_plot_properties(ms=8))
                if graph_options[statistics[enum]] == 'bars':
                    bar(list(range(1, len(x) + 1)), y, width=0.8, **env.globals_vars.figure_bar_properties())
            if graph == _('vs_Altitude'):
                ax.plot(x, y, 'o', **env.globals_vars.figure_plot_properties(ms=8))

            ## X
            if graph == _('vs_Stations'):
                ax.set_xlabel(str(_('Stations'), 'utf-8'), env.globals_vars.graphs_axis_properties())
                xticks(list(range(1, len(x) + 1)), x, rotation='vertical')
            if graph == _('vs_Altitude'):
                ax.set_xlabel(_('Altitude (m)'), env.globals_vars.graphs_axis_properties())
                pyplot.xticks(rotation='vertical')
                # avoid the auto exponential ticks format
                ax.get_xaxis().get_major_formatter().set_useOffset(False)

            ## Y
            # get units os type of var D or I
            if statistics[enum] not in ['skewness', 'kurtosis', 'coef_variation']:
                units = env.var_D.UNITS
            else:
                units = '--'
            ax.set_ylabel(str('{0} ({1})'.format(statistic.replace('_', ' '), units), 'utf-8'),
                          env.globals_vars.graphs_axis_properties())

            pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)
            if graph == _('vs_Stations'):
                if graph_options[statistics[enum]] == 'dots':
                    zoom_graph(ax=ax, x_scale_below=-0.3, x_scale_above=-0.3, y_scale_below=-0.1, y_scale_above=-0.1,
                               abs_x=True)
                if graph_options[statistics[enum]] == 'bars':
                    zoom_graph(ax=ax, x_scale_below=-0.3, x_scale_above=-0.3, y_scale_above=-0.1, abs_x=True)
            if graph == _('vs_Altitude'):
                zoom_graph(ax=ax, x_scale_below=-0.07, x_scale_above=-0.07, y_scale_below=-0.08, y_scale_above=-0.08)

            if graph == _('vs_Stations') and graph_options[statistics[enum]] == 'bars' and \
                    all(v == 0 for v in y):
                ax.text(0.5, 0.5, str(_("All values are zeros"), 'utf-8'),
                        fontsize=14, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

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

    min_start_periods = min(start_periods) + 1
    max_end_periods = max(end_periods) - 1

    min_years_for_range_period = 8
    list_of_periods = []

    for _start_year in range(min_start_periods, max_end_periods - min_years_for_range_period + 1):
        for _end_year in range(min_start_periods + min_years_for_range_period, max_end_periods + 1):
            if (_end_year - _start_year) < min_years_for_range_period:
                continue
            list_of_one_period = []
            num_stations_in_before_nulls_permitted_value = 0
            for max_percentage_nulls_permitted in range(0, 17, 4):
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

                    station_data = station.var_D.data[
                                   station.var_D.date.index(start_date_var):station.var_D.date.index(end_date_var) + 1]

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
                period["rank"] = (((period["side_valid_data"] * (period["num_stations"] ** 2) * (
                period["end_year"] - period["start_year"]))) /
                                  ((period["total_nulls"] + 1) / float(period["side_valid_data"] + 1)) ** 0.2) / 10000.0
                if period["num_stations"] > num_stations_in_before_nulls_permitted_value:
                    list_of_one_period.append(period)
                num_stations_in_before_nulls_permitted_value = period["num_stations"]
                del period

            if len(list_of_one_period) > 0:
                list_of_periods += sorted(list_of_one_period, key=lambda x: x["rank"], reverse=True)

    periods_ranked = sorted(list_of_periods, key=lambda x: x["rank"], reverse=True)[0:len(list_of_periods) / 3]
    # write into file the periods ranked with stations of each period
    file_name = os.path.join(eda_dir, _('Analysis_the_best_periods_to_process.csv'))
    open_file = open(file_name, 'w')
    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    header = [_('ANALYSIS PERIOD'), _('NUM. YEARS'), _('NUM. STATIONS INCLUDED FOR PERIOD'),
              _('MAX % OF NULLS PERMITTED PER STATION'),
              _('% OF NULLS INSIDE THE PERIOD OF ALL DATA'), _('RANKING*'), '--',
              _('LIST STATIONS INCLUDED FOR PERIOD:')]
    csv_file.writerow(header)

    for period_ranked in periods_ranked:
        csv_file.writerow(['{0}-{1}'.format(period_ranked["start_year"], period_ranked["end_year"]),
                           period_ranked["end_year"] - period_ranked["start_year"] + 1, period_ranked["num_stations"],
                           period_ranked["max_percentage_nulls_permitted"],
                           output.number(period_ranked["total_nulls"] * 100 / float(period_ranked["side_valid_data"])),
                           output.number(period_ranked["rank"]), '--'] + period_ranked["stations_included"])

    open_file.close()
    del csv_file, periods_ranked, list_of_periods


# types graphs based on type of var D
types_var_D = {'PPT': {'graph': 'bar', 'color': '#0078B8'}, 'NDPPT': {'graph': 'bar', 'color': '#0078B8'},
               'TMIN': {'graph': 'o-', 'color': '#C08A1C'}, 'TMAX': {'graph': 'o-', 'color': '#C08A1C'},
               'TEMP': {'graph': 'o-', 'color': '#C08A1C'}, 'PATM': {'graph': '*-', 'color': '#287F2A'},
               'RH': {'graph': 's-', 'color': '#833680'}, 'RUNOFF': {'graph': 's-', 'color': '#833680'}}


def graphs_inspection_of_series(stations_list):
    """
    Graphs for inspection of series, part of Exploratory_Data_Analysis.
    """

    # directory for save graphs of descriptive statistic

    graphs_dir = os.path.join(shapiro_wilks_dir, _('Graphs_Inspection_of_Series'))

    output.make_dirs(graphs_dir)

    for station in stations_list:
        image_list = []

        station_image_path = os.path.join(graphs_dir, station.code + '-' + station.name)

        output.make_dirs(station_image_path)

        list_graphs = [[station.var_D, 'D'], [station.var_I, 'I']]

        # add special plot for make mosaic when the frequency off var D and var I are different
        if env.var_D.is_n_daily() and env.var_I.is_n_monthly():
            list_graphs.append([station.var_I, 'special_I'])
        if env.var_D.is_n_monthly() and env.var_I.is_n_daily():
            list_graphs.append([station.var_D, 'special_D'])

        for var, type in list_graphs:
            x = list(var.date_in_process_period)
            y = list(var.data_in_process_period)

            # number of year for process
            num_years = env.globals_vars.PROCESS_PERIOD['end'] - env.globals_vars.PROCESS_PERIOD['start']

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
                x.append(x[-1] + relativedelta(months=1))
                y.append(var.data[var.date.index(x[-1])])

                if type == 'special_I':
                    len_x = len(station.var_D.date_in_process_period)
                if type == 'special_D':
                    len_x = len(station.var_I.date_in_process_period)
                    # dynamic with based of number of stations
            if env.var_[var.type].is_n_monthly():
                with_fig = 8 + len_x / 150.0
            if env.var_[var.type].is_n_daily() or type == 'special_I' or type == 'special_D':
                # with_fig = len_x/20+4
                with_fig = 12

            fig = pyplot.figure(figsize=(with_fig, 5))
            # fig = pyplot.figure()
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
            ax.set_title(str(name_graph.replace('_', ' '), 'utf-8'), env.globals_vars.graphs_title_properties())

            # default zoom values
            x_scale_below = -1.0 / len_x
            x_scale_above = -2.7 / len_x
            y_scale_below = -0.04
            y_scale_above = -0.04

            if env.var_[var.type].is_n_daily() or type == 'special_I' or type == 'special_D':
                x_scale_below = -3.0 / len_x
                x_scale_above = -6.0 / len_x

            if type == 'D' or type == 'special_D':
                if env.var_[var.type].is_n_daily() or type == 'special_D':
                    if type_var not in types_var_D:
                        # default for generic type for var D
                        ax.plot(x, y, '-', linewidth=2, **env.globals_vars.figure_plot_properties())
                    else:
                        if types_var_D[type_var]['graph'] == 'bar':
                            bar(x, y, width=2 + num_years / 5.0,
                                **env.globals_vars.figure_bar_properties(color=types_var_D[type_var]['color'],
                                                                         eg_color=types_var_D[type_var]['color']))
                            y_scale_below = 0
                        else:
                            # ax.plot(x, y, TYPES_VAR_D[type_var]['graph'], color=TYPES_VAR_D[type_var]['color'])
                            ax.plot(x, y, '-', linewidth=2,
                                    **env.globals_vars.figure_plot_properties(color=types_var_D[type_var]['color']))
                if env.var_[var.type].is_n_monthly() and not type == 'special_D':
                    if type_var not in types_var_D:
                        # default for generic type for var D
                        ax.plot(x, y, '-', linewidth=2, **env.globals_vars.figure_plot_properties())
                    else:
                        if types_var_D[type_var]['graph'] == 'bar':
                            bar(x, y, width=22 + num_years / 5.0,
                                **env.globals_vars.figure_bar_properties(color=types_var_D[type_var]['color'],
                                                                         eg_color=types_var_D[type_var]['color']))
                            y_scale_below = 0
                        else:
                            ax.plot(x, y, '-', linewidth=2,
                                    **env.globals_vars.figure_plot_properties(color=types_var_D[type_var]['color']))

            if type == 'I' or type == 'special_I':
                ax.plot(x, y, '-', linewidth=2, **env.globals_vars.figure_plot_properties())

            # check if all values (y-axis) are nulls inside the period to process,
            # then render text message in the graph
            if len([item for item in y if not env.globals_vars.is_valid_null(item)]) == 0:
                pyplot.cla()
                ax.text(0.5, 0.5, str(_("All values are nulls"), 'utf-8'),
                        fontsize=14, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
                image_path = os.path.join(station_image_path, name_graph + '.png')
                # save image
                pyplot.savefig(image_path, dpi=75)
                image_list.append(image_path)
                pyplot.close('all')
                continue

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

            ax.set_ylabel(str('{0} ({1})'.format(type_var, units), 'utf-8'),
                          env.globals_vars.graphs_axis_properties())

            pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)
            zoom_graph(ax=ax, x_scale_below=x_scale_below, x_scale_above=x_scale_above,
                       y_scale_below=y_scale_below, y_scale_above=y_scale_above)

            fig.tight_layout()

            image_path = os.path.join(station_image_path, name_graph + '.png')

            # save image
            pyplot.savefig(image_path, dpi=75)

            image_list.append(image_path)

            pyplot.close('all')

        ## create mosaic
        if env.var_D.is_n_daily() and env.var_I.is_n_monthly():
            image_var_D = Image.open(image_list[0])
            image_var_I = Image.open(image_list[2])
        elif env.var_D.is_n_monthly() and env.var_I.is_n_daily():
            image_var_D = Image.open(image_list[2])
            image_var_I = Image.open(image_list[1])
        else:
            image_var_D = Image.open(image_list[0])
            image_var_I = Image.open(image_list[1])

        # definition height and width of individual image
        width, height = image_var_D.size
        mosaic_dir_save = os.path.join(station_image_path,
                                       _('mosaic_station_{0}-{1}.png').format(station.code, station.name))

        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        mosaic_plots = pyplot.figure(figsize=((width) / 75.0, (height * 2) / 75.0))
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

        # from guppy import hpy; h=hpy()
        # print h.heap()
        # h.iso(1,[],{})


# -------------------------------------------------------------------------


def get_climatology_data(station, freq=None):
    '''Calculate function for some variables need in climatology
    and others results
    '''

    _station = copy.deepcopy(station)
    original_FREQUENCY_DATA = env.var_D.FREQUENCY_DATA

    if freq is None:
        freq = env.var_D.FREQUENCY_DATA

    _station.var_D.convert2(freq)
    if _station.var_D.was_converted:
        env.var_D.set_FREQUENCY_DATA(freq, check=False)

    _station.var_D.calculate_data_date_and_nulls_in_period()
    var_D_data = _station.var_D.data_in_process_period
    var_D_date = _station.var_D.date_in_process_period

    env.var_D.set_FREQUENCY_DATA(original_FREQUENCY_DATA, check=False)

    y_mean = []
    y_max = []  # value to add to mean for max value
    y_min = []  # value to subtract to mean for min value

    if freq in ['monthly', 'bimonthly', 'trimonthly']:
        for month in range(1, 13):
            interannual_values = []
            for iter, value in enumerate(var_D_data):
                if var_D_date[iter].month == month:
                    interannual_values.append(value)
            interannual_values = array.clean(interannual_values)
            y_mean.append(array.mean(interannual_values))
            y_max.append(array.maximum(interannual_values) - y_mean[-1])
            y_min.append(y_mean[-1] - array.minimum(interannual_values))

        del _station
        return y_min, y_mean, y_max

    if freq in ['5days', '10days', '15days']:
        range_analysis_interval = get_range_analysis_interval()
        for month in range(1, 13):
            for day in range_analysis_interval:
                interannual_values = []
                for year in range(env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end'] + 1):
                    value_in_this_year = var_D_data[var_D_date.index(date(year, month, day))]
                    interannual_values.append(value_in_this_year)
                interannual_values = array.clean(interannual_values)
                y_mean.append(array.mean(interannual_values))
                y_max.append(array.maximum(interannual_values) - y_mean[-1])
                y_min.append(y_mean[-1] - array.minimum(interannual_values))

        del _station
        return y_min, y_mean, y_max


def climatology(stations_list):
    """Make table and graphs of climatology, part of Exploratory_Data_Analysis.
    """

    climatology_dir = os.path.join(eda_dir, _('Climatology'))
    output.make_dirs(climatology_dir)

    # name climatology table of all stations
    if env.var_D.is_n_daily() or env.var_D.is_monthly():
        filename_climatology_table = _('Climatology_table_{0}_(monthly)').format(env.var_D.TYPE_SERIES) + '.csv'
    else:
        filename_climatology_table = _('Climatology_table_{0}_({1})').format(env.var_D.TYPE_SERIES,
                                                                             env.config_run.get_ANALYSIS_INTERVAL_i18n()) + '.csv'
    # climatology table file
    open_file_climatology_table \
        = open(os.path.join(climatology_dir, filename_climatology_table), 'w')
    csv_climatology_table = csv.writer(open_file_climatology_table, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD')]
    if env.var_D.is_n_daily() or env.var_D.is_monthly():
        header += [output.months_in_initials(i) for i in range(12)]
    else:
        header += [output.analysis_interval_text(i) for i in range(1, 13)]

    csv_climatology_table.writerow(header)

    for station in stations_list:
        # -------------------------------------------------------------------------
        ## for climatology table
        line = [station.code, station.name, output.number(station.lat), output.number(station.lon),
                output.number(station.alt), '{0}-{1}'.format(env.globals_vars.PROCESS_PERIOD['start'],
                                                             env.globals_vars.PROCESS_PERIOD['end'])]

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
            vars_n_monthly['x_labels'] = [output.analysis_interval_text(i) for i in range(1, 13)]
            climatology_n_monthly_list.append(vars_n_monthly)

        for climatology_n_monthly in climatology_n_monthly_list:

            # first check if the variable need to be convert
            # if env.config_run.settings['analysis_interval'] in ['bimonthly', 'trimonthly']:
            y_min, y_mean, y_max = get_climatology_data(station, climatology_n_monthly['freq'])

            # -------------------------------------------------------------------------
            # for climatology graphs, N-month (base)

            station_climatology_path = os.path.join(climatology_dir, station.code + '-' + station.name)
            output.make_dirs(station_climatology_path)

            x = list(range(1, 13))
            x_labels = climatology_n_monthly['x_labels']

            # do that matplotlib plot zeros in extreme values
            for value in y_mean:
                if value == 0:
                    y_mean[y_mean.index(value)] = 0.0001

            title = _("Multiyear climatology ({0})\n{1} {2} - {3} ({4}-{5})").format(climatology_n_monthly['label'],
                                                                                     station.code, station.name,
                                                                                     env.var_D.TYPE_SERIES,
                                                                                     env.globals_vars.PROCESS_PERIOD[
                                                                                         'start'],
                                                                                     env.globals_vars.PROCESS_PERIOD[
                                                                                         'end'])

            # -------------------------------------------------------------------------
            # climatology N-monthly without whiskers

            name_graph = _("Multiyear_climatology_({0})_{1}_{2}_{3}").format(climatology_n_monthly['label'],
                                                                             station.code, station.name,
                                                                             env.var_D.TYPE_SERIES)

            fig = pyplot.figure(figsize=(8, 5.5))
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())

            ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            if climatology_n_monthly['freq'] == 'monthly':
                ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            else:
                ax.set_xlabel(climatology_n_monthly['label'].capitalize(), env.globals_vars.graphs_axis_properties())

            xticks(x, x_labels, rotation=climatology_n_monthly['x_rotation'])

            ## Y
            # get units os type of var D or I
            if env.config_run.settings['mode_calculation_series_D'] == 'mean':
                ax.set_ylabel(str('{0} ({1}) - '.format(type_var, env.var_D.UNITS) + _('[mean]'), 'utf-8'),
                              env.globals_vars.graphs_axis_properties())
            if env.config_run.settings['mode_calculation_series_D'] == 'accumulate':
                ax.set_ylabel(str('{0} ({1}) - '.format(type_var, env.var_D.UNITS) + _('[accumulate]'), 'utf-8'),
                              env.globals_vars.graphs_axis_properties())

            # pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)

            if type_var not in types_var_D:
                # default for generic type for var D
                # ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=env.globals_vars.colors['plt_default'], mec=env.globals_vars.colors['plt_default'], mew=3, linewidth=2.5, elinewidth=1)
                ax.plot(x, y_mean, '-o', linewidth=2.5, **env.globals_vars.figure_plot_properties())
                zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_below=-0.04, y_scale_above=-0.04)
            else:
                if types_var_D[type_var]['graph'] == 'bar':
                    bar(x, y_mean, **env.globals_vars.figure_bar_properties(color=types_var_D[type_var]['color']))
                    # ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_above=-0.04)
                else:
                    # ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=TYPES_VAR_D[type_var]['color'],
                    #    mec=TYPES_VAR_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                    ax.plot(x, y_mean, '-o', linewidth=2.5,
                            **env.globals_vars.figure_plot_properties(color=types_var_D[type_var]['color'],
                                                                      mec=types_var_D[type_var]['color']))
                    zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_below=-0.04,
                               y_scale_above=-0.04)

            # labels on both sides
            # ax.tick_params(labeltop=False, labelright=True)

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
                                                                                      station.code, station.name,
                                                                                      env.var_D.TYPE_SERIES)

            fig = pyplot.figure(figsize=(8, 5.5))
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())

            ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            if climatology_n_monthly['freq'] == 'monthly':
                ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            else:
                ax.set_xlabel(climatology_n_monthly['label'].capitalize(), env.globals_vars.graphs_axis_properties())

            xticks(x, x_labels, rotation=climatology_n_monthly['x_rotation'])

            ## Y
            # get units os type of var D or I
            if env.config_run.settings['mode_calculation_series_D'] == 'mean':
                ax.set_ylabel(
                    str(('{0} ({1}) - ' + _('[min-mean-max]')).format(type_var, env.var_D.UNITS), 'utf-8'),
                    env.globals_vars.graphs_axis_properties())
            if env.config_run.settings['mode_calculation_series_D'] == 'accumulate':
                ax.set_ylabel(
                    str(('{0} ({1}) - ' + _('[min-accum-max]')).format(type_var, env.var_D.UNITS), 'utf-8'),
                    env.globals_vars.graphs_axis_properties())

            # pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)

            if type_var not in types_var_D:
                # default for generic type for var D
                ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', mec=env.globals_vars.colors['plt_default'], mew=3,
                            linewidth=2.5, elinewidth=1, **env.globals_vars.figure_bar_properties(align=None))
                # bar(x, y_mean, align='center', color=env.globals_vars.colors['plt_default'])
                zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_below=-0.04, y_scale_above=-0.04)
            else:
                if types_var_D[type_var]['graph'] == 'bar':
                    bar(x, y_mean, **env.globals_vars.figure_bar_properties(color=types_var_D[type_var]['color']))
                    ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_above=-0.04)
                else:
                    ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=types_var_D[type_var]['color'],
                                mec=types_var_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                    # ax.plot(x, y_mean, TYPES_VAR_D[type_var]['graph'], color=TYPES_VAR_D[type_var]['color'])
                    zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_below=-0.04,
                               y_scale_above=-0.04)

            # labels on both sides
            # ax.tick_params(labeltop=False, labelright=True)

            fig.tight_layout()
            # save image
            image = os.path.join(station_climatology_path, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

            # -------------------------------------------------------------------------
            # climatology N-monthly table (csv)

            name_csv_table = _("Multiyear_climatology_table_{0}_{1}_{2}_{3}.csv") \
                .format(climatology_n_monthly['label'], station.code, station.name, env.var_D.TYPE_SERIES)
            open_file = open(os.path.join(station_climatology_path, name_csv_table), 'w')
            csv_table = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

            # print header
            header = [''] + x_labels
            csv_table.writerow(header)

            # max values
            csv_table.writerow([_('max')] + [output.number(x + y_max[i]) for i, x in enumerate(y_mean)])

            # mean values
            if env.config_run.settings['mode_calculation_series_D'] == 'mean':
                csv_table.writerow([_('mean')] + [output.number(x) for x in y_mean])
            if env.config_run.settings['mode_calculation_series_D'] == 'accumulate':
                csv_table.writerow([_('accum')] + [output.number(x) for x in y_mean])

            # min values
            csv_table.writerow([_('min')] + [output.number(x - y_min[i]) for i, x in enumerate(y_mean)])

            open_file.close()
            del csv_table

        # -------------------------------------------------------------------------
        # For climatology graphs based to analysis interval:
        # 5, 10 or 15 days climatology -> for data daily

        if env.var_D.is_n_daily() and env.config_run.settings['analysis_interval'] not in ['monthly', 'bimonthly',
                                                                                           'trimonthly']:

            y_min, y_mean, y_max = get_climatology_data(station, env.config_run.settings['analysis_interval'])

            x = list(range(1, len(y_mean) + 1))
            x_step_label = len(y_mean) / 12.0
            x_labels = []
            for i in range(len(y_mean)):
                if i % x_step_label == 0:
                    x_labels.append(output.months_in_initials(i / x_step_label))
                else:
                    x_labels.append('')

            title = _("Multiyear climatology (each {0} days)\n{1} {2} - {3} ({4}-{5})").format(
                env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, env.var_D.TYPE_SERIES, env.globals_vars.PROCESS_PERIOD['start'],
                env.globals_vars.PROCESS_PERIOD['end'])

            # -------------------------------------------------------------------------
            # climatology N days without whiskers

            name_graph = _("Multiyear_climatology_({0}days)_{1}_{2}_{3}").format(
                env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, env.var_D.TYPE_SERIES)

            with_fig = 5 + len(y_mean) / 9.0
            fig = pyplot.figure(figsize=(with_fig, 5.5))
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
            ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            xticks(x, x_labels)

            ## Y
            # get units os type of var D or I
            if env.config_run.settings['mode_calculation_series_D'] == 'mean':
                ax.set_ylabel(str('{0} ({1}) - '.format(type_var, env.var_D.UNITS) + _('[mean]'), 'utf-8'),
                              env.globals_vars.graphs_axis_properties())
            if env.config_run.settings['mode_calculation_series_D'] == 'accumulate':
                ax.set_ylabel(str('{0} ({1}) - '.format(type_var, env.var_D.UNITS) + _('[accumulate]'), 'utf-8'),
                              env.globals_vars.graphs_axis_properties())

            # pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)

            x_scale_value = -0.013 - env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL / 600.0

            if type_var not in types_var_D:
                # default for generic type for var D
                # ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=env.globals_vars.colors['plt_default'], mec=env.globals_vars.colors['plt_default'], mew=3, linewidth=2.5, elinewidth=1)
                ax.plot(x, y_mean, '-o', linewidth=2.5, **env.globals_vars.figure_plot_properties())
                zoom_graph(ax=ax, x_scale_below=x_scale_value, x_scale_above=x_scale_value, y_scale_below=-0.04,
                           y_scale_above=-0.04)
            else:
                if types_var_D[type_var]['graph'] == 'bar':
                    bar(x, y_mean, **env.globals_vars.figure_bar_properties(color=types_var_D[type_var]['color']))
                    # ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value, x_scale_above=x_scale_value, y_scale_above=-0.04)
                else:
                    ax.plot(x, y_mean, '-o', linewidth=2.5,
                            **env.globals_vars.figure_plot_properties(color=types_var_D[type_var]['color'],
                                                                      mec=types_var_D[type_var]['color']))
                    # ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=TYPES_VAR_D[type_var]['color'],
                    #    mec=TYPES_VAR_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value, x_scale_above=x_scale_value, y_scale_below=-0.04,
                               y_scale_above=-0.04)

            # labels on both sides
            # ax.tick_params(labeltop=False, labelright=True)

            fig.tight_layout()

            # save image
            image = os.path.join(station_climatology_path, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

            # -------------------------------------------------------------------------
            # climatology N days with whiskers

            name_graph = _("Multiyear_climatology_({0}days+whiskers)_{1}_{2}_{3}").format(
                env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL,
                station.code, station.name, env.var_D.TYPE_SERIES)

            with_fig = 5 + len(y_mean) / 9.0
            fig = pyplot.figure(figsize=(with_fig, 5.5))
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
            ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            type_var = env.var_D.TYPE_SERIES

            ## X
            ax.set_xlabel(_('Months'), env.globals_vars.graphs_axis_properties())
            xticks(x, x_labels)

            ## Y
            # get units os type of var D or I
            if env.config_run.settings['mode_calculation_series_D'] == 'mean':
                ax.set_ylabel(
                    str(('{0} ({1}) - ' + _('[min-mean-max]')).format(type_var, env.var_D.UNITS), 'utf-8'),
                    env.globals_vars.graphs_axis_properties())
            if env.config_run.settings['mode_calculation_series_D'] == 'accumulate':
                ax.set_ylabel(
                    str(('{0} ({1}) - ' + _('[min-accum-max]')).format(type_var, env.var_D.UNITS), 'utf-8'),
                    env.globals_vars.graphs_axis_properties())

            # pyplot.subplots_adjust(bottom=0.2)
            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)

            x_scale_value = -0.013 - env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL / 600.0

            if type_var not in types_var_D:
                # default for generic type for var D
                ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=env.globals_vars.colors['plt_default'],
                            mec=env.globals_vars.colors['plt_default'], mew=3, linewidth=2.5, elinewidth=1,
                            **env.globals_vars.figure_bar_properties(align=None))
                zoom_graph(ax=ax, x_scale_below=x_scale_value, x_scale_above=x_scale_value, y_scale_below=-0.04,
                           y_scale_above=-0.04)
                # bar(x, y_mean, align='center', color=env.globals_vars.colors['plt_default'])
            else:
                if types_var_D[type_var]['graph'] == 'bar':
                    bar(x, y_mean, **env.globals_vars.figure_bar_properties(color=types_var_D[type_var]['color']))
                    ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt=None, ecolor='#2F4C6F', mew=3, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value, x_scale_above=x_scale_value, y_scale_above=-0.04)
                else:
                    # ax.plot(x, y_mean, TYPES_VAR_D[type_var]['graph'], color=TYPES_VAR_D[type_var]['color'])
                    ax.errorbar(x, y_mean, yerr=[y_min, y_max], fmt='o-', color=types_var_D[type_var]['color'],
                                mec=types_var_D[type_var]['color'], mew=3, linewidth=2.5, elinewidth=1)
                    zoom_graph(ax=ax, x_scale_below=x_scale_value, x_scale_above=x_scale_value, y_scale_below=-0.04,
                               y_scale_above=-0.04)

            # labels on both sides
            # ax.tick_params(labeltop=False, labelright=True)

            fig.tight_layout()

            # save image
            image = os.path.join(station_climatology_path, name_graph + '.png')
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

            # -------------------------------------------------------------------------
            # climatology N days table (csv)

            name_csv_table = _("Multiyear_climatology_table_{0}days_{1}_{2}_{3}.csv").format(
                env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL, station.code, station.name, env.var_D.TYPE_SERIES)
            open_file = open(os.path.join(station_climatology_path, name_csv_table), 'w')
            csv_table = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

            # print header
            header = ['']
            for month in range(1, 13):
                for day in get_range_analysis_interval():
                    header.append(output.analysis_interval_text(month, day))

            csv_table.writerow(header)

            # max values
            csv_table.writerow([_('max')] + [output.number(x + y_max[i]) for i, x in enumerate(y_mean)])

            # mean values
            if env.config_run.settings['mode_calculation_series_D'] == 'mean':
                csv_table.writerow([_('mean')] + [output.number(x) for x in y_mean])
            if env.config_run.settings['mode_calculation_series_D'] == 'accumulate':
                csv_table.writerow([_('accum')] + [output.number(x) for x in y_mean])

            # min values
            csv_table.writerow([_('min')] + [output.number(x - y_min[i]) for i, x in enumerate(y_mean)])

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

    fig_height = 3.2 * len(stations_list) / 1.5
    fig_with = 4 * len(stations_list) / 1.5

    pyplot.figure(figsize=(fig_with, fig_height))

    name_plot = _("scatter_plots_of_series") + "_{0}_{2}-{3}".format(env.var_D.TYPE_SERIES,
                                                                     env.var_D.UNITS,
                                                                     env.globals_vars.PROCESS_PERIOD['start'],
                                                                     env.globals_vars.PROCESS_PERIOD['end'])

    title_plot = _("Scatter plots of series") + "\n{0} ({1}) {2}-{3}".format(env.var_D.TYPE_SERIES,
                                                                             env.var_D.UNITS,
                                                                             env.globals_vars.PROCESS_PERIOD['start'],
                                                                             env.globals_vars.PROCESS_PERIOD['end'])

    pyplot.suptitle(str(title_plot, 'utf-8'), y=(fig_height - 0.1) / fig_height,
                    **env.globals_vars.graphs_title_properties(fs=14, fva='top'))

    for iter_v, station_v in enumerate(stations_list):
        for iter_h, station_h in enumerate(stations_list):
            x = station_h.var_D.data_in_process_period
            y = station_v.var_D.data_in_process_period

            ax = pyplot.subplot2grid((len(stations_list), len(stations_list)), (iter_v, iter_h))

            ax.scatter(x, y, marker='o', color=env.globals_vars.colors['plt_default'],
                       edgecolors=env.globals_vars.colors['grey_S3'])

            if iter_h == 0:
                ax.set_ylabel(station_v.code, env.globals_vars.graphs_axis_properties())
            else:
                ax.set_yticklabels([])
            if iter_v == len(stations_list) - 1:
                ax.set_xlabel(str(station_h.code, 'utf-8'), env.globals_vars.graphs_axis_properties())
            else:
                ax.set_xticklabels([])

            pyplot.xticks(rotation='vertical')
            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax, ts=12.5)
            ax.autoscale(tight=True)

            pyplot.tight_layout(pad=0.8)

    # adjust title plot
    pyplot.subplots_adjust(top=(fig_height - 0.6) / fig_height)

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
    bins = 1 + 3.3 * log10(n)

    hist, bin_edges = histogram(data, bins=int(round(bins)))

    return hist, bin_edges


def frequency_histogram(stations_list):
    frequency_histogram_dir = os.path.join(distribution_test_dir, _('Frequency_histogram'))

    output.make_dirs(frequency_histogram_dir)

    for station in stations_list:

        name_graph = _("frequency_histogram_{0}_{1}_{2}").format(station.code, station.name, env.var_D.TYPE_SERIES)

        fig = pyplot.figure()
        ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
        ax.set_title(str(_("Frequency histogram\n{0} {1} - {2} ({3}-{4})").format(station.code, station.name,
                                                                                      env.var_D.TYPE_SERIES,
                                                                                      env.globals_vars.PROCESS_PERIOD[
                                                                                          'start'],
                                                                                      env.globals_vars.PROCESS_PERIOD[
                                                                                          'end']), 'utf-8'),
                     env.globals_vars.graphs_title_properties())


        ## X
        type_var = env.var_D.TYPE_SERIES
        ax.set_xlabel(str('{0} ({1})'.format(type_var, env.var_D.UNITS), 'utf-8'),
                      env.globals_vars.graphs_axis_properties())

        ## Y
        ax.set_ylabel(_('Frequency'), env.globals_vars.graphs_axis_properties())

        # check if all values (var D) are nulls inside the period to process,
        # then render text message in the graph
        if len(station.var_D.data_filtered_in_process_period) == 0:
            ax.text(0.5, 0.5, str(_("All values are nulls"), 'utf-8'),
                    fontsize=14, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        else:
            hist, bin_edges = get_frequency_histogram(station.var_D.data_filtered_in_process_period)
            width = 0.7 * (bin_edges[1] - bin_edges[0])
            center = (bin_edges[:-1] + bin_edges[1:]) / 2.0
            bar(center, hist, width=width, **env.globals_vars.figure_bar_properties())

        ax.grid(True, color='gray')
        env.globals_vars.set_others_properties(ax)
        ax.autoscale(tight=True)

        zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_above=-0.04)

        fig.tight_layout()

        # save image
        image = os.path.join(frequency_histogram_dir, name_graph + '.png')
        pyplot.savefig(image, dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')


def shapiro_wilks_test(stations_list):
    file_shapiro_wilks_var_D \
        = os.path.join(distribution_test_dir, _('shapiro_wilks_test_{0}.csv').format(env.var_D.TYPE_SERIES))

    open_file_D = open(file_shapiro_wilks_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), 'W', 'P_value', 'Ho?']

    csv_file_D.writerow(header)

    for station in stations_list:

        with console.redirectStdStreams():
            # check if all values (var D) are nulls inside the period to process
            if len(station.var_D.data_filtered_in_process_period) == 0:
                W = p_value = float('nan')
                Ho = _('unknown (all values are nulls)')
            else:
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
            '{0}-{1}'.format(env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']),
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
            env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
            station_copy.var_D.convert2(convert_var_D_to)
            if station_copy.var_D.was_converted:
                env.var_D.set_FREQUENCY_DATA(convert_var_D_to, check=False)
            station_copy.var_D.calculate_data_date_and_nulls_in_period()
        if convert_var_I_to:
            env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)
            station_copy.var_I.convert2(convert_var_I_to)
            if station_copy.var_I.was_converted:
                env.var_I.set_FREQUENCY_DATA(convert_var_I_to, check=False)
            station_copy.var_I.calculate_data_date_and_nulls_in_period()

        return station_copy

    for station in stations_list:

        # -------------------------------------------------------------------------
        ## Outliers graph per station

        if env.config_run.settings['graphics']:

            outliers_per_stations_dir = os.path.join(outliers_dir, _("Outliers_per_station"))

            output.make_dirs(outliers_per_stations_dir)

            name_graph = _("Outliers") + "_{0}_{1}_{2}_({3}-{4})".format(station.code, station.name,
                                                                         env.var_D.TYPE_SERIES,
                                                                         env.globals_vars.PROCESS_PERIOD['start'],
                                                                         env.globals_vars.PROCESS_PERIOD['end'])

            fig = pyplot.figure(figsize=(3.8, 7))
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
            ax.set_title(str(_("Outliers") + "\n{0} ({1}-{2})".format(env.var_D.TYPE_SERIES,
                                                                          env.globals_vars.PROCESS_PERIOD['start'],
                                                                          env.globals_vars.PROCESS_PERIOD['end']),
                                 'utf-8'), env.globals_vars.graphs_title_properties())

            ## X
            ax.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
            ax.set_xlabel(str('{0}\n{1}'.format(station.code, station.name), 'utf-8'),
                          env.globals_vars.graphs_axis_properties())

            ## Y
            type_var = env.var_D.TYPE_SERIES
            ax.set_ylabel(str('{0} ({1})'.format(type_var, env.var_D.UNITS), 'utf-8'),
                          env.globals_vars.graphs_axis_properties())
            # ax.set_ylabel(_('Frequency'))

            # check if all values (var D) are nulls inside the period to process
            if len(station.var_D.data_filtered_in_process_period) == 0:
                ax.text(0.5, 0.5, str(_("All values are nulls"), 'utf-8'),
                        fontsize=14, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
                with console.redirectStdStreams():
                    boxplot_station = boxplot([float('nan')] * 3)
            else:
                boxplot_station = boxplot(station.var_D.data_filtered_in_process_period)

            pyplot.setp(boxplot_station['boxes'], color=env.globals_vars.colors['plt_default'], linewidth=2.5)
            pyplot.setp(boxplot_station['medians'], color='red', linewidth=2.5)
            pyplot.setp(boxplot_station['whiskers'], color=env.globals_vars.colors['plt_default'], linestyle='solid',
                        linewidth=2.5)
            pyplot.setp(boxplot_station['fliers'], color='red', markersize=16, marker='+', markeredgecolor='red',
                        markeredgewidth='1')
            pyplot.setp(boxplot_station['caps'], color=env.globals_vars.colors['plt_default'], linewidth=2.5)

            ax.grid(True, color='gray')
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)

            zoom_graph(ax=ax, x_scale_below=-2.5, x_scale_above=-2.5, y_scale_below=-0.04, y_scale_above=-0.04)

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
            # check if all values (var D) are nulls inside the period to process
            if len(station.var_D.data_filtered_in_process_period) == 0:
                with console.redirectStdStreams():
                    boxplot_station = boxplot([float('nan')] * 3)
            else:
                boxplot_station = boxplot(station.var_D.data_filtered_in_process_period)

        # -------------------------------------------------------------------------
        ## Prepare variables for report all outliers of all stations

        outliers_station = {}

        outliers_station['station'] = station

        outliers_station['whiskers_below'] = boxplot_station['whiskers'][0].get_data()[1][1]
        outliers_station['whiskers_above'] = boxplot_station['whiskers'][1].get_data()[1][1]

        ## prepare station for special case
        station_copy = clone_and_transform_station(station,
                                                   convert_var_D_to=env.config_run.settings['analysis_interval'],
                                                   convert_var_I_to=env.config_run.settings['analysis_interval'])

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
                    station.var_I.specific_values = time_series.get_specific_values(station_copy, 'var_I', 0,
                                                                                    outlier_date.month)
                    # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                    values_var_I = get_values_in_range_analysis_interval(station_copy.var_I, outlier_date.year,
                                                                         outlier_date.month, None, 0)
                else:
                    # get the corresponding start day of analysis interval
                    day = locate_day_in_analysis_interval(outlier_date.day)
                    # get I values for outliers date
                    station.var_I.specific_values = time_series.get_specific_values(station_copy, 'var_I', 0,
                                                                                    outlier_date.month, day)
                    # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
                    values_var_I = get_values_in_range_analysis_interval(station_copy.var_I, outlier_date.year,
                                                                         outlier_date.month, day, 0)
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

    if env.config_run.settings['graphics'] and (1 < Station.stations_processed <= 50):

        name_graph = _("Outliers") + "_{0}_({1}-{2})".format(
            env.var_D.TYPE_SERIES, env.globals_vars.PROCESS_PERIOD['start'],
            env.globals_vars.PROCESS_PERIOD['end'])

        if len(stations_list) <= 4:
            _part_title = _("Outliers") + '\n'
            fig = pyplot.figure(figsize=(2.5 + len(stations_list) / 2.5, 7))
        else:
            _part_title = _("Outliers") + ' - '
            fig = pyplot.figure(figsize=(2.5 + len(stations_list) / 2.5, 7))

        ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())

        ax.set_title(str(_part_title + "{0} ({1}-{2})".format(env.var_D.TYPE_SERIES,
                                                                  env.globals_vars.PROCESS_PERIOD['start'],
                                                                  env.globals_vars.PROCESS_PERIOD['end']), 'utf-8'),
                     env.globals_vars.graphs_title_properties())

        ## X
        # xticks(range(len(stations_list)), codes_stations, rotation='vertical')
        ax.set_xlabel(str(_('Stations'), 'utf-8'), env.globals_vars.graphs_axis_properties())

        ## Y
        type_var = env.var_D.TYPE_SERIES
        ax.set_ylabel(str('{0} ({1})'.format(type_var, env.var_D.UNITS), 'utf-8'),
                      env.globals_vars.graphs_axis_properties())
        # ax.set_ylabel(_('Frequency'))

        data_stations = [float('nan') if len(x) == 0 else x for x in data_stations]

        boxplot_station = boxplot(data_stations)

        # X ticks
        xticks(list(range(1, len(stations_list) + 1)), codes_stations, rotation='vertical')

        pyplot.setp(boxplot_station['boxes'], color=env.globals_vars.colors['plt_default'], linewidth=2.5)
        pyplot.setp(boxplot_station['medians'], color='red', linewidth=2.5)
        pyplot.setp(boxplot_station['whiskers'], color=env.globals_vars.colors['plt_default'], linestyle='solid',
                    linewidth=2.5)
        pyplot.setp(boxplot_station['fliers'], color='red', markersize=8, marker='+', markeredgecolor='red',
                    markeredgewidth='1')
        pyplot.setp(boxplot_station['caps'], color=env.globals_vars.colors['plt_default'], linewidth=2.5)

        ax.grid(True, color='gray')
        env.globals_vars.set_others_properties(ax)
        ax.autoscale(tight=True)
        # pyplot.subplots_adjust(bottom=) #(len(array.max(codes_stations))/30.0))

        zoom_graph(ax=ax, x_scale_below=-0.2, x_scale_above=-0.2, y_scale_below=-0.04, y_scale_above=-0.04, abs_x=True)

        fig.tight_layout()

        # save image
        image = os.path.join(outliers_dir, name_graph + '.png')
        pyplot.savefig(os.path.join(outliers_dir, name_graph + '.png'), dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')


    # -------------------------------------------------------------------------
    ## Report all Outliers of all stations in file

    file_outliers_var_D \
        = os.path.join(outliers_dir, _("Outliers_table") + "_{0}_({1}-{2}).csv".format(
        env.var_D.TYPE_SERIES, env.globals_vars.PROCESS_PERIOD['start'],
        env.globals_vars.PROCESS_PERIOD['end']))

    open_file_D = open(file_outliers_var_D, 'w')
    csv_file_D = csv.writer(open_file_D, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    num_max_outliers = 0
    for outliers_station in outliers_all_stations:
        if len(outliers_station['outliers']) > num_max_outliers:
            num_max_outliers = len(outliers_station['outliers'])

    # print header
    header = [_('CODE'), _('NAME'), _('LAT'), _('LON'), _('ALT'), _('PROCESS PERIOD'), _('WHISKERS BELOW'),
              _('WHISKERS ABOVE'), _('NUM. OUTLIERS'), '']

    header_outliers = [_('DATE'), _('VALUE'), _('PHEN_CAT*')]

    header = header + header_outliers * num_max_outliers

    csv_file_D.writerow(header)

    for outliers_station in outliers_all_stations:

        num_outliers = len(outliers_station['outliers'])

        outliers_station_line = [
            outliers_station['station'].code,
            outliers_station['station'].name,
            output.number(outliers_station['station'].lat),
            output.number(outliers_station['station'].lon),
            output.number(outliers_station['station'].alt),
            '{0}-{1}'.format(outliers_station['station'].process_period['start'],
                             outliers_station['station'].process_period['end']),
            output.number(outliers_station['whiskers_below']),
            output.number(outliers_station['whiskers_above']),
            num_outliers, _('OUTLIERS LIST:')
        ]

        # sort the outliers list base on outlier value
        outliers_station['outliers'] = sorted(outliers_station['outliers'], key=lambda x: x[1])

        for outlier in outliers_station['outliers']:
            outliers_station_line.append('{0}-{1}-{2}'.format(outlier[0].year,
                                                              output.fix_zeros(outlier[0].month),
                                                              output.fix_zeros(outlier[0].day)))
            outliers_station_line.append(output.number(outlier[1]))
            outliers_station_line.append(outlier[2])
            # outliers_station_line.append('|')

        csv_file_D.writerow(outliers_station_line)

    # print footnote
    csv_file_D.writerow([])
    csv_file_D.writerow([get_text_of_frequency_data('I')])

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

        station_path = os.path.join(correlation_dir, station.code + '-' + station.name)

        # recalculate data if is needed
        if env.var_D.was_converted:
            station.var_D.calculate_data_date_and_nulls_in_period()
        if env.var_I.was_converted:
            station.var_I.calculate_data_date_and_nulls_in_period()

        output.make_dirs(station_path)

        correlation_values = {'lags': [], 'pearson': []}

        # check if all values (var D or var I) are nulls inside the period to process
        if len(station.var_D.data_filtered_in_process_period) == 0 or len(
                station.var_I.data_filtered_in_process_period) == 0:
            continue

        if type_correlation == 'auto':

            data_X = copy.deepcopy(station.var_D.data_filtered_in_process_period)
            data_Y = copy.deepcopy(station.var_D.data_filtered_in_process_period)

            # calculate pearson for 0 to 24 lags
            pearson = stats.pearsonr(data_X, data_Y)[0]
            for lag in range(25):

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
                try:
                    del data_X[0]
                    del data_Y[-1]
                    pearson = stats.pearsonr(data_X, data_Y)[0]
                except:
                    pearson = float('nan')

            name_of_files = _("Auto_Correlation_{0}_{1}_{2}").format(station.code, station.name, env.var_D.TYPE_SERIES)

        if type_correlation == 'cross':
            # TODO: check if move overlaps between the series is correctly

            data_X = copy.deepcopy(station.var_D.data_in_process_period)
            data_Y = copy.deepcopy(station.var_I.data_in_process_period)

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
                try:
                    del _data_X[0]
                    del _data_Y[-1]
                    pearson = stats.pearsonr(_data_X, _data_Y)[0]
                except:
                    pearson = float('nan')

                correlation_values['lags'].append(-lag)
                correlation_values['pearson'].append(pearson)

            # fix order: -24 to -1
            correlation_values['lags'].reverse()
            correlation_values['pearson'].reverse()

            # -------------------------------------------------------------------------
            # calculate pearson for 0 to 24 lags
            _data_X = list(data_X)
            _data_Y = list(data_Y)
            pearson = stats.pearsonr(_data_X, _data_Y)[0]
            for lag in range(25):

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
                try:
                    del _data_X[-1]
                    del _data_Y[0]
                    pearson = stats.pearsonr(_data_X, _data_Y)[0]
                except:
                    pearson = float('nan')

            name_of_files = _("Cross_Correlation_{0}_{1}_{2}").format(station.code, station.name, env.var_D.TYPE_SERIES)

        # -------------------------------------------------------------------------
        # graphics result

        if env.config_run.settings['graphics']:

            if type_correlation == 'auto':
                fig = pyplot.figure(figsize=(6.5, 4.8))
                title = _("Auto Correlation - {0} {1}\n"
                          "{2} ({3}-{4})").format(station.code, station.name, env.var_D.TYPE_SERIES,
                                                  env.globals_vars.PROCESS_PERIOD['start'],
                                                  env.globals_vars.PROCESS_PERIOD['end'])
            if type_correlation == 'cross':
                fig = pyplot.figure(figsize=(8.5, 4.8))
                title = _("Cross Correlation - {0} {1}\n"
                          "{2} vs {3} ({4}-{5})").format(station.code, station.name, env.var_D.TYPE_SERIES,
                                                         env.var_I.TYPE_SERIES,
                                                         env.globals_vars.PROCESS_PERIOD['start'],
                                                         env.globals_vars.PROCESS_PERIOD['end'])

            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())

            ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

            ## X
            ax.set_xlabel(str(_('Lags'), 'utf-8'), env.globals_vars.graphs_axis_properties())
            # xticks(correlation_values['lags'], x_labels)

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(str(_("Correlation"), 'utf-8'), env.globals_vars.graphs_axis_properties())

            pyplot.axhline(linewidth=1, color='k')

            ax.autoscale(tight=True)

            # bar(correlation_values['lags'], correlation_values['pearson'], align='center', width=0.2, color='k')
            ax.plot(correlation_values['lags'], correlation_values['pearson'], 'ro', linewidth=2.5,
                    **env.globals_vars.figure_plot_properties())
            ax.vlines(correlation_values['lags'], [0], correlation_values['pearson'], linewidth=2.5,
                      color=env.globals_vars.colors['plt_default'])

            pyplot.ylim(-1, 1)

            ax.text(24, -1, str(get_text_of_frequency_data('D'), 'utf-8'), horizontalalignment='right',
                    verticalalignment='center')

            env.globals_vars.set_others_properties(ax)
            ax.grid(True, color='gray')

            zoom_graph(ax=ax, x_scale_below=-0.05, x_scale_above=-0.05, y_scale_below=-0.06, y_scale_above=-0.06)
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

        # print footnote
        csv_file.writerow([])
        csv_file.writerow([get_text_of_frequency_data('D')])
        csv_file.writerow([_("*Data in period {0}-{1}").format(env.globals_vars.PROCESS_PERIOD['start'],
                                                               env.globals_vars.PROCESS_PERIOD['end'])])

        open_file.close()
        del csv_file

    # -------------------------------------------------------------------------
    # cross-correlation matrix table

    if type_correlation == 'cross' and len(stations_list) > 1:

        cross_correlation_matrix = []
        stations_code_and_name = []

        for station_My in stations_list_correlation:
            cross_correlation_matrix_line = []
            for station_Mx in stations_list_correlation:

                data_My = list(station_My.var_D.data_in_process_period)
                data_Mx = list(station_Mx.var_D.data_in_process_period)

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
                                  .format(env.globals_vars.PROCESS_PERIOD['start'],
                                          env.globals_vars.PROCESS_PERIOD['end']))
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
        csv_file.writerow([_("*Data in the period {0}-{1}").format(env.globals_vars.PROCESS_PERIOD['start'],
                                                                   env.globals_vars.PROCESS_PERIOD['end'])])

        open_file.close()
        del csv_file

    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)

    return return_msg


def homogeneity(stations_list):
    return_msg = True

    stations_list_copy = copy.deepcopy(stations_list)

    # -------------------------------------------------------------------------
    # Mann-Whitney-Wilcoxon Test (MWW)

    csv_name = os.path.join(homogeneity_dir, 'MWW_test.csv')
    open_file = open(csv_name, 'w')
    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
    # print header
    csv_file.writerow([_('NAME'), _('CODE'), _('U'), _('P-VALUE'), _('?')])

    for station in stations_list_copy:
        series = station.var_D.data_in_process_period
        series = array.clean(series)

        len_s = len(series)

        s1 = series[0:len_s / 2]
        s2 = series[len_s / 2::]

        u, prob = stats.mannwhitneyu(s1, s2, use_continuity=False)

        p_value = prob * 2.0

        if p_value > 0.05:
            is_homogeneous = _('yes')
        else:
            is_homogeneous = _('no')

        csv_file.writerow([station.name, station.code, output.number(u), output.number(p_value), is_homogeneous])

    # print footnote
    csv_file.writerow([])
    csv_file.writerow([get_text_of_frequency_data('D')])
    csv_file.writerow([_("*Data in the period {0}-{1}").format(env.globals_vars.PROCESS_PERIOD['start'],
                                                               env.globals_vars.PROCESS_PERIOD['end'])])

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
        series = station.var_D.data_in_process_period
        series = array.clean(series)

        len_s = len(series)

        s1 = series[0:len_s / 2]
        s2 = series[len_s / 2::]

        t, p_value = stats.ttest_ind(s1, s2)

        if p_value > 0.05:
            is_homogeneous = _('yes')
        else:
            is_homogeneous = _('no')

        csv_file.writerow([station.name, station.code, output.number(t), output.number(p_value), is_homogeneous])

    # print footnote
    csv_file.writerow([])
    csv_file.writerow([get_text_of_frequency_data('D')])
    csv_file.writerow([_("*Data in the period {0}-{1}").format(env.globals_vars.PROCESS_PERIOD['start'],
                                                               env.globals_vars.PROCESS_PERIOD['end'])])

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
        series = station.var_D.data_in_process_period
        series = array.clean(series)

        len_s = len(series)

        s1 = series[0:len_s / 2]
        s2 = series[len_s / 2::]

        w, p_value = stats.levene(s1, s2)

        if p_value > 0.05:
            is_homogeneous = _('yes')
        else:
            is_homogeneous = _('no')
        csv_file.writerow([station.name, station.code, output.number(w), output.number(p_value), is_homogeneous])

    # print footnote
    csv_file.writerow([])
    csv_file.writerow([get_text_of_frequency_data('D')])
    csv_file.writerow([_("*Data in the period {0}-{1}").format(env.globals_vars.PROCESS_PERIOD['start'],
                                                               env.globals_vars.PROCESS_PERIOD['end'])])

    open_file.close()
    del csv_file

    # -------------------------------------------------------------------------
    # Mass Curve

    if env.var_D.TYPE_SERIES == 'PPT' and env.config_run.settings['graphics']:

        output.make_dirs(os.path.join(homogeneity_dir, _('Mass_Curve')))

        for station in stations_list_copy:
            series = station.var_D.data_in_process_period
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
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())

            titulo = _("{0}\n{1}-{2}") \
                .format(_('Mass Curve'), station.code, station.name)
            ax.set_title(str(titulo, 'utf-8'), env.globals_vars.graphs_title_properties())

            ## X
            ax.set_xlabel(str(_("Time"), 'utf-8'), env.globals_vars.graphs_axis_properties())
            # xticks(station.var_D.date_in_process_period)
            # xticks(rotation='vertical')

            ## Y
            # get units os type of var D or I
            ax.set_ylabel(str(_('{0} accumulated ({1})').format(env.var_D.TYPE_SERIES, env.var_D.UNITS), 'utf-8'),
                          env.globals_vars.graphs_axis_properties())

            pyplot.axhline(linewidth=1, color='k')

            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)

            pyplot.xlim(station.var_D.date_in_process_period[0], station.var_D.date_in_process_period[-1])
            ax.grid(True, color='gray')

            # bar(correlation_values['lags'], correlation_values['pearson'], align='center', width=0.2, color='k')
            ax.plot(station.var_D.date_in_process_period, accumulate, linewidth=5,
                    **env.globals_vars.figure_plot_properties())

            fig.tight_layout()

            # save image
            image = os.path.join(homogeneity_dir, _('Mass_Curve'),
                                 _('Mass_Curve') + '_{0}-{1}.png'.format(station.code, station.name))
            pyplot.savefig(image, dpi=75)

            # stamp logo
            watermarking.logo(image)

            pyplot.close('all')

    return return_msg


def anomaly(stations_list):
    """Calculate the frequency histogram and the time series of the
    anomaly of the data converted to the analysis interval of all
    station (var D).
    """

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
        clim_min, clim_mean, clim_max = get_climatology_data(station, env.config_run.settings['analysis_interval'])
        # get the time series values ordered
        time_series_ordered = sorted(station_copy.time_series['lag_0'], key=lambda x: x[0])
        time_series_var_D_values = [x[1] for x in time_series_ordered]

        # extend the climatology values to N years of time series
        climatology_var_D = clim_mean * (
        env.globals_vars.PROCESS_PERIOD['end'] - env.globals_vars.PROCESS_PERIOD['start'] + 1)

        anomaly_values = [x1 - x2 for (x1, x2) in zip(time_series_var_D_values, climatology_var_D)]
        anomaly_values_cleaned = array.clean(anomaly_values)

        ### Anomaly_time_series
        file_anomaly_time_series \
            = os.path.join(anomaly_time_series_dir,
                           _('Anomaly_time_series_{0}_{1}_{2}.csv').format(env.var_D.TYPE_SERIES, station.code,
                                                                           station.name))
        open_file_anomaly_time_series = open(file_anomaly_time_series, 'w')
        csv_file_anomaly_time_series = csv.writer(open_file_anomaly_time_series,
                                                  delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

        # print header
        header = [_('DATE'), _('ANOMALIES') + ' - {0} ({1})*'.format(station.var_D.type_series, env.var_D.UNITS)]
        csv_file_anomaly_time_series.writerow(header)

        for date_anomaly, anomaly in zip([x[0] for x in time_series_ordered], anomaly_values):
            if env.var_D.is_n_monthly():
                date_formated = str(date_anomaly.year) + ' ' + str(output.analysis_interval_text(date_anomaly.month))
            if env.var_D.is_n_daily():
                date_formated = str(date_anomaly.year) + ' ' + str(
                    output.analysis_interval_text(date_anomaly.month, date_anomaly.day))
            csv_file_anomaly_time_series.writerow([date_formated, output.number(anomaly)])

        # print footnote
        csv_file_anomaly_time_series.writerow([])
        csv_file_anomaly_time_series.writerow([get_text_of_frequency_data('D')])

        open_file_anomaly_time_series.close()
        del csv_file_anomaly_time_series

        if env.config_run.settings['graphics']:

            name_graph = _("Anomaly_frequency_histogram_{0}_{1}_{2}").format(station.code, station.name,
                                                                             env.var_D.TYPE_SERIES)

            fig = pyplot.figure()
            ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
            ax.set_title(
                str(_("Anomaly frequency histogram\n{0} {1} - {2} ({3}-{4})").format(station.code, station.name,
                                                                                         env.var_D.TYPE_SERIES,
                                                                                         env.globals_vars.PROCESS_PERIOD[
                                                                                             'start'],
                                                                                         env.globals_vars.PROCESS_PERIOD[
                                                                                             'end']), 'utf-8'),
                env.globals_vars.graphs_title_properties())

            ## X
            type_var = env.var_D.TYPE_SERIES
            ax.set_xlabel(str('{0} ({1})\n{2}'
                                  .format(type_var, env.var_D.UNITS,
                                          get_text_of_frequency_data('D')), 'utf-8'),
                          env.globals_vars.graphs_axis_properties())

            ## Y
            ax.set_ylabel(_('Frequency'), env.globals_vars.graphs_axis_properties())

            # check if all values (var D) are nulls inside the period to process,
            # then render text message in the graph
            if len(anomaly_values_cleaned) == 0:
                ax.text(0.5, 0.5, str(_("All values are nulls"), 'utf-8'),
                        fontsize=14, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            else:
                hist, bin_edges = get_frequency_histogram(anomaly_values_cleaned)
                width = 0.7 * (bin_edges[1] - bin_edges[0])
                center = (bin_edges[:-1] + bin_edges[1:]) / 2.0
                bar(center, hist, width=width, **env.globals_vars.figure_bar_properties())

            ax.grid(True, color='gray')
            ax.axvline(x=0, color=env.globals_vars.colors['grey_S2'], ls='dashed', linewidth=1)
            env.globals_vars.set_others_properties(ax)
            ax.autoscale(tight=True)
            # ax.text(0.99, 0.985, get_text_of_frequency_data('D', ndays=True), horizontalalignment='right',
            #        verticalalignment='top', transform = ax.transAxes, rotation="vertical")

            zoom_graph(ax=ax, x_scale_below=-0.04, x_scale_above=-0.04, y_scale_above=-0.04)

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


def make_periodogram(station, path_to_save, data, variable):
    output.make_dirs(path_to_save)

    ## Bartlett M
    # calculate the frequencies and power spectral density for var D
    freq_1, Pxx_den_1 = signal.periodogram(data, fs=1.0, window='bartlett', nfft=None, detrend='constant',
                                           return_onesided=True, scaling='density', axis=-1)

    freq_1 = list(freq_1)
    # check if all values (var D) are nulls inside the period to process
    if len(freq_1) == 0:
        return
    # calculate period
    _freq_1 = copy.deepcopy(freq_1)
    del _freq_1[0]
    period_1 = [1 / float(x) for x in _freq_1]
    period_1 = [float('nan')] + period_1

    ## Bartlett M/5
    # for smooth frequency diagram with m=m/5
    freq_2, Pxx_den_2 = signal.welch(data, fs=1.0, window='bartlett', nperseg=round(len(data) / 5.0), nfft=len(data),
                                     detrend='constant',
                                     return_onesided=True, scaling='density', axis=-1)
    freq_2 = list(freq_2)
    # check if all values (var D) are nulls inside the period to process
    if len(freq_2) == 0:
        return
    # calculate period
    _freq_2 = copy.deepcopy(freq_2)
    del _freq_2[0]
    period_2 = [1 / float(x) for x in _freq_2]
    period_2 = [float('nan')] + period_2

    # select and save the top 5 of maximum of pxx_den
    # Pxx_den_station = zip(period_1, freq_1, Pxx_den_1)
    # top_Pxx_den = {}
    # top_Pxx_den[(station.code, station.name)] = sorted(Pxx_den_station, key=lambda x: x[2], reverse=True)[0:6]

    # -------------------------------------------------------------------------
    # graphics result periodogram in period

    if env.config_run.settings['graphics']:

        if variable == 'D':
            title = _("Periodogram - {0} {1}\n"
                      "{2} ({3}-{4})").format(station.code, station.name, env.var_[variable].TYPE_SERIES,
                                              station.process_period['start'], station.process_period['end'])
        if variable == 'I':
            title = _("Periodogram - {0} ({1}-{2})").format(env.var_[variable].TYPE_SERIES,
                                                            station.process_period['start'],
                                                            station.process_period['end'])

        fig = pyplot.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())

        ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

        ## X
        if env.var_[variable].FREQUENCY_DATA in ['bimonthly', 'trimonthly']:
            ax.set_xlabel(str(_('Period') + ' (' + _('months') + ')', 'utf-8'),
                          env.globals_vars.graphs_axis_properties())
        else:
            ax.set_xlabel(
                str(_('Period') + ' (' + env.var_[variable].get_FREQUENCY_DATA(adverb=False) + ')', 'utf-8'),
                env.globals_vars.graphs_axis_properties())
        # xticks(correlation_values['lags'], x_labels)

        ## Y
        # get units os type of var D or I
        ax.set_ylabel(str(_("Power spectral density"), 'utf-8'), env.globals_vars.graphs_axis_properties())
        # ax.set_ylabel(unicode(_('Densidad de potencia espectral'), 'utf-8'), env.globals_vars.graphs_axis_properties())

        # pyplot.axhline(linewidth=0.8, color=env.globals_vars.colors['grey_S1'])

        ax.grid(True, color='gray')
        env.globals_vars.set_others_properties(ax)
        ax.autoscale(tight=True)

        # bar(period, Pxx_den, align='center', color=env.globals_vars.colors['plt_default'], edgecolor='none') #, width=0.5, width=0.003
        plt_1, = ax.plot(period_1, Pxx_den_1, '-o', linewidth=2,
                         **env.globals_vars.figure_plot_properties(mec=env.globals_vars.colors['grey_S4'], ms=7))
        plt_2, = ax.plot(period_2, Pxx_den_2, '-o', linewidth=2,
                         **env.globals_vars.figure_plot_properties(color='red', mec=env.globals_vars.colors['grey_S2'],
                                                                   ms=7))
        # ax.vlines(period, [0], Pxx_den, linewidth=2.5, color=env.globals_vars.colors['plt_default'])

        # # put label on the 3 best points
        # for per, fre, pxx in top_Pxx_den[(station.code, station.name)][0:3]:
        #     ax.annotate(round(per,1), xy=(per, pxx),  xycoords='data',
        #     xytext=(-12, 0), textcoords='offset points', rotation='vertical',
        #     horizontalalignment='center', verticalalignment='center',
        #     color=env.globals_vars.colors['grey_S2'], size=10
        #     )

        ### legend
        l = ax.legend((plt_1, plt_2), (_('Bartlett (M)'), _('Bartlett (M/5)')), loc='upper right',
                      shadow=False, fancybox=False, fontsize=12, markerscale=0.8, framealpha=0.6, numpoints=1,
                      handlelength=1.2)

        # set color for legend text
        for text in l.get_texts():
            text.set_color(env.globals_vars.colors['grey_S3'])
        # set color for legend border
        l.get_frame().set_edgecolor(env.globals_vars.colors['grey_S3'])

        ax.text(0.01, 0.97, str(get_text_of_frequency_data('D'), 'utf-8'), horizontalalignment='left',
                verticalalignment='center', transform=ax.transAxes)

        # pyplot.ylim(-1, 1)
        zoom_graph(ax=ax, x_scale_below=-0.05, x_scale_above=-0.05, y_scale_below=-0.06, y_scale_above=-0.11)
        fig.tight_layout()

        # save image
        if variable == 'D':
            name_of_files = _("Periodogram_(period)_{0}_{1}_{2}").format(station.code, station.name,
                                                                         env.var_[variable].TYPE_SERIES)
        if variable == 'I':
            name_of_files = _("Periodogram_(period)_{0}").format(env.var_[variable].TYPE_SERIES)
        image = os.path.join(path_to_save, name_of_files + '.png')
        pyplot.savefig(image, dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')

    # -------------------------------------------------------------------------
    # graphics result periodogram in frequency

    if env.config_run.settings['graphics']:

        if variable == 'D':
            title = _("Periodogram - {0} {1}\n"
                      "{2} ({3}-{4})").format(station.code, station.name, env.var_[variable].TYPE_SERIES,
                                              station.process_period['start'], station.process_period['end'])
        if variable == 'I':
            title = _("Periodogram - {0} ({1}-{2})").format(env.var_[variable].TYPE_SERIES,
                                                            station.process_period['start'],
                                                            station.process_period['end'])

        fig = pyplot.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())

        ax.set_title(str(title, 'utf-8'), env.globals_vars.graphs_title_properties())

        ## X
        if env.var_[variable].FREQUENCY_DATA in ['bimonthly', 'trimonthly']:
            ax.set_xlabel(str(_('Frequency') + ' (1/' + _('months') + ')', 'utf-8'),
                          env.globals_vars.graphs_axis_properties())
        else:
            ax.set_xlabel(
                str(_('Frequency') + ' (1/' + env.var_[variable].get_FREQUENCY_DATA(adverb=False) + ')', 'utf-8'),
                env.globals_vars.graphs_axis_properties())
        # xticks(correlation_values['lags'], x_labels)

        ## Y
        # get units os type of var D or I
        ax.set_ylabel(str(_("Power spectral density"), 'utf-8'), env.globals_vars.graphs_axis_properties())
        # ax.set_ylabel(unicode(_('Densidad de potencia espectral'), 'utf-8'), env.globals_vars.graphs_axis_properties())

        # pyplot.axhline(linewidth=0.8, color=env.globals_vars.colors['grey_S1'])

        ax.grid(True, color='gray')
        env.globals_vars.set_others_properties(ax)
        ax.autoscale(tight=True)

        # bar(period, Pxx_den, align='center', color=env.globals_vars.colors['plt_default'], edgecolor='none') #, width=0.5, width=0.003
        ax.plot(freq_1, Pxx_den_1, '-o', linewidth=2,
                **env.globals_vars.figure_plot_properties(mec=env.globals_vars.colors['grey_S4'], ms=7))
        ax.plot(freq_2, Pxx_den_2, '-o', linewidth=2,
                **env.globals_vars.figure_plot_properties(color='red', mec=env.globals_vars.colors['grey_S2'], ms=7))
        # ax.vlines(period, [0], Pxx_den, linewidth=2.5, color=env.globals_vars.colors['plt_default'])

        # # put label on the 3 best points
        # for per, fre, pxx in top_Pxx_den[(station.code, station.name)][0:3]:
        #     ax.annotate(round(fre,2), xy=(fre, pxx),  xycoords='data',
        #     xytext=(-12, 0), textcoords='offset points', rotation='vertical',
        #     horizontalalignment='center', verticalalignment='center',
        #     color=env.globals_vars.colors['grey_S2'], size=10
        #     )

        ### legend
        l = ax.legend((plt_1, plt_2), (_('Bartlett (M)'), _('Bartlett (M/5)')), loc='upper right',
                      shadow=False, fancybox=False, fontsize=12, markerscale=0.8, framealpha=0.6, numpoints=1,
                      handlelength=1.2)

        # set color for legend text
        for text in l.get_texts():
            text.set_color(env.globals_vars.colors['grey_S3'])
        # set color for legend border
        l.get_frame().set_edgecolor(env.globals_vars.colors['grey_S3'])

        ax.text(0.01, 0.97, str(get_text_of_frequency_data('D'), 'utf-8'), horizontalalignment='left',
                verticalalignment='center', transform=ax.transAxes)

        # pyplot.ylim(-1, 1)
        zoom_graph(ax=ax, x_scale_below=-0.05, x_scale_above=-0.05, y_scale_below=-0.06, y_scale_above=-0.11)
        fig.tight_layout()

        # save image
        if variable == 'D':
            name_of_files = _("Periodogram_(freq)_{0}_{1}_{2}").format(station.code, station.name,
                                                                       env.var_[variable].TYPE_SERIES)
        if variable == 'I':
            name_of_files = _("Periodogram_(freq)_{0}").format(env.var_[variable].TYPE_SERIES)
        image = os.path.join(path_to_save, name_of_files + '.png')
        pyplot.savefig(image, dpi=75)

        # stamp logo
        watermarking.logo(image)

        pyplot.close('all')

    # -------------------------------------------------------------------------
    # table result

    if variable == 'D':
        name_of_files = _("Periodogram_{0}_{1}_{2}").format(station.code, station.name, env.var_[variable].TYPE_SERIES)
    if variable == 'I':
        name_of_files = _("Periodogram_{0}").format(env.var_[variable].TYPE_SERIES)
    table_file = os.path.join(path_to_save, name_of_files + ".csv")

    open_file = open(table_file, 'w')
    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

    # print header
    csv_file.writerow([_("BARTLETT (M)"), '', '', _("BARTLETT (M/5)")])
    csv_file.writerow([_("POWER SPECTRAL DENSITY"), _("PERIOD") + '**', _('FREQUENCY') + '**'] * 2)

    # sorted by power spectral density
    Pxx_den_sorted_1 = sorted(zip(Pxx_den_1, period_1, freq_1), key=lambda x: x[0], reverse=True)
    Pxx_den_sorted_2 = sorted(zip(Pxx_den_2, period_2, freq_2), key=lambda x: x[0], reverse=True)

    for (_Pxx_den_1, _period_1, _freq_1), (_Pxx_den_2, _period_2, _freq_2) in zip(Pxx_den_sorted_1, Pxx_den_sorted_2):
        csv_file.writerow([output.number(_Pxx_den_1), output.number(_period_1), output.number(_freq_1),
                           output.number(_Pxx_den_2), output.number(_period_2), output.number(_freq_2)])

    # print footnote
    csv_file.writerow([])
    csv_file.writerow([get_text_of_frequency_data('D')])
    csv_file.writerow([_("*Data in the period {0}-{1}").format(env.globals_vars.PROCESS_PERIOD['start'],
                                                               env.globals_vars.PROCESS_PERIOD['end'])])
    if env.var_[variable].FREQUENCY_DATA in ['bimonthly', 'trimonthly']:
        csv_file.writerow(["**" + _("overlapping") + " " + env.var_[variable].get_FREQUENCY_DATA()])
    else:
        csv_file.writerow(["**" + env.var_[variable].get_FREQUENCY_DATA()])

    open_file.close()
    del csv_file


def periodogram(stations_list):
    """Make graphs and tables of periodogram for var D and var I
    """
    # save original state of data for var D and I
    original_freq_data_var_D = env.var_D.FREQUENCY_DATA
    original_freq_data_var_I = env.var_I.FREQUENCY_DATA

    # stations_list_adjusted = convert_stations(stations_list, filling=True)
    stations_list_adjusted = copy.deepcopy(stations_list)
    ## make periodogram for var D (all stations)
    # Filling the variables for all stations before convert
    for station in stations_list_adjusted:
        station.var_D.rollback_to_origin()
        station.var_D.filling()
    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    # Adjust the same frequency data for the two time series
    adjust_data_of_variables(stations_list_adjusted, messages=False)

    # make periodograms for each station for Var D
    for station in stations_list_adjusted:
        station.var_D.calculate_data_date_and_nulls_in_period()
        path_to_save = os.path.join(periodogram_dir, station.code + '-' + station.name)
        data = list(station.var_D.data_filtered_in_process_period)
        make_periodogram(station, path_to_save, data, 'D')

    ## make periodogram for var I
    path_to_save = os.path.join(periodogram_dir)
    station = stations_list_adjusted[0]
    # Filling the variables for all stations before convert
    station.var_I.rollback_to_origin()
    station.var_I.filling()
    # return to original FREQUENCY_DATA of the two variables
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)
    # Adjust the same frequency data for the two time series
    adjust_data_of_variables([station], messages=False)
    station.var_I.calculate_data_date_and_nulls_in_period()
    data = list(station.var_I.data_filtered_in_process_period)
    make_periodogram(station, path_to_save, data, 'I')

    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)


def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    '''
    import matplotlib as mpl
    import numpy as np
    import sys
    bit_rgb = np.linspace(0, 1, 256)
    if position == None:
        position = np.linspace(0, 1, len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
    return cmap


def make_wavelets(station, path_to_save, variable):
    output.make_dirs(path_to_save)

    data = np_array(list(station.var_[variable].data_filtered_in_process_period))

    wa = WaveletAnalysis(data)

    fig = pyplot.figure(figsize=(17, 11))
    gs = gridspec.GridSpec(2, 2, height_ratios=[2, 4], width_ratios=[25, 1])

    ax1 = pyplot.subplot(gs[0, 0], **env.globals_vars.graphs_subplot_properties(bg_color='white'))
    ax2 = pyplot.subplot(gs[1, 0], **env.globals_vars.graphs_subplot_properties(bg_color='white'))
    ax3 = pyplot.subplot(gs[1, 1], **env.globals_vars.graphs_subplot_properties())
    fig.delaxes(ax3)

    ###### firsts graphic
    if variable == 'D':
        ax1.set_title(str(_("Station {0} {1} - {2}-{3}")
                              .format(station.code, station.name, env.globals_vars.PROCESS_PERIOD['start'],
                                      env.globals_vars.PROCESS_PERIOD['end']), 'utf-8'),
                      env.globals_vars.graphs_title_properties())
    else:
        ax1.set_title(str(_("Independent Variable {0} - {1}-{2}")
                              .format(env.var_[variable].TYPE_SERIES, env.globals_vars.PROCESS_PERIOD['start'],
                                      env.globals_vars.PROCESS_PERIOD['end']), 'utf-8'),
                      env.globals_vars.graphs_title_properties())

    x = list(station.var_[variable].date_in_process_period)
    y = list(station.var_[variable].data_in_process_period)

    ax1.plot(x, y, '-', linewidth=2,
             **env.globals_vars.figure_plot_properties(color=env.globals_vars.colors["grey_S3"]))

    # ax1.set_xlabel(_('Time'), env.globals_vars.graphs_axis_properties())

    x_idx_years1 = [d for d in station.var_[variable].date_in_process_period if d.month == 1 and d.day == 1]
    x_idx_years = [station.var_[variable].date_in_process_period.index(d) for d in
                   station.var_[variable].date_in_process_period if d.month == 1 and d.day == 1]
    x_years = [d.year for d in station.var_[variable].date_in_process_period if d.month == 1 and d.day == 1]

    ax1.xaxis.set_ticks(x_idx_years1)

    inter_x = int(round(len(x_years) / 15.0, 0))
    xticklabels = [i if i in x_years[0::inter_x] else '' for i in x_years]

    ax1.set_xticklabels(xticklabels)

    # graphs the background var I categories
    # colors for paint bars and labels: below, normal , above
    if env.config_run.settings['class_category_analysis'] == 3:
        colours = {'below': '#DD4620', 'normal': '#62AD29', 'above': '#6087F1'}
        colours_keys = ['below', 'normal', 'above']
    if env.config_run.settings['class_category_analysis'] == 7:
        colours = {'below3': '#DD4620', 'below2': '#DD8620', 'below1': '#DDC620', 'normal': '#62AD29',
                   'above1': '#60C7F1', 'above2': '#6087F1', 'above3': '#6047F1'}
        colours_keys = ['below3', 'below2', 'below1', 'normal', 'above1', 'above2', 'above3']

    calculate_time_series(station, lags=[0], makes_files=False)
    before_category_of_phenomenon = None
    start_area_date = None
    for idx, iter_date in enumerate(x):
        ## categorize the outlier based on category of var I
        if env.config_run.settings['analysis_interval'] in ['monthly', 'bimonthly', 'trimonthly']:
            # get I values for outliers date
            station.var_I.specific_values = time_series.get_specific_values(station, 'var_I', 0, iter_date.month)
            # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
            values_var_I = get_values_in_range_analysis_interval(station.var_I, iter_date.year, iter_date.month, None,
                                                                 0)
        else:
            # get the corresponding start day of analysis interval
            day = locate_day_in_analysis_interval(iter_date.day)
            # get I values for outliers date
            station.var_I.specific_values = time_series.get_specific_values(station, 'var_I', 0, iter_date.month, day)
            # get all values of var I in analysis interval in the corresponding period of outlier (var_D)
            values_var_I = get_values_in_range_analysis_interval(station.var_I, iter_date.year, iter_date.month, day, 0)
        # get the mean or sum (based on mode_calculation_series_I) of all values of var I
        # in analysis interval in the corresponding period of outlier (var_D)
        value_var_I = time_series.calculate_specific_values_of_time_series(station.var_I, values_var_I)

        # get categorize of phenomenon for the value_var_I
        category_of_phenomenon = get_label_of_var_I_category(value_var_I, station)

        if start_area_date is None:
            start_area_date = iter_date
        if before_category_of_phenomenon is None:
            before_category_of_phenomenon = category_of_phenomenon

        if before_category_of_phenomenon != category_of_phenomenon or idx == len(x) - 1:
            # if before_category_of_phenomenon == "above":
            color = colours[[key for key, value in env.config_run.settings['categories_labels_var_I'].items() if
                             value == before_category_of_phenomenon][0]]
            ax1.axvspan(start_area_date, iter_date, ymax=1, alpha=0.22, color=color)
            before_category_of_phenomenon = category_of_phenomenon
            start_area_date = iter_date

    ## legend of categories
    import matplotlib.patches as mpatches
    legend_items = []
    for category, label in zip(colours_keys, env.config_run.get_CATEGORIES_LABELS_VAR_I()):
        legend_items.append(mpatches.Patch(color=colours[category], label=label, alpha=0.22))

    ax1.legend(handles=legend_items, ncol=env.config_run.settings['class_category_analysis'], loc=9,
               bbox_to_anchor=(0.5, -0.1), frameon=False)

    # ax1.autoscale(tight=True)
    ax1.grid(True, color='gray')
    ax1.set_ylabel(str('{0} ({1})'.format(env.var_[variable].TYPE_SERIES, env.var_[variable].UNITS), 'utf-8'),
                   env.globals_vars.graphs_axis_properties())
    env.globals_vars.set_others_properties(ax1)

    ###### second graphic

    ax2.set_title(str(_("Wavelet power spectrum"), 'utf-8'), env.globals_vars.graphs_title_properties())
    t, s = wa.time, wa.scales

    # colors = [(229, 236, 240), (56, 99, 128), (85, 175, 105), (210,196,0), (182,0,0)]
    # colors = [(211, 231, 243), (110, 171, 207), (56, 99, 128), (64, 201, 94), (255, 239, 10), (254, 0, 0), (150, 0, 0)]
    colors = [(254, 254, 254), (0, 108, 209), (85, 160, 170), (51, 117, 114), (25, 215, 123), (118, 168, 0),
              (255, 239, 10), (240, 183, 92), (254, 0, 0), (254, 0, 0), (150, 0, 0)]
    # colors = [ (85, 175, 105), (210,196,0), (182,0,0)] # This example uses the 8-bit RGB
    my_cmap = make_cmap(colors, bit=True)

    # plot the wavelet power
    T, S = meshgrid(t, s)
    # ax2.contourf(T, S, wa.wavelet_power, 256, cmap=pyplot.get_cmap('gist_stern_r'))
    CT = ax2.contourf(T, S, wa.wavelet_power, 256, cmap=my_cmap)

    if env.var_[variable].FREQUENCY_DATA in ['bimonthly', 'trimonthly']:
        ax2.set_ylabel(str(_("Period (" + _('months') + ")"), 'utf-8'), env.globals_vars.graphs_axis_properties())
    else:
        ax2.set_ylabel(str(_("Period ({0})").format(env.var_[variable].get_FREQUENCY_DATA(adverb=False)), 'utf-8'),
                       env.globals_vars.graphs_axis_properties())
    ax2.set_xlabel(str(_("Years"), 'utf-8'), env.globals_vars.graphs_axis_properties())
    ax2.set_yscale('log')
    ax2.grid(True, color='gray')

    # put the ticks at powers of 2 in the scale
    ticks = unique(2 ** floor(log2(s)))[1:]
    ax2.yaxis.set_ticks(ticks)
    ax2.yaxis.set_ticklabels(ticks.astype(str))
    ax2.set_ylim(128, 0)

    ax2.xaxis.set_ticks(x_idx_years)
    ax2.xaxis.set_ticklabels(xticklabels)

    ax2.text(0, 1.013, str(get_text_of_frequency_data('D'), 'utf-8'), horizontalalignment='left',
             verticalalignment='center', transform=ax2.transAxes)

    # shade the region between the edge and coi
    C, S = wa.coi
    C = append(t.min(), C)
    C = append(C, t.max())
    S = append(s.min(), S)
    S = append(S, s.min())

    ax2.fill_between(x=C, y1=S, y2=s.max(), color='gray', edgecolor='black', alpha=0.2, hatch='x')

    cbar = pyplot.colorbar(CT, fraction=1, pad=0.01, ax=ax3)
    # cbar.ax.set_ylabel(unicode(_("Wavelets units"), 'utf-8'), env.globals_vars.graphs_axis_properties())

    for cbar_label in cbar.ax.get_yticklabels():
        cbar_label.set_fontsize(15)
        cbar_label.set_color(env.globals_vars.colors['grey_S3'])

    ax2.grid(True, color='gray')
    env.globals_vars.set_others_properties(ax2)
    ax2.autoscale(tight=True)

    ax2.set_xlim(t.min(), t.max())
    ax2.set_xbound(lower=0, upper=len(station.var_[variable].date_in_process_period) - 1)

    fig.tight_layout()
    gs.update(hspace=0.3)

    # save image
    if variable == 'D':
        name_of_files = _("Wavelets_{0}_{1}_{2}").format(station.code, station.name, env.var_[variable].TYPE_SERIES)
    if variable == 'I':
        name_of_files = _("Wavelets_{0}").format(env.var_[variable].TYPE_SERIES)
    image = os.path.join(path_to_save, name_of_files + '.png')
    pyplot.savefig(image, dpi=75)

    # stamp logo
    watermarking.logo(image)

    pyplot.close('all')


def wavelets(stations_list):
    """Make graphs and tables of Wavelets for var D and var I
    """
    # save original state of data for var D and I
    original_freq_data_var_D = env.var_D.FREQUENCY_DATA
    original_freq_data_var_I = env.var_I.FREQUENCY_DATA

    # stations_list_adjusted = convert_stations(stations_list, filling=True)
    stations_list_adjusted = copy.deepcopy(stations_list)
    ## make periodogram for var D (all stations)
    # Filling the variables for all stations before convert
    for station in stations_list_adjusted:
        station.var_D.rollback_to_origin()
        station.var_D.filling()
    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    # Adjust the same frequency data for the two time series
    adjust_data_of_variables(stations_list_adjusted, messages=False)

    # make wavelets for each station for Var D
    for station in stations_list_adjusted:
        station.var_D.calculate_data_date_and_nulls_in_period()
        path_to_save = os.path.join(wavelets_dir, station.code + '-' + station.name)
        make_wavelets(station, path_to_save, 'D')

    # make wavelet for Var I
    station = stations_list_adjusted[0]
    # Filling the variables for all stations before convert
    station.var_I.rollback_to_origin()
    station.var_I.filling()
    # return to original FREQUENCY_DATA of the two variables
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)
    # Adjust the same frequency data for the two time series
    adjust_data_of_variables([station], messages=False)
    station.var_I.calculate_data_date_and_nulls_in_period()
    station.var_D.calculate_data_date_and_nulls_in_period()
    path_to_save = os.path.join(wavelets_dir)
    make_wavelets(station, path_to_save, 'I')

    # return to original FREQUENCY_DATA of the two variables
    env.var_D.set_FREQUENCY_DATA(original_freq_data_var_D, check=False)
    env.var_I.set_FREQUENCY_DATA(original_freq_data_var_I, check=False)
