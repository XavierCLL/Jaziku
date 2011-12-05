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
 
import scipy.stats as stat
 
def contingency_test(O, E = None, alpha = 0.10, side = 0):
    """
    O     - input observed values matrix, each column is a category. 
    E     - expected values, will be computed if None.
    alpha - significance level, as numeric, example:0.01, 0.05, 0.10
    side  - -1 left sided
             0 two-sided 
             1 right sided
 
    Returns an object with the following information.
      data      - reference to M, be sure not to destroy M as values may get recalculated.
      expected  - expected value matrix.
      test_stat - test statistic
      df        - degree of freedom
      p-value   - pvalue
    """
    m = len(O)
    n = len(O[0])
 
    if E is None:
        E = [[0.0] * n  for i in range(m)]
    colsum = [0.0] * n
    rowsum = [0.0] * m 
 
    # compute all marginal sums.
    for i in range(m):
        rowsum[i] = sum([O[i][j] for j in range(n)])
    for j in range(n):
        colsum[j] = sum([O[i][j] for i in range(m)])
    Tot = float(sum(rowsum))
 
    # Compute expected values.
    for i in range(m):
        for j in range(n):
            E[i][j] = (colsum[j] * rowsum[i]) / Tot    
 
    # Compute statistic.
    teststat = 0.0
    for i in range(m):
        for j in range(n):
            if E[i][j] != 0:
                teststat += (E[i][j] - O[i][j]) ** 2 / E[i][j]  
 
    # Determine critical value.
    if m == 1:  # single row?
        df = n - 1
    elif n == 1: # single column?
        df = m - 1
    else:
        df = (m - 1) * (n - 1)
 
    if side == -1:
        critvalue = stat.chi2.ppf(alpha, df)  # http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2.html#scipy.stats.chi2
        pvalue = stat.chi2.cdf(teststat, df)
    elif side == 0:
        critvalue = stat.chi2.ppf(1 - alpha / 2.0, df)
        pvalue = (1.0 - stat.chi2.cdf(teststat, df))
    else:
        critvalue = stat.chi2.ppf(1 - alpha, df)
        pvalue = 1.0 - stat.chi2.cdf(teststat, df)
 
    return  O, E, teststat, critvalue, df, pvalue, alpha
 
 
# Observed, Expected, teststat, critvalue, df, pvalue, alpha=  contingencytest(M, None, alpha, side)


