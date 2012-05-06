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

from datetime import date

import globals

#==============================================================================
# VALIDATION FOR DEPENDENT AND INDEPENDENT VARIABLE

#==============================================================================
# Validation var_D (dependent variable)
#
# If inputs are monthly:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=3500mm
#  Num. of days
#   with rain------------NDPPT        -     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=50°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=50°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=50°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----HR          -                0%<=HR<=100%
#  Average flow rate-----AFR        m^3/s                0 to 3300
#
# If inputs are daily:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=200mm
#  Num. of days
#   with rain------------NDPPT        -     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=22°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=34°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=34°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----HR          -                0%<=HR<=100%
#  Average flow rate-----AFR        m^3/s                0 to 3300


def validation_var_D(type_var_D, var_D, date_D, data_of_var_D):
    '''
    Fuction for validation (dependent variable) depending on the type of
    variable
    '''

    # define generic text for generate exception
    def returnError(e):
        # generation exception
        raise ValueError(_("exception validation in dependent variable: "
                           "value out of range:\nThe value \"{1}\" is not "
                           "valid for type variable \"{0}\"\n{2}")
                         .format(type_var_D, var_D, e))

    # validation for precipitation
    def if_var_D_is_PPT():
        if data_of_var_D == "daily":
            if (0 <= var_D <= 200) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("precipitation not valid"))
        if data_of_var_D == "monthly":
            if (0 <= var_D <= 3500) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("precipitation not valid"))

    # validation for number of days with rain
    def if_var_D_is_NDPPT():
        if data_of_var_D == "daily":
            raise Exception(_("validation: (NDPPT) number of days with rain must have\n"
                              "data monthly"))
        if data_of_var_D == "monthly":
            try:
                date(date_D.year, date_D.month, int(var_D))
                return var_D
            except Exception, e:
                if  int(var_D) in globals.VALID_NULL or int(var_D) == 0:
                    return var_D
                else:
                    returnError(e)

    # validation for minimum temperature
    def if_var_D_is_TMIN():
        if data_of_var_D == "daily":
            if (-15 <= var_D <= 22) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("minimum temperature not valid"))
        if data_of_var_D == "monthly":
            if (-15 <= var_D <= 50) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("minimum temperature not valid"))

    # validation for maximun temperature
    def if_var_D_is_TMAX():
        if data_of_var_D == "daily":
            if (-15 <= var_D <= 34) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("maximun temperature not valid"))
        if data_of_var_D == "monthly":
            if (-15 <= var_D <= 50) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("maximun temperature not valid"))

    # validation for medium temperature
    def if_var_D_is_TEMP():
        if data_of_var_D == "daily":
            if (-15 <= var_D <= 34) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("medium temperature not valid"))
        if data_of_var_D == "monthly":
            if (-15 <= var_D <= 50) or int(var_D) in globals.VALID_NULL:
                return var_D
            else:
                returnError(_("medium temperature not valid"))

    # validation for atmosfere pressure
    def if_var_D_is_PATM():
        if (400 <= var_D <= 1100) or int(var_D) in globals.VALID_NULL:
            return var_D
        else:
            returnError(_("atmosfere pressure not valid"))

    # validation for % of relative humidity
    def if_var_D_is_HR():
        if (0 <= var_D <= 100) or int(var_D) in globals.VALID_NULL:
            return var_D
        else:
            returnError(_("% of relative humidity not valid"))

    # validation for Average flow rate
    def if_var_D_is_AFR():
        if (0 <= var_D <= 3300) or int(var_D) in globals.VALID_NULL:
            return var_D
        else:
            returnError(_("Average flow rate not valid"))

    # switch validation
    validation = {
      "PPT": if_var_D_is_PPT,
      "NDPPT": if_var_D_is_NDPPT,
      "TMIN": if_var_D_is_TMIN,
      "TMAX": if_var_D_is_TMAX,
      "TEMP": if_var_D_is_TEMP,
      "PATM": if_var_D_is_PATM,
      "HR": if_var_D_is_HR,
      "AFR": if_var_D_is_AFR
    }
    return validation[type_var_D]()

