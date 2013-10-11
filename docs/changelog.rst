.. _changelog:

=========
Changelog
=========


0.7.0 (**2013-XX-XX**)
----------------------

news
++++

- Analysis the best periods to be process, off all stations
  inside the runfile, and are ranked and organized in based
  on number of stations, number of years and number of nulls.
  Writes a csv file of all possible periods from best to worst
  (in based of ranking) with its corresponding list of stations
  included for the analysis period.
- The calculate for make the time series in range analysis interval
  (and lags) now put NaN if the nulls values are greater than 40% of
  the values.
- New footnote that show the historical values (maximum and minimum
  of the time series based in analysis interval and inside the period
  to process) and thresholds for the respective relevant climate
  categories selected in runfile for the composite analysis graphics
  in climate module
- New thresholds p50+/-NN, this is percentile 50 for the multi-year
  interval analysis values and more or less NN particular values
  (in the same units). In runfile put; p50+NN or p50-NN, e.g.
  p50+3.4, p50-7.8
- [code] Refactoring lag to time_series
- [code] Refactoring read_var_D and read_var_I into read_variable
- [code] Ported the old PIL to new Python-pillow

**ideamFormat2jazikuFormat:**

- For ideamFormat2jazikuFormat script added 3 new filters (time
  series that contain start/end year and minimum size years of
  data) for choose stations for write in runfile
- For ideamFormat2jazikuFormat script now accepted the data
  daily from Sisdhim format, auto-detect and transform to Jaziku
  data daily format

fixes
+++++

- Fix convert time series using mean or accumulate defined in
  mode_calculation_series_X inside runfile
- Fixes some messages and warnings
- Fix units in particular type of time series in y-label for graphs
  for inspection of series
- Fixes units variable translations for var_D and var_I
- Adjust title in Outliers graphs
- Fix crash in some division by zero in statistic tests functions
- Fix infinite loop of recursion calculating the thresholds with
  analog_year
- Fix the black points in deterministic maps for events different
  to "normal"

**ideamFormat2jazikuFormat**

- Force convert dos2unix with binary characters and fix directory
  name when the file haven't extension in ideamFormat2jazikuFormat
- Fix special character in stations name and name variable in
  continue station in ideamFormat2jazikuFormat script
- Fix calculating the number of days in month with data daily and
  fixed when the year is repeat for the same station in
  ideamFormat2jazikuFormat script
- Fixes when run with different variables for each station
- Several fixes and adjust in ideamFormat2jazikuFormat script
- Fix crashed when there are some words inside data (e.g. vectorial
  wind data)



0.6.1 (**2013-06-XX**)
----------------------

news
++++

- New script and executable (ideamFormat2jazikuFormat) that convert
  SISDHIM format of IDEAM to Jaziku inputs format ready for to be processed
  with it.
- New two columns "total data" and "lost data" in descriptive statistic table

fixes
+++++

- Fixed different names for deterministic and probabilistic maps
- Fixed when checking the lags options set from runfile
- Delete variable to reset the forecast date for test
- Fixed and adjust the internal Colombia shape for maps
- Fixed internal thresholds for PPT in 3 categories
- Fix number format in climatology table
- Improve the check values in runfile
- The analog year now can run with different thresholds


0.6.0 (**2013-06-19**)
----------------------

news
++++

- Reform and reorganize the runfile
- Now Jaziku first check and set the grids list before process and show the configurations
  of all grids in configuration run message
- Changed the division when there are more of one options in some configuration in runfile,
  changed from comma separated to different row
- New option in runfile relevant_climate_categories_var_I, with this option
  the user can choose the relevant climate categories of var I for only make
  graphics with these two categories selected or all categories
- New deterministic maps only for 7 categories and climate and forecast (no correlation) maps,
  this map graphs the position of index (inside of the 7 categories) by each station, and
  graphs this station as color point, not graphs interpolation values.
