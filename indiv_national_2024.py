#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 13:53:45 2026

@author: josephriley
"""



# import modules
import pandas as pd
import zipfile
import csv
import io
import sys
# create lists for filtering purposes: FEC_COLUMNS to create column names in the txt file, 
# and KEEPVARS to know which variables to keep
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
 
 
KEEPVARS = ["CMTE_ID", "STATE", "ZIP_CODE", "PGI", "date", "amt"]

results = []


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
    try:
        amt = float(row[col_index['TRANSACTION_AMT']])
    except ValueError:
        continue
    # trim zip
    zip_code = row[col_index["ZIP_CODE"]].strip().zfill(5)[:5]
    # build 'results'
    results.append({
        "CMTE_ID":  row[col_index["CMTE_ID"]],
        "STATE":    row[col_index["STATE"]],
        "ZIP_CODE": zip_code,
        "PGI":      pgi,
        "date":     dt.strftime("%Y-%m"),
        "amt":      amt,
        })                
    
print(f"  Final rows kept:           {len(results):>10,}")

results = pd.DataFrame(results)
results.to_pickle('indiv_national_2024.zip')
# filter to just presidential committees
cand24 = pd.read_csv('com_cand_info_2024.csv')
pres_cmtes_24 = set(cand24['CMTE_ID'].str.strip())
national_24 = results[results['CMTE_ID'].isin(pres_cmtes_24)].copy()
dem_national_24 = national_24[national_24['CMTE_ID'].isin(
    cand24[cand24['CAND_PTY_AFFILIATION_x']=='DEM']['CMTE_ID'])]['amt'].sum()
rep_national_24 = national_24[national_24['CMTE_ID'].isin(
    cand24[cand24['CAND_PTY_AFFILIATION_x']=='REP']['CMTE_ID'])]['amt'].sum()

