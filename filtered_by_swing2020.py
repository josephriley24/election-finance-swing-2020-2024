#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 14:10:03 2026

@author: josephriley
"""

# import modules
import pandas as pd
# create the dataframe 'raw'
raw = pd.read_csv('contributions2020.zip', dtype=str)

# set the variable n_now
n_now = len(raw)
print(n_now)

# create the columns 'PGI' and 'amt'
raw = raw.rename(columns = {"TRANSACTION_PGI": "PGI"})
raw['amt'] = raw['TRANSACTION_AMT'].astype(float)

# create the variable 'ymd'
ymd = pd.to_datetime(raw['TRANSACTION_DT'], format='%m%d%Y')

# create the column 'date', converting the full date into one with monthly frequency
raw['date'] = ymd.dt.to_period('M')

# set the variable n_last, create the dataframe 'contrib' and reset n_now
n_last = n_now
year_ok = ymd.dt.year >= 2019
contrib = raw.loc[year_ok]
n_now = len(contrib)

# print number of contributions made before 2019
print('Number of 2020 Political Campaign Contributions Made Before 2019:', n_last-n_now)

# set n_last back to n_now
n_last = n_now

# pick out records for primary and general elections in 2020
contrib = contrib.query("PGI == 'G2020'")

# set n_now back to contrib
n_now = len(contrib)

# print number of records that were not for either primary or general elections
print('Number of 2020 Political Campaign Contributions that were not for Primary or General Elections:', n_last - n_now)

# print number of records for 2020 primary or general elections made in 2019 or later
print('Number of 2020 Primary or General Election Contributions made in 2019 or later:', n_now)

# create the list 'keepvars'
keepvars = ['CMTE_ID', 'STATE', 'ZIP_CODE', 'PGI', 'date', 'amt']

# create the variable 'trimmed'
trimmed = contrib[keepvars]

# save a pickled version of 'trimmed'
trimmed.to_pickle('contrib_all_pkl.zip')

# print number of records in pickled dataframe
print('Number of 2020 Primary or General Election Contributions made in 2019 or later:',len(trimmed))

# print columns in the trimmed dataset
print('Columns in the Trimmed Dataset:', list(trimmed.columns))

# set the variable 'grouped'
grouped = trimmed.groupby(['date', 'PGI'])

# set the variable 'by_date_pgi'
by_date_pgi = grouped['amt'].sum()/1e6

# unstack the data to create separate columns for primary and general elections
by_date_wide = by_date_pgi.unstack('PGI')

# trim 'trimmed' to just swing states
SWING_STATES = {'STATE': ["PA", "MI", "WI", "AZ", "GA", "NV", "NC"]}
trimmed = trimmed[trimmed['STATE'].isin(SWING_STATES['STATE'])] 

# fix zip code to match 2024 data  
# create 'zip_all'
zip_all = trimmed['ZIP_CODE']

# create 'ziplen' to produce a series with the length, in characters, of each zip code
ziplen = zip_all.str.len()

# produce a table of counts of zip code lengths
print(ziplen.value_counts(dropna=False))

# create 'zip_9' and 'zip_5'
zip_9 = ziplen == 9
zip_5 = ziplen == 5

# create 'zip_ok'
zip_ok = zip_5 | zip_9
# create 'zip_bad'
zip_bad = ~ zip_ok
# create 'zip5'
zip5 = zip_all.copy()

# set the values of zip5 where the original zip code is 9 digits to the first 5 digits
zip5[zip_9] = zip5[zip_9].str[:5]

# mark 'zip_bad' as missing data
zip5[zip_bad] = None

# create 'zip5len' and print the value counts
zip5len = zip5.str.len()
print(zip5len.value_counts(dropna=False))

# create the column 'zip'
trimmed['zip'] = zip5
# drop old zip column
trimmed = trimmed.drop(columns='ZIP_CODE')
trimmed = trimmed.rename(columns={'zip': 'ZIP_CODE'})



