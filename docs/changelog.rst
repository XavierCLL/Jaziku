.. _changelog:

=========
Changelog
=========

0.5 (**2012-09-XX**)
----------------------

news
++++

- Rewrite, reformation and reorganization all Jaziku project.
- New: (eda) descriptive statistic, this calculate many statistics for var D
  make files and graphs contrast to stations and altitude
- Reformatted runfile adaptation for requirements in eda, these are; new
  parameter in station list "Alt" (altitude), type and limits for var "D"
  and "I" now are static and you set these options in "general options"
  and (of course) delete these parameters in stations list
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



0.4.2 (**2012-08-21**)
----------------------

news
++++
 
- new option in runfile: the "analog_year", with this the calcule of thresholds 
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

0.4.0
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

0.3.0
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
  
0.2.1
----------------------

fixes
+++++

- change name function and filename results of Arithmetic Mean Trim to mean_trim


0.2.0
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