- The 'consistent_data' option in the runfile is a percentage maximum allow of numbers of
  nulls of the var_D and/or var_I of each station, now can set 'default' (=15%) or with
  custom value by user (percentage from 0 to 100)
- Rename the option in runfile var_I_category_labels to categories_labels_var_I
- Adjust climate, correlation and forecast maps for 3 and 7 categories
- Several adjust and fixes for the images of climate and forecast module
- Adjust the images of climate module for output bars and the tables based on the
  relevant_climate_categories_var_I
- The graphics of climate module now make and show the NaN values when one or more
  blocks (as below, normal of above) of the contingency table have not values
- Adjust, for 3 and 7 categories, the method to calculate the contingency table in
  percentage base on threshold size
- New pie chart for forecast module only for 7 categories that use deterministic
  values based on thresholds for the forecast date
- New option in argument: -o --output dir, where 'dir' is the absolute and particular
  directory to save all results that makes Jaziku (this option is optional, default path
  for save result is the same where is the runfile)
- Reimplemented and check code for analog year for and 3 or 7 categories
  and adjust using new functions
- Reimplemented the thresholds by default, now can use 'default' in
  thresholds for particular type for and 3 or 7 categories and adjust
  thresholds for several variables
- Reimplemented the check of probability_forecast_values from input
  forecast_var_I_lag_N for 3 and 7 categories for make the forecast_contingency_table
- New type of thresholds: 'percentage', jaziku now accept percentage as
  thresholds (e.g. 10%, 20%, 45%...) for 3 or 7 categories, this values
  are calculate based on that 100% is the mean of all values of time series
- New validation decorator function for validate the thresholds calculated
  using for this the limits of this variable, for some thresholds as standard
  deviations (sd) this is a requirement and the limits for this variable
  need to be set (not none).
- Now the standard deviation in thresholds by below (for 3 or 7 categories) need
  specify the negative values, e.g: sd-2.1, sd-1.2, sd-0.5, sd0.6, sd0.9, sd1.3
- Defined internal mode_calculation_series for var D and I in 'default' value
  and check it when is chose by the user
- New options in runfile: mode_calculation_series_D and mode_calculation_series_I,
  these are the options to calculate the series: accumulate or mean, and
  adjust all result with this change.
- Updated thresholds for var D for 3 and 7 categories (ATTENTION: this change
  modify several results)
- Updated thresholds for var I for 3 and 7 categories (ATTENTION: this change
  modify several results)
- have the possibility of define internal thresholds and limits for data
  daily o monthly
- Fixes input, check and format for 'forecast_date' option, now new input
  format: month or month;day in runfile.
- Make function that adjust data of all variables if is needed and check
  and convert variables in prepare data function (before run anything)
  (ATTENTION: this change modify several results mainly in EDA module)
- Replace 'forecasting' to 'forecast' string in code and in results
- Now check the values of latitude, longitude and altitude for each stations
- [code] Refactoring config_run, this is where save all variable
  of configuration run settings
- [code] Refactoring globals_vars in new environment dir
- [code] Api documentation
- [code] Moved principal code files into 'core' directory
- [code] Moved some variables of globals_vars to config_run.settings
- [code] Check and prepare all stations before run any modules
- [code] More reused code in input_runfile with new functions
- [code] Organize get_month and get_trimester text function in format_out
- [code] Organize thresholds functions
- [code] Refactoring settings
- [code] Refactoring format_in format_out
- [code] Refactoring thresholds functions for different class_category_analysis
- [code] Refactoring variables for var_D and var_I from globals_vars
- [code] Refactoring limits and null values validations in core.input.validation.py
- [code] Refactoring contingency_tables functions
- [code] Refactoring result table functions and csv results
- [code] Adjust and fixes the maps data for climate for 3 and 7 categories

fixes
+++++

- Check if don't have any common period between series, show error message
  if common period is empty
- Fixed the standard deviation by below for thresholds
- Change the mode to entry forecast_date in runfile, this fixed problems with
  format entries that are auto-convert from sheets application
