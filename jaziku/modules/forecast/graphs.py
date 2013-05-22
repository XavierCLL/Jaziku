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

#===============================================================================
# GRAPHS
# Generate pies charts and mosaics for forecast
# http://matplotlib.sourceforge.net/api/pyplot_api.html

import os
from math import isnan
from matplotlib import pyplot
from Image import open as img_open

from jaziku import env
from jaziku.utils import  watermarking, format_out


def forecast_graphs(station):
    """Generate pie charts and mosaics of probability for 3 or 7 categories
     for independent variable for the composite analysis.
    """
    # defined the size of the image
    image_height = 240
    image_width = 310

    image_open_list = []

    for lag in env.config_run.settings['lags']:

        if env.globals_vars.STATE_OF_DATA in [1, 3]:
            title_date_graphic = _("trim {0} ({1})").format(env.config_run.settings['forecast_date']['month'],
                format_out.trimester_in_initials(env.config_run.settings['forecast_date']['month'] - 1))
            filename_date_graphic = _("trim_{0}").format(env.config_run.settings['forecast_date']['month'])

        if env.globals_vars.STATE_OF_DATA in [2, 4]:
            title_date_graphic = "{0} {1}"\
                .format(format_out.month_in_initials(env.config_run.settings['forecast_date']['month'] - 1),
                        env.config_run.settings['forecast_date']['day'])
            filename_date_graphic = "{0}_{1}"\
                .format(format_out.month_in_initials(env.config_run.settings['forecast_date']['month'] - 1),
                        env.config_run.settings['forecast_date']['day'])

        # -------------------------------------------------------------------------
        # climate graphics for 3 categories
        if env.config_run.settings['class_category_analysis'] == 3:
            # Options for graphics pie
            dpi = 75.0
            fig = pyplot.figure(figsize=((image_width) / dpi, (image_height) / dpi))

            fig.suptitle(unicode(_('Probability forecasted of {0} under {1}\n{2} ({3})\nlag {4} - {5} - ({6}-{7})')
                .format(station.var_D.type_series, station.var_I.type_series, station.name, station.code, lag, title_date_graphic,
                        station.process_period['start'], station.process_period['end']),
                        'utf-8'), fontsize=13)

            # colors for paint pie: below, normal , above
            colours = ['#DD4620', '#62AD29', '#6087F1']

            labels = (_('Decrease'), _('Normal'), _('Exceed'))

            values_pie = [station.prob_var_D[lag]['below'],
                          station.prob_var_D[lag]['normal'],
                          station.prob_var_D[lag]['above']]

            explode = (0.03, 0.03, 0.03)

            # assign value for piece of pie
            def autopct_funt(pct):
                total = sum(values_pie)
                val = pct * total / 100.0
                return '{p:1.1f}%\n({v:1.2f})'.format(p=pct, v=val)

            if True in [isnan(value) for value in values_pie]:
                # this append when there are NaN values in contingency table in percentage for this series
                fig.text(0.5, 0.4, _("For this time series there aren't suitable\n"
                                     "probabilities, because there are thresholds\n"
                                     "problems in contingency table, or the series data."), fontsize=10, ha='center')
            else:
                ax = fig.add_subplot(111)
                ax.pie(values_pie, colors=colours, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True)

            pyplot.subplots_adjust(bottom=0.025, top=0.76, left=0.22, right=0.78)

            # dir and name of image
            image_dir_save \
                = os.path.join(station.forecast_dir, _('prob_of_{0}_lag_{1}_{2}_({3}-{4}).png')
                    .format(station.var_D.type_series, lag, filename_date_graphic,
                            station.process_period['start'], station.process_period['end']))

        # save image
        pyplot.savefig(image_dir_save, dpi=dpi)
        pyplot.clf()
        # save dir image for mosaic
        image_open_list.append(image_dir_save)


    # -------------------------------------------------------------------------
    ## Create mosaic

    if len(env.config_run.settings['lags']) != 1:

        mosaic_dir_save \
            = os.path.join(station.forecast_dir, _('mosaic_prob_of_{0}_{1}_({3}-{4}).png')
                .format(station.var_D.type_series, lag, filename_date_graphic,
                        station.process_period['start'], station.process_period['end']))
        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        # http://www.classical-webdesigns.co.uk/resources/pixelinchconvert.html
        #pyplot.figure(figsize=(3.75 * len(env.config_run.settings['lags']), 3.75))
        dpi = 100.0
        mosaic_plots = pyplot.figure(figsize=((image_width * len(env.config_run.settings['lags'])) / dpi, image_height / dpi))
        mosaic_plots.savefig(mosaic_dir_save, dpi=dpi)
        mosaic = img_open(mosaic_dir_save)
        for lag_iter in range(len(env.config_run.settings['lags'])):
            mosaic.paste(img_open(image_open_list[lag_iter]), (image_width * lag_iter, 0))
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