#==============================================================================
# Validation var_I (independent variable)
#
#     Variable               Abbreviation     Units          Range of variation
# Oceanic Nino Index-------------ONI         anomaly              -5 to 5
# Index of the Southern
# Oscillation NOAA---------------SOI    standarized anomaly       -7 to 7
# Multivariate ENSO index--------MEI           ---            -4.552 to 6.078
# Radiation wavelength
# Long tropical------------------OLR           W/m2               -6 to 6
# Index of wind anomaly----------W200   standarized anomaly     -7.5 to 7.5
# Sea surface temperature--------SST            °C               -60 to 60
# % Amazon relative humidity-----ARH             %              -100 to 100
# North atlantic oscillation index--NAO        anomaly         -6.36 to 6.08
# quasibienal oscillation index--QBO            Km/h           -59.1 to 33.24
# Carribbean (CAR) Index-------SSTA_CAR         °C              -1.3 to 1.3
# Monthly anomaly of the
# ocean surface area Ocean                Area anomaly scaled
# region >28.5C----------------SSTA_WHWP     by 10e6 km^2        -13 to 14

def validation_var_I(type_var_I, var_I, range_below_I, range_above_I):
    '''
    Fuction for validation (independent variable) depending on the type of
    variable
    '''

    # define generic text for generate exception
    def returnError(e):
        # generation exception
        raise ValueError(_("exception validation in independent variable: "
                           "value out of range:\nThe value \"{1}\" is not "
                           "valid for type variable \"{0}\"\n{2}")
                         .format(type_var_I, var_I, e))

    # if defined as particular range
    if type(range_below_I) is float and type(range_above_I) is float:
        if (range_below_I <= var_I <= range_above_I) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("{0} not valid").format(type_var_I))

    # validation for Oceanic Nino Index
    def if_var_I_is_ONI():
        if (-5 <= var_I <= 5) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Oceanic Nino Index not valid"))

    # validation for Index of the Southern Oscillation NOAA
    def if_var_I_is_SOI():
        if (-7 <= var_I <= 7) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Index of the Southern Oscillation NOAA not valid"))

    # validation for Multivariate ENSO index
    def if_var_I_is_MEI():
        if (-4.552 <= var_I <= 6.078) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Multivariate ENSO index not valid"))

    # validation for Radiation wavelength Long tropical
    def if_var_I_is_OLR():
        if (-6 <= var_I <= 6) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Radiation wavelength Long tropical not valid"))

    # validation for Index of wind anomaly
    def if_var_I_is_W200():
        if (-7.5 <= var_I <= 7.5) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Index of wind anomaly not valid"))

    # validation for Sea surface temperature
    def if_var_I_is_SST():
        if (-60 <= var_I <= 60) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Sea surface temperature not valid"))

    # validation for % Amazon relative humidity
    def if_var_I_is_ARH():
        if (-100 <= var_I <= 100) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("% Amazon relative humidity not valid"))

    # validation for North atlantic oscillation index
    def if_var_I_is_NAO():
        if (-6.36 <= var_I <= 6.08) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("North Atlantic Oscillation index not valid"))

    # validation for quasibienal oscillation index
    def if_var_I_is_QBO():
        if (-59.1 <= var_I <= 33.24) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Quasibienal Oscillation Index not valid"))

    # validation for Carribbean (CAR) Index
    def if_var_I_is_SSTA_CAR():
        if (-1.3 <= var_I <= 1.3) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Carribbean (CAR) Index not valid"))

    # validation for Monthly anomaly of the ocean surface area Ocean region
    def if_var_I_is_AREA_WHWP():
        if (-13 <= var_I <= 14) or int(var_I) in globals.VALID_NULL:
            return var_I
        else:
            returnError(_("Monthly anomaly of the ocean surface area Ocean region not valid"))

    # switch validation
    validation = {
      "ONI": if_var_I_is_ONI,
      "SOI": if_var_I_is_SOI,
      "MEI": if_var_I_is_MEI,
      "OLR": if_var_I_is_OLR,
      "W200": if_var_I_is_W200,
      "SST": if_var_I_is_SST,
      "ARH": if_var_I_is_ARH,
      "NAO": if_var_I_is_NAO,
      "QBO": if_var_I_is_QBO,
      "SSTA_CAR": if_var_I_is_SSTA_CAR,
      "SSTA_WHWP": if_var_I_is_AREA_WHWP
    }
    return validation[type_var_I]()
