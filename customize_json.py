#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script is used to customize the json files created from generate_config_files.py,
following Matthieu's instruction. This customization is to ease the reading of the
config files by the listening test software.
"""

import pandas as pd

import glob
import os
import json



#%%
"""
Add end_experiment entry to each trial.
This is not necessary anymore, can be removed.
"""

input_path = 'config_files/json'
output_path = 'config_files/modified_json2'
if not os.path.isdir(output_path):
    os.makedirs(output_path)

file_list = glob.glob(os.path.join(input_path, '*.json'))

for file in file_list:
    
    basename = os.path.basename(file)
    
    df = pd.read_json(file)
    df['end_experiment'] = ['false']*len(df)
    
    # row = [df.iloc[-1]['subset'], df.iloc[-1]['session'], 'null', 'null', 'true']
    # df.loc[len(df)] = row
    
    with open(os.path.join(output_path, basename), 'w') as f:
        json.dump(df.to_dict('records'), f, indent=1)
        
#%% 
"""Add a variable with the id of the subject at the beginning of the json.
This was asked by Matthieu and is used to read the file in javascript.
"""


input_path = 'config_files/modified_json2'
output_path = 'config_files/modified_json2'

file_list = glob.glob(os.path.join(input_path, '*.json'))

if not os.path.isdir(output_path):
    os.mkdir(output_path)

for file in file_list:
    
    basename = os.path.basename(file)
    
    with open(file, 'r') as f:
        lines = f.readlines()
        
    # this is necessary
    lines[0] = 'all_trials' + ' = ' + lines[0]
    
    # to match Matthieu's manual modification, just to check, this can be removed
    lines[-2] = ' },\n'
    
    new_file = os.path.join(output_path, basename)
    with open(new_file, 'w') as f:
        f.writelines(lines)