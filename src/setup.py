#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as osp
from setuptools import setup, find_packages
from jaziku.plugins import global_var

name = global_var.PROG_NAME

def get_package_data(name, extlist):
    """Return data files for package *name* with extensions in *extlist*"""
    flist = []
    # Workaround to replace os.path.relpath (not available until Python 2.6):
    offset = len(name)+len(os.pathsep)
    for dirpath, _dirnames, filenames in os.walk(name):
        for fname in filenames:
            if not fname.startswith('.') and osp.splitext(fname)[1] in extlist:
                flist.append(osp.join(dirpath, fname)[offset:])
    return flist

setup(name = global_var.PROG_NAME,
      version = global_var.VERSION,
      license = "GNU General Public License (GPL) v3",
      description = "Jaziku is a software for the implementation of composite analysis "\
                     "metodology between the major indices of climate variability and major "\
                     "meteorological variables in puntual scale.",
      long_description = """
        Jaziku is a software for the implementation of composite analysis 
        metodology between the major indices of climate variability and major 
        meteorological variables in puntual scale.
                  
        According to IDEAM’s commitment to promote and guide scientiﬁc research 
        about weather forecasting and climate, "Jazikü" is a program designed to 
        evaluate teleconnections between meteorological variables with the main 
        indices of climate variability aﬀecting climate in Colombia.
        
        Jaziku, follows the composite methodology analysis proposed by The 
        University Corporation for Atmospheric Research (UCAR)), National Oceanic 
        and Atmospheric Administration (NOAA) & U.S. Department of Commerce 
        (DOC)[1][1, 2][1, 2, 3][1, 2, 3] and can produce probability scenarios 
        under which it is expected precipitation or any other variable for speciﬁc 
        sites or areas interpolated to behave, as a function of the probability 
        values predicted for each climate variability and the history of involvement 
        in the quarterly average level. Such scenarios become a powerful tool for 
        decision making by the national meteorological services
        
        [1] National Oceanic and Atmospheric Administration (NOAA) , University 
        Corporation for Atmospheric Research (UCAR)). Creating a Local Climate 
        Product Using Composite Analysis - Print Version of Webcast -(En Linea). 
        1997-2010:COMET Website at http://meted.ucar.edu/, 1997.
        [2] A. Leetmaa Barnston, A. G. NCEP Forecasts of the El Niño of 1997 1998 
        and Its U.S. Impacts. Bull. Amer. Met. Soc, 80:1829 – 1852, 1999.
        [3] M. B. Richman Montroy, D.L. Observed Nonlinearities of Monthly 
        Teleconnections between Tropical Paciﬁc Sea Surface Temperature Anomalies
        and Central and Eastern North American Precipitation. Journal of Climate, 
        11:1812 – 1835, 1998.""",
      author = "Ines Sánchez Rodriguez, Xavier Corredor Llano",
      author_email = "incsanchezro (a) gmail.com, xcorredorl (a) ideam.gov.co",
      url = "http://hg.ideam.gov.co:8000/meteorologia/jaziku",
      platforms="platform-independent",
      packages = find_packages(),
      py_modules = ["jaziku"],
      scripts = [ "bin/jaziku" ],
      install_requires = ["scipy", "argparse", "python-dateutil", "matplotlib", "numpy", "PIL"],
      package_data = {"jaziku":get_package_data("jaziku",('.po','.mo')),
                      "doc":get_package_data("doc",('.pdf','.odp','.txt','.csv'))}
      )
