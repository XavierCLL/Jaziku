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

#===============================================================================
# GRAPHS
# Generate pies charts and mosaics for forecast
# http://matplotlib.sourceforge.net/api/pyplot_api.html

import os
from math import isnan
from matplotlib import pyplot
from PIL import Image

from jaziku import env
from jaziku.modules.climate import time_series
from jaziku.modules.climate.thresholds import get_thresholds
from jaziku.utils import  watermarking, output
from jaziku.utils.text import slugify


def forecast_graphs(station):
    """Generate pie charts and mosaics of probability for 3 or 7 categories
     for independent variable for the composite analysis.
    """

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Probability graphics for forecasts (pie chart)

    # defined the size of the image
    image_height = 318
    image_width = 445

    image_open_list = []

    for lag in env.config_run.settings['lags']:

        # -------------------------------------------------------------------------
        # climate graphics for 3 categories
        if env.config_run.settings['class_category_analysis'] == 3:
            # Options for graphics pie
            dpi = 100.0
            fig = pyplot.figure(figsize=((image_width) / dpi, (image_height) / dpi))

            fig.suptitle(unicode(_('Probability forecasts of {0} / {1}\n{2} ({3})\nlag {4} - {5} - ({6}-{7})')
                .format(station.var_D.type_series, station.var_I.type_series, station.name, station.code, lag, env.config_run.settings['forecast_date']['text'],
                        env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']),
                        'utf-8'), **env.globals_vars.graphs_title_properties(fs=12, fva='top'))

            # colors for paint pie: below, normal , above
            colours = ['#DD4620', '#62AD29', '#6087F1']
            colours = list(reversed(colours))

            labels = (unicode(_('Decrease'), 'utf-8'), unicode(_('Normal'), 'utf-8'), unicode(_('Exceed'), 'utf-8'))

            labels = tuple(reversed(labels))

            values_pie = [station.prob_var_D[lag]['below'],
                          station.prob_var_D[lag]['normal'],
                          station.prob_var_D[lag]['above']]

            values_pie = list(reversed(values_pie))

            # assign value for piece of pie
            def autopct_funt(pct):
                total = sum(values_pie)
                val = pct * total / 100.0
                return '{p:1.1f}%\n({v:1.2f})'.format(p=pct, v=val)

            if True in [isnan(value) for value in values_pie]:
                # this append when there are NaN values in contingency table in percentage for this series
                fig.text(0.5, 0.4, unicode(_("For this time series there aren't suitable\n"
                                     "probabilities, because there are thresholds\n"
                                     "problems in contingency table, or the series data."), 'utf-8'), fontsize=10, ha='center')
            else:
                ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
                pie_plot = ax.pie(values_pie, colors=colours, autopct='%1.1f%%', shadow=True)
                # pie without borders
                for wedges in pie_plot[0]:
                    wedges.set_linewidth(0)

                pyplot.legend(tuple(pie_plot[0]), labels, loc=(0.96,0.4), borderaxespad=-3, shadow=False, fancybox=True, fontsize=10, labelspacing=0.3)

            env.globals_vars.set_others_properties(ax)
            #pyplot.subplots_adjust(bottom=0.025, top=0.76, left=0.22, right=0.78)
            pyplot.subplots_adjust(bottom=-0.04, top=0.78, left=0.06, right=0.65)

            # dir and name of image
            image_dir_save \
                = os.path.join(station.forecast_dir, _('prob_of_{0}_lag_{1}_{2}_({3}-{4}).png')
                    .format(station.var_D.type_series, lag, slugify(env.config_run.settings['forecast_date']['text']),
                            env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']))

        # -------------------------------------------------------------------------
        # climate graphics for 7 categories in percentage
        if env.config_run.settings['class_category_analysis'] == 7:
            # Options for graphics pie
            dpi = 100.0
            fig = pyplot.figure(figsize=((image_width) / dpi, (image_height) / dpi))

            fig.suptitle(unicode(_('Probability forecasts of {0} / {1}\n{2} ({3})\nlag {4} - {5} - ({6}-{7})')
                .format(station.var_D.type_series, station.var_I.type_series, station.name, station.code, lag, env.config_run.settings['forecast_date']['text'],
                        env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']),
                        'utf-8'), **env.globals_vars.graphs_title_properties(fs=12, fva='top'))

            # colors for paint pie: *below, normal , *above
            colours = ['#DD4620', '#DD8620','#DDC620', '#62AD29', '#60C7F1', '#6087F1', '#6047F1']
            colours = list(reversed(colours))

            labels = (unicode(_('Strong decrease'), 'utf-8'), unicode(_('Moderate decrease'), 'utf-8'),
                      unicode(_('Weak decrease'), 'utf-8'), unicode(_('Normal'), 'utf-8'),
                      unicode(_('Weak exceed'), 'utf-8'), unicode(_('Moderate exceed'), 'utf-8'),
                      unicode(_('Strong exceed'), 'utf-8'))

            labels = tuple(reversed(labels))

            values_pie = [station.prob_var_D[lag]['below3'],
                          station.prob_var_D[lag]['below2'],
                          station.prob_var_D[lag]['below1'],
                          station.prob_var_D[lag]['normal'],
                          station.prob_var_D[lag]['above1'],
                          station.prob_var_D[lag]['above2'],
                          station.prob_var_D[lag]['above3']]

            values_pie = list(reversed(values_pie))

            # assign value for piece of pie
            def autopct_funt(pct):
                total = sum(values_pie)
                val = pct * total / 100.0
                return '{p:1.1f}%\n({v:1.2f})'.format(p=pct, v=val)

            if True in [isnan(value) for value in values_pie]:
                # this append when there are NaN values in contingency table in percentage for this series
                fig.text(0.5, 0.4, unicode(_("For this time series there aren't suitable\n"
                                     "probabilities, because there are thresholds\n"
                                     "problems in contingency table, or the series data."), 'utf-8'), fontsize=10, ha='center')
            else:
                ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
                pie_plot = ax.pie(values_pie, colors=colours, autopct='%1.1f%%', shadow=True)
                # pie without borders
                for wedges in pie_plot[0]:
                    wedges.set_linewidth(0)
                pyplot.legend(tuple(pie_plot[0]), labels, loc=(0.96,0.27), borderaxespad=-3, shadow=False, fancybox=True, fontsize=9, labelspacing=0.3)

            env.globals_vars.set_others_properties(ax)
            pyplot.subplots_adjust(bottom=-0.04, top=0.78, left=-0.01, right=0.58)

            # dir and name of image
            output.make_dirs(os.path.join(station.forecast_dir, _('probabilistic')))
            image_dir_save \
                = os.path.join(station.forecast_dir, _('probabilistic'), _('prob_of_{0}_lag_{1}_{2}_({3}-{4}).png')
                    .format(station.var_D.type_series, lag, slugify(env.config_run.settings['forecast_date']['text']),
                            env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']))

        # save image
        pyplot.savefig(image_dir_save, dpi=dpi)
        pyplot.clf()
        pyplot.close('all')
        # save dir image for mosaic
        image_open_list.append(image_dir_save)

    # -------------------------------------------------------------------------
    # Create mosaic

    if len(env.config_run.settings['lags']) != 1:

        filename = _('mosaic_prob_of_{0}_under_{1}_{2}_({3}-{4}).png')\
                    .format(station.var_D.type_series, station.var_I.type_series,
                            slugify(env.config_run.settings['forecast_date']['text']),
                            env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end'])

        if env.config_run.settings['class_category_analysis'] == 3:
            mosaic_dir_save \
                = os.path.join(station.forecast_dir, filename)
        if env.config_run.settings['class_category_analysis'] == 7:
            output.make_dirs(os.path.join(station.forecast_dir, _('probabilistic')))
            mosaic_dir_save \
                = os.path.join(station.forecast_dir, _('probabilistic'), filename)

        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        # http://www.classical-webdesigns.co.uk/resources/pixelinchconvert.html
        #pyplot.figure(figsize=(3.75 * len(env.config_run.settings['lags']), 3.75))
        dpi = 100.0
        mosaic_plots = pyplot.figure(figsize=((image_width * len(env.config_run.settings['lags'])) / dpi, image_height / dpi))
        mosaic_plots.savefig(mosaic_dir_save, dpi=dpi)
        mosaic = Image.open(mosaic_dir_save)
        for lag_iter in range(len(env.config_run.settings['lags'])):
            mosaic.paste(Image.open(image_open_list[lag_iter]), (image_width * lag_iter, 0))
        # save
        mosaic.save(mosaic_dir_save)
        # stamp logo
        watermarking.logo(mosaic_dir_save)
        # clear and delete all instances of graphs created by pyplot
        pyplot.clf()
        pyplot.close('all')

    # apply stamp logo
    for image in image_open_list:
        watermarking.logo(image)


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Deterministic graphics for forecasts only for 7 categories (pie chart)

    if env.config_run.settings['class_category_analysis'] == 7:

        image_open_list = []

        for lag in env.config_run.settings['lags']:

            # Options for graphics pie
            dpi = 100.0
            fig = pyplot.figure(figsize=((image_width) / dpi, (image_height) / dpi))

            fig.suptitle(unicode(_('Deterministic forecasts of {0} / {1}\n{2} ({3})\nlag {4} - {5} - ({6}-{7})')
                .format(station.var_D.type_series, station.var_I.type_series, station.name, station.code, lag, env.config_run.settings['forecast_date']['text'],
                        env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']),
                        'utf-8'), **env.globals_vars.graphs_title_properties(fs=12, fva='top'))

            # colors for paint pie: *below, normal , *above
            colours = ['#DD4620', '#DD8620','#DDC620', '#62AD29', '#60C7F1', '#6087F1', '#6047F1']
            colours = list(reversed(colours))

            # get specific values of forecast date for calculating thresholds
            if env.var_D.is_n_monthly():
                # get all values of var D based on this lag and month
                station.var_D.specific_values \
                    = time_series.get_specific_values(station, 'var_D', lag, env.config_run.settings['forecast_date']['month'])
            if env.var_D.is_n_daily():
                # get all values of var D based on this lag and month and day
                station.var_D.specific_values \
                    = time_series.get_specific_values(station, 'var_D', lag, env.config_run.settings['forecast_date']['month'],
                                               env.config_run.settings['forecast_date']['day'])

            # thresholds of var D for deterministic values for use in labels on legend
            thresholds_var_D = get_thresholds(station, station.var_D)

            for tag, value in thresholds_var_D.items():
                thresholds_var_D[tag] = round(value, 1)

            labels = (_('< {0}').format(thresholds_var_D['below3']),
                      _('{0} to {1}').format(thresholds_var_D['below3'], thresholds_var_D['below2']),
                      _('{0} to {1}').format(thresholds_var_D['below2'], thresholds_var_D['below1']),
                      _('{0} to {1}').format(thresholds_var_D['below1'], thresholds_var_D['above1']),
                      _('{0} to {1}').format(thresholds_var_D['above1'], thresholds_var_D['above2']),
                      _('{0} to {1}').format(thresholds_var_D['above2'], thresholds_var_D['above3']),
                      _('> {0}').format(thresholds_var_D['above3']))

            labels = tuple(reversed(labels))

            values_pie = [station.prob_var_D[lag]['below3'],
                          station.prob_var_D[lag]['below2'],
                          station.prob_var_D[lag]['below1'],
                          station.prob_var_D[lag]['normal'],
                          station.prob_var_D[lag]['above1'],
                          station.prob_var_D[lag]['above2'],
                          station.prob_var_D[lag]['above3']]

            values_pie = list(reversed(values_pie))

            # assign value for piece of pie
            def autopct_funt(pct):
                total = sum(values_pie)
                val = pct * total / 100.0
                return '{p:1.1f}%\n({v:1.2f})'.format(p=pct, v=val)

            if True in [isnan(value) for value in values_pie]:
                # this append when there are NaN values in contingency table in percentage for this series
                fig.text(0.5, 0.4, unicode(_("For this time series there aren't suitable\n"
                                     "probabilities, because there are thresholds\n"
                                     "problems in contingency table, or the series data."), 'utf-8'), fontsize=10, ha='center')
            else:
                ax = fig.add_subplot(111, **env.globals_vars.graphs_subplot_properties())
                pie_plot = ax.pie(values_pie, colors=colours, autopct='%1.1f%%', shadow=True)
                # pie without borders
                for wedges in pie_plot[0]:
                    wedges.set_linewidth(0)
                pyplot.legend(tuple(pie_plot[0]), labels, loc=(0.96,0.2), borderaxespad=-3, shadow=False, fancybox=True, fontsize=11, labelspacing=0.3)
                # show units above of legend box
                fig.text(0.745, 0.585, '{0}\n{1} ({2})'.format(env.var_D.UNITS,
                                                               env.config_run.get_MODE_CALCULATION_SERIES_i18n("D"),
                                                               env.config_run.get_ANALYSIS_INTERVAL_i18n()), fontsize=11, ha='center')

            env.globals_vars.set_others_properties(ax)
            pyplot.subplots_adjust(bottom=-0.04, top=0.78, left=0, right=0.59)

            # dir and name of image
            output.make_dirs(os.path.join(station.forecast_dir, _('deterministic')))
            image_dir_save \
                = os.path.join(station.forecast_dir, _('deterministic'), _('Determ_of_{0}_lag_{1}_{2}_({3}-{4}).png')
                    .format(station.var_D.type_series, lag, slugify(env.config_run.settings['forecast_date']['text']),
                            env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']))
            # save image
            pyplot.savefig(image_dir_save, dpi=dpi)
            pyplot.clf()
            # save dir image for mosaic
            image_open_list.append(image_dir_save)

        # -------------------------------------------------------------------------
        # Create mosaic for deterministic forecasts pie chart

        if len(env.config_run.settings['lags']) != 1:

            filename = _('mosaic_determ_of_{0}_under_{1}_{2}_({3}-{4}).png')\
                    .format(station.var_D.type_series, station.var_I.type_series,
                            slugify(env.config_run.settings['forecast_date']['text']),
                            env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end'])
            mosaic_dir_save \
                = os.path.join(station.forecast_dir, _('deterministic'), filename)
            output.make_dirs(os.path.join(station.forecast_dir, _('deterministic')))

            # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
            # http://www.classical-webdesigns.co.uk/resources/pixelinchconvert.html
            #pyplot.figure(figsize=(3.75 * len(env.config_run.settings['lags']), 3.75))
            dpi = 100.0
            mosaic_plots = pyplot.figure(figsize=((image_width * len(env.config_run.settings['lags'])) / dpi, image_height / dpi))
            mosaic_plots.savefig(mosaic_dir_save, dpi=dpi)
            mosaic = Image.open(mosaic_dir_save)
            for lag_iter in range(len(env.config_run.settings['lags'])):
                mosaic.paste(Image.open(image_open_list[lag_iter]), (image_width * lag_iter, 0))
            # save
            mosaic.save(mosaic_dir_save)
            # stamp logo
            watermarking.logo(mosaic_dir_save)
            # clear and delete all instances of graphs created by pyplot
            pyplot.clf()
            pyplot.close('all')

        # apply stamp logo
        for image in image_open_list:
            watermarking.logo(image)