- Fixed input validation for var I with particular values
- Fix crash detecting languages function when the OS in not defined default locale
- Check when use special internal variables (ONI1, ONI2, CAR) these series have trimester values
  in this case only can use trimester for analysis interval
- Adjust values when two thresholds are equal and if the value to evaluate is the same value too,
  put the value in the middle of category in contingency table
- Fixed initialize matplotlib backend in raster graphics for old version of matplotlib
- Clean stations points with 'nan' values for probabilistic maps

0.5.2a (**2013-02-13**)
-----------------------

fixes
+++++

- Fix bug: enable "shape_boundary" option. Bug description: when "shape_boundary"
  option is enable the maps aren't cutting data outside of shape in mesh data.


0.5.2 (**2013-01-24**)
----------------------

news
++++

- Now Jaziku check is the series (var D/I) are complete in the last and/or
  start year, else Jaziku fill with null values for complete the year,
  but Jaziku required at least January and February for the last year and
  november and december for the start year, due the lags required these
  values.
- The series (var D o I) accept three delimiters: spaces (' '),
  tabulation ('\t') or semi-colon (';')
- Added new independent variables: ONI1, ONI2, SOI_TROUP, W850w, W850c,
  W850e, SST12, SST3, SST4, SST34, ASST12, ASST3, ASST4, ASST34 and
  updated the remaining series
- (Temporally until version 0.7) disable MEI series
- Special case when var_I is ONI1, ONI2 or CAR, don't calculate trimesters
  because the ONI and CAR series was calculated by trimesters from original source
- New multiyears climatology tables for monthly and/or N days

fixes
+++++

- Fixes max and min functions when data has many null values
- Fixed the outliers table filename
- Some adjusts of console text
- Clean/delete some old code needless
- Fix check thresholds as default for internal_var_I_types
- Check if the paths for var D and I is absolute else jaziku convert
  paths to absolute base in runfile directory, this problem present when
  run jaziku in anywhere directory with absolute path to runfile (now it is
  possible)
- Check if var D exist
- Fix path when used var I as internal
- Initialize matplotlib backend in raster graphics
- Fixes for 'special case' in categorize the outliers and calculate lags
- Fixes when use particular value in thresholds for var D or I
- Apply special case when are calculating the contingency table


0.5.1 (**2012-12-05**)
----------------------

news
++++

- Apply stamp (watermarking) for all graphics of Jaziku logo
- New option in runfile for enable or disable the marks of stations
- Plotting marks of stations in maps
- When marks_stations is enable, plotting the legend referent of marks of
  stations
- Plot the color of value in maps when all values are identical

fixes
+++++

- Adjust latitude and longitude of Colombia maps
- restore threshold problem values when run each station
- Fix path to save correlation maps
- Fix call mean function in maps
- Clean some functions
- Many small adjustments
- Fix message number of maps process in each grid
- Fixes max and min whiskers in climatology graphs when the values contain
  nulls
- Fixes subtitles of maps based on analog_year


0.5.0 (**2012-11-22**)
----------------------

news
++++

- Modularization, rewrite, reformation and reorganization all Jaziku project,
  based on develop it during of 1 year I know better the perspective to future
- New: (eda) descriptive statistic, this calculate many statistics for var D
  make files and graphs contrast to stations and altitude
- Reformatted runfile adaptation for requirements in eda, these are; new
  parameter in station list "Alt" (altitude), and the type, limits thresholds,
  path_to_file_var_I, the analysis interval, the 9 values for forecasting and
  forecasting date now are static and you set these options in "configuration run"
  in runfile and (of course) delete these parameters in stations list
- Accept new valid null 'nan' (Not a Number) for input series, now this
  is the default and recommended valid null.
- New: (eda) graphs inspection of series for each station and mosaic
  with inspection of series of var D and var I
- New: now for limits for var D and I can use combination of
  particular value, none or default.
- When the frequency data are different for var D and var I, Jaziku make
  special graphs stretched the x-axis to equalize the x-axis from other
  variable for do the mosaic of inspections of series in EDA
