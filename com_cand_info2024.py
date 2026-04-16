#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 16:51:11 2026

@author: josephriley
"""

import zipfile

zips_to_merge = ['weball24.zip', 'cm24.zip', 'cn24.zip']
master_comcanddata_zip = 'combined.zip'

with zipfile.ZipFile(master_comcanddata_zip, 'w') as master:
    for zip_path in zips_to_merge:
        with zipfile.ZipFile(zip_path, 'r') as source:
            for member_name in source.namelist():
                # read the files and write them to master
                content = source.read(member_name)
                master.writestr(member_name, content)
    
# now join the file contents from combined.zip
with zipfile.ZipFile('combined.zip', 'r') as z:
    # join lines from text files within the zips
    combined_content = b''
    for filename in ['weball24.txt', 'cm.txt', 'cn.txt']:
        combined_content += z.read(filename) + b'\n'
    
    # save joined content to a new file
    with open('com_cand_info2024.txt', 'wb') as f:
        f.write(combined_content)
