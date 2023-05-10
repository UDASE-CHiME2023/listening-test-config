#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import glob
import os

input_path = 'config_files/json'
output_path = 'config_files/modified_json'
if not os.path.isdir(output_path):
    os.mkdir(output_path)

file_list = glob.glob(os.path.join(input_path, '*.json'))

for file in file_list:
    
    basename = os.path.basename(file)
    
    with open(file, 'r') as f:
        lines = f.readlines()
        
    lines[0] = basename[:-5] + ' = ' + lines[0]
    
    new_file = os.path.join(output_path, basename)
    with open(new_file, 'w') as f:
        f.writelines(lines)