#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011 IDEAM
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

# this file base on:
#
# file     testofcorr.py
# author   Ernesto P. Adorio
#          ernesto.adorio @ gmail.com
#          UP at Clarkfield
#          Angeles, Pampanga
# version  0.0.1 april 4, 2010
# http://dr-adorio-adventures.blogspot.com/2010/04/testing-significance-of-correlation.html

from math import sqrt
from scipy.stats import t

def ttest(samplestat, se, df, alpha = 0.05, side = 0):
    """                                            
    T-test of a sample statistic.                  
    Arguments:                                     
     samplestat- sample statistic                  
     se -    standard error of sample statistic    
     df      degree of freedom                     
     alpha - significance level                    
     side  - -1 left-sided test                    
             0  double sided test                  
             +1 right-sided test                   
    """                                            
    Ttest = samplestat / se                          
    if side == 0:                                   
        pvalue = t.cdf(Ttest, df)                     
        if Ttest > 0:                              
            pvalue = 1 - pvalue                      
        pvalue *= 2                                 
        tcrit1 = t.ppf(alpha / 2, df)              
        tcrit2 = t.ppf(1 - alpha / 2.0, df)             
        return pvalue, Ttest, (tcrit1, tcrit2)      
    elif side == -1:                               
        pvalue = t.cdf(Ttest, df)                     
        tcrit = t.ppf(alpha, df)                      
        return pvalue, Ttest, tcrit                 
    else:                                          
        pvalue = 1 - t.cdf(Ttest, df)                  
        tcrit = t.ppf(1.0 - alpha, df)                 
        return pvalue, Ttest, tcrit                 

def corrtest(rho, r, n, alpha = 0.05, side = 0):
    se = sqrt((1 - r * r) / (n - 2.0))
    return ttest(r - rho, se, n - 2, alpha, side)

#example
#rho = 0
#r = 0.951
#alpha = 0.05
#side = 1
#n = 14
#print "Berenson's example, p. 546"
#print corrtest(rho, r, n, alpha, side)