- New: Make the matrix plots of scatter plots of all series of the var D
- New: Climatology table and graphs for var D
- Now the thresholds for var D an I are global values and unique for all
  stations, and config it in "var D/I options" sections of runfile
- New: Shapiro Wilks Test for EDA
- Now accept spaces or tabulations as delimiters in input series of var D or I
- Now the command to run Jaziku is without '-runfile', for example: jaziku runfile.csv
- Now show the warning of limits of variables and notify about of interval var I below
  of configuration run information
- After set all configuration to run, jaziku prompt to user for read the configuration
  and ask for continue.
- Add argument '-f', for force all ask to default answer for continue
- New: Report all outliers of all stations in file and make Box-Jenkins diagram one
  by station and all in one diagram of outliers
- New option in runfile for set particular units for var D or/and I regardless if
  the variables are o not internal variables
- Now Jaziku check the 9 values for forecasting process
- Setting global properties for all graphs of EDA
- Now before run the data analysis, check analysis interval and state of data
- New: check the code and/or name of stations don't repeat, exit or show warning
  depending on the case.
- Not make graphics in EDA module if graphics option in runfile is disabled
- Now use NCARG_ROOT variable defined into system for locate the ncarg libraries
- Now check the basic requirements for maps (ncl, convert, and others)
- Reorganize stations results for climate and forecasting

fixes
+++++

- Many Fixed TYPOS and grammatical language error
- Fix number of line when print runfile error
- Fix flush console message stream when wait process
- Fix particular limits for var D and I
- Fixes when check enable/disable for main process in runfile
- Fix graphs in EDA when var D defined as particular type
- Add and enable the independent variable ARH dipole
- Fix function for redirect standard stream
- Fix global variable thresholds
- Fix when read runfile with NULL byte inside it
- Fixes checking the several valid parameters in runfile
- Fix SST_CAR name and file
- Fix getting units for var D or I when type is external
- Fix when lag equal to 0 Jaziku confused it with None
- Fix when read NaN (standard null) from series
- Fixes particular limits when these are 0
- Check if runfile exist before open
- Show the footer when finished
- Fixes translation in some variables in globals_vars
- Correction in function for extract type and units
- Fix thresholds for NAO!: -1 to 1
- Avoid same name in variable and function in state_of_data
- Limits of 10 and 50 stations for to do the scatter_plots_of_series
  and box-plot of outliers all stations, respectively.
- Fixes when jaziku categorized the outliers with analysis interval equal
  to trimester and var D is daily.
- Constrict and adjust the graphs inspection of series
- Correction the categorized the outliers
- Fixes unicode streams for EDA


0.4.2 (**2012-08-21**)
----------------------

news
++++
 
- new option in runfile: the "analog_year", with this the calculate of thresholds
  for only var D are based on percentile(33 and 66) of all raw values in analog
  year, ignoring null values. For use it, defined analog_year and put "default" 
  value in  THRESHOLD VAR D BELOW/ABOVE in runfile.
- Jaziku now detect and show missing values inside input series of var D and I 

fixes
+++++

- fix when cheking the numbers of parameters of stations list in runfile
- other minor bugfixes


0.4.1 (**2012-08-13**)
----------------------

news
++++

- new option in runfile for select lags to run, this can be 0, 1 and/or 2, 
  combination of these or default (this is all).
- new option in runfile, now you can use any type for dependent variable and 
  select particular values for limits.
- limits var D/I in runfile now can be: none (no check), default (internals limits)
  or particular values.
- new option in runfile for set threshold for dependent variable, this can be:
  default (this is p33 and p66), pNN, sdNN or particular value. 
- new option for maps in runfile, now you can select what you want to run for
  maps, maps can be 'climate', 'forecasting', 'correlation' combination of these, 
  or 'all'
- added the variable particular_properties_map for more settings in ncl script for
  internals or external shapes files

fixes
+++++

