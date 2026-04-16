#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 21:44:41 2026

@author: josephriley
"""

# import modules
import pandas as pd
import zipfile
import csv
import io
import sys
# create lists for filtering purposes: FEC_COLUMNS to create column names in the txt file, 
# SWING_STATES for filtering states, and KEEPVARS to know which variables to keep
def open_fec(stem):

    #
    #  What we know how to process
    #
    
    info = {
        'cm':    ('cm24.zip','cm.txt','cm_header_file.csv'),
        'cn':    ('cn24.zip','cn.txt','cn_header_file.csv'),
        'indiv': ('indiv24.zip','itcont.txt','indiv_header_file.csv')
        }

    if stem not in info:
        sys.exit('Unexpected stem:',stem)

    #
    #  Get the information for this data compoonent
    #
    
    (zipname,datname,hdrname) = info[stem]

    #
    #  Read the header file with column names
    #
    
    hdr = pd.read_csv(hdrname)
    cols = list(hdr.columns)
    
    #
    #  Open the zip file, open the file within it, and attach
    #  a csv.Reader
    #
    
    archive = zipfile.ZipFile(zipname)
    
    inp_byte   = archive.open(datname)
    inp_handle = io.TextIOWrapper(inp_byte)
    inp_reader = csv.reader(inp_handle,delimiter='|',quoting=csv.QUOTE_NONE)

    #
    #  Return the columns and the reader object
    #
    
    return cols, inp_reader

cols, reader = open_fec('indiv')

for i, row in enumerate(reader):
    if i == 0:
        print(cols)  # header
    print(row)

    if i > 10:  # just preview
        break
    
from datetime import datetime
 
SWING_STATES = {"PA", "MI", "WI", "AZ", "GA", "NV", "NC"}
 
KEEPVARS = ["CMTE_ID", "STATE", "ZIP_CODE", "PGI", "date", "amt"]

results = []
count_after_swing = 0

col_index = {name: i for i, name in enumerate(cols)}

for row in reader:
    # rename PGI
    pgi = row[col_index['TRANSACTION_PGI']]
    # filter to general election
    if pgi != 'G2024':
        continue
    # filter date
    try:
       dt = datetime.strptime(row[col_index["TRANSACTION_DT"]], "%m%d%Y")
    except ValueError:
       continue
    if dt.year < 2023:
       continue
    # filter to swing states
    state = row[col_index['STATE']]
    if state not in SWING_STATES:
       continue
    count_after_swing +=1
    try:
        amt = float(row[col_index['TRANSACTION_AMT']])
    except ValueError:
        continue
    # trim zip
    zip_code = row[col_index["ZIP_CODE"]].strip().zfill(5)[:5]
    # build 'results'
    results.append({
        "CMTE_ID":  row[col_index["CMTE_ID"]],
        "STATE":    state,
        "ZIP_CODE": zip_code,
        "PGI":      pgi,
        "date":     dt.strftime("%Y-%m"),
        "amt":      amt,
        })                
    
print(f"  Final rows kept:           {len(results):>10,}")

results = pd.DataFrame(results)
results.to_csv('2024contributions.csv', index=False)
results.to_pickle('indiv_swing_2024.zip')



