#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 16:51:11 2026

@author: josephriley
"""

import pandas as pd
import zipfile


# use header file for cn
# read the header file
headers = pd.read_csv('cn_header_file.csv')
col_names = headers.columns.tolist()

# read the data from the zip
with zipfile.ZipFile('combined.zip', 'r') as z:
    with z.open('cn.txt') as f:
        cn = pd.read_csv(f, sep='|', names=col_names, 
                         encoding='latin-1', dtype=str)


# use header file for cm
# read the header file
headers = pd.read_csv('cm_header_file.csv')
col_names = headers.columns.tolist()

# read the data from the zip
with zipfile.ZipFile('combined.zip', 'r') as z:
    with z.open('cm.txt') as f:
        cm = pd.read_csv(f, sep='|', names=col_names, 
                         encoding='latin-1', dtype=str)
        
# read the data from the zip (weball)
weball_cols = ['CAND_ID', 'CAND_NAME', 'CAND_ICI', 'PTY_CD', 'CAND_PTY_AFFILIATION', 'TTL_RECEIPTS', 'TRANS_FROM_AUTH', 'TTL_DISB', 'TRANS_TO_AUTH', 'COH_BOP', 'COH_COP', 'CAND_CONTRIB',
               'CAND_LOANS', 'OTHER_LOANS', 'CAND_LOAN_REPAY', 'OTHER_LOAN_REPAY', 'DEBTS_OWED_BY', 'TTL_INDIV_CONTRIB', 'CAND_OFFICE_ST', 'CAND_OFFICE_DISTRICT', 'SPEC_ELECTION',
               'PRIME_ELECTION', 'RUN_ELECTION', 'GEN_ELECTION', 'GEN_ELECTION_PRECENT','OTHER_POL_CMTE_CONTRIB', 'POL_PTY_CONTRIB', 'CVG_END_DT', 'INDIV_REFUNDS', 'CMTE_REFUNDS']
with zipfile.ZipFile('combined.zip', 'r') as z:
    with z.open('weball24.txt') as f:
        weball = pd.read_csv(f, sep='|', names=weball_cols,
                         encoding='latin-1', dtype=str)
# check shapes
print(weball.shape)
print(cn.shape)

# check CAND_ID values in each
print(weball['CAND_ID'].head(10).tolist())
print(cn['CAND_ID'].head(10).tolist())

# check for whitespace issues
print(repr(weball['CAND_ID'].iloc[0]))
print(repr(cn['CAND_ID'].iloc[0]))

# join and filter to general election presidential data to create com_cand_info_2024.csv
merged = pd.merge(weball, cn, left_on='CAND_ID', right_on='CAND_ID', how='inner')
merged = pd.merge(merged, cm, left_on='CAND_PCC', right_on='CMTE_ID', how='inner')
general_p = merged[(merged['CAND_OFFICE']=='P') & (merged['CAND_ELECTION_YR']=='2024')]
general_p.to_csv('com_cand_info_2024.csv', index=False)