- fix check and default value for process period in runfile
- fix console message for graphics process, enable/disable activation
- fix warning message when use "none" in limits dependets and independents variable
- fix when calculated the thresholds with standard desviation, the values 
  must be valid values (without nulls values) 
- fix cheking index value when is "nan"
- fixes typos in messages warnings
- fix translations in some string


0.4.0 (**2012-06-29**)
----------------------

news
++++

- get configuration run and station list in the same file, delete all arguments
  when run Jaziku, now only argument is "-runfile" and this files contains all
  the necessary to run Jaziku.
- adds parameters for maps options in runfile
- ignore station line in runfile that begin with "#"
- Now maps files and maps for climate and forecasting are ordered 
  and grouped based on analysis interval
- Implemented HPGL library for interpolation of the data maps (ordinary kriging
  in this version) and the user can change parameters for interpolation in 
  runfile 
- Generate maps with NCL based in files output of interpolation 
- Shapes and grids internal with particular ncl scripts and extreme lat and lon
  definition
- Personal shape
- Maps for correlations
- Climate/forecasting and correlation palette colors bar for NCL
- Posibility for run many countries or regions and group based on their names
- Posibility to delete data outside of shape, the shape mask method consist 
  in delete all data outside boundaries of shape, analyzing all points in mesh

fixes
+++++

- many fixies and comprobations of all features and changes
- (especifig bug that affect 0.3 version) bug translation in phenomenon label


0.3.0 (**2012-05-22**)
----------------------

news
++++

- now you can run using internal files for independents variables, defining as 
  "default" in "file_I" section inside stations list file.
- enable run with particular independent variable file
- change period defined in argument as process period instead of common period,
  ATTENTION! this affects titles, namefiles and captions of all results
- Result table csv file now write by lags
- Deleted contingency table in results
- Changed the resolution of analysis of trimesters to months and even days, now 
  Jaziku can read var D and I with data daily and can print results for 5, 10, 
  and 15 days, with these changes all result (graphics, tables, ...) are different
  depended if data as daily and how to print result (5,10,15 days) 
- Now maps files (and maps, in the next release) for climate are ordered and 
  grouped based on analysis interval
- Added 3 new variables independent (SST_CAR and AREA_WHWP) and one variable
  dependent (RUNOFF)
- Updated transform_data_stations script
- Consistent data analysis for independent and dependent variable, 
  check the number of null values from all values inside the process period, 
  continue only if it have less than 15%
- add two new arguments: --disable-consistent-data and --disable-graphics
- set to default acuracy to 5 decimal point for print result

fixes
+++++

- bugfix the size data when set particular common period
- fix TYPOS
- fix when Jaziku detect language from system 
- fix crash and memory overflow when open many file
- check different cases to run data daily/monthly and analisis interval defined
- fixed range interval for var I and different lags when data is daily and 
  result is in 5, 10 or 15 days
- fixed constant value for var I when run case 2 (var_D daily and var_I monthly)
  for 5, 10 and 15 days 
- fixed calculating pearson for data daily
- fixed table order for calculate forecasting
  

0.2.1 (**2012-03-24**)
----------------------

fixes
+++++

- change name function and filename results of Arithmetic Mean Trim to mean_trim


0.2.0 (**2012-03-23**)
----------------------

news
++++

- change numeration version
- applied some PEP8 rules, fix typos and reorganize code
- aplied color text in console information for errors, warnings and process 
- final message with number of stations processed when Jaziku has finished
- new argument input "-l" language selector, e.g. "-l es" 
- show in terminal the run configuration
- changes filename outputs for the results and some text inside files/graphics

fixes
+++++

- fix "Segmentation fault" in plt.close() using pyplot
- show and info error when found wrong line or garbage character in input files
- fix crash when the name or number from files (station list and files 
  variables input) contain spaces or tabs at the start or/and final of this.
- fix memory leak using pyplot library   
- fix several strings messages, correct to translate after install, translation
  works now.


0.1.0 initial version (**2011-11-03**)
--------------------------------
- (initial code)