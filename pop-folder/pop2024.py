#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 12:40:11 2026

@author: josephriley
"""

import pandas as pd
import requests
# read the API key into apikey
with open('apikey.txt') as fh:
        apikey = fh.readline().strip()
# set 'api'
api = 'https://api.census.gov/data/2024/acs/acs5'
# set the for clause
#for_clause = 'county:*'
# set the in clause
#in_clause = 'state:36'
# create the dictionary 'payload'
payload = {'get':"B01003_001E",
           'for':'zip code tabulation area:*',
           'key':apikey}
response = requests.get(api, payload)
parsed = response.json()
colnames = parsed[0]
datarows = parsed[1:]
# convert the data into a Pandas dataframe
pop = pd.DataFrame(columns = colnames, data=datarows)
# Rename columns to 'pop' and 'zip'
new_names = {
    'B01003_001E':'pop',
    'zip code tabulation area': 'zip'}
pop = pop.rename(columns=new_names)
# set index to zip, sort by sip and save dataframe
pop = pop.set_index('zip')
pop = pop.sort_index()
pop.to_csv('pop2024.csv')
pop = pd.read_csv('pop2024.csv', dtype={'zip': str})
print(pop.head())
print(pop.dtypes)
print(pop['pop'].describe())
import numpy as np
pop['pop'] = pd.to_numeric(pop['pop'])
pop['pop'] = pop['pop'].replace(-666666666, np.nan)
