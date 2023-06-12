#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

SEED = 0

import numpy as np
np.random.seed(SEED)
import pandas as pd
import os
from glob import glob
import random
random.seed(SEED)
import json
import shutil
import csv

config_dir = 'config_files'

# number of subjects for listening test
num_subjects = 32

# number of subsets
num_subsets = 4

# number of samples (elements) in each subset
numel_per_subset = 32 # 58, 41, 32

# number of conditions
num_cond = 5

# number of stimuli in anchoring phase
num_stim_anchoring = 48

#%% check that the number of stimuli is as expected

# create dataframe with all stimuli from all subjects
df_all = pd.DataFrame(columns=['subset', 'session', 'file', 'scale'])
for i in range(num_subjects):
    
    file = os.path.join(config_dir, 'json', 'subject_' + str(i+1) + '.json')

    df_subject = pd.read_json(file)
    
    df_all = pd.concat([df_all, df_subject])

# remove duplicates and convert to list
stimuli_list = list(df_all['file'].unique())
# get only basename (i.e., wavfile name, without path)
stimuli_list = [os.path.basename(x) for x in stimuli_list]
# remove duplicates and sort
stimuli_list = list(set(stimuli_list))
stimuli_list.sort()

# check 
assert num_subsets*numel_per_subset + num_stim_anchoring == len(stimuli_list)

#%% copy files to listen for checking

audio_input_dir = 'data/C0'
audio_output_dir = '/data/tmp/to_listen'
if not os.path.isdir(audio_output_dir):
    os.makedirs(audio_output_dir)
    
for file in stimuli_list:
    
    if file[0] == 'i':
        continue
    
    src = os.path.join(audio_input_dir, file)
    dst = os.path.join(audio_output_dir, file)
    shutil.copyfile(src, dst)

#%% create csv for results

df_results = pd.DataFrame(columns=['subject', 'condition', 'sample', 'scale', 'rating'])

for i in range(num_subjects):
    
    file = os.path.join(config_dir, 'json', 'subject_' + str(i+1) + '.json')

    df_subject = pd.read_json(file)
    
    for index, row in df_subject.iterrows():
            
        file = row['file']
        
        sample = os.path.basename(file)
        condition = os.path.basename(os.path.dirname(file))
        scale = row['scale']
        rating = 0
        
        if condition == 'ref': continue
        
        new_row = [i+1, condition, sample, scale, rating]
        
        df_results.loc[len(df_results)] = new_row
        

#%%        

samples = list(df_results['sample'].unique())
conditions = list(df_results['condition'].unique())
conditions.sort()
subjects = list(df_results['subject'].unique())
scales = list(df_results['scale'].unique())

scales = [scales[0]]  # only SIG scale to test

# each element of this dictionnary contains a list of rows to write in a csv file
# each row corresponds to a pair of (stimulus, condition) and contains the 
# ratings of all subjects (nan if the stimulus was not in the subject's subset).
results = {'SIG': [],
           'BAK': [],
           'OVRL': []}

for condition in conditions:
    
    for sample in samples:
            
        for scale in scales:        
            
            ratings = []
            
            for subject in subjects:
                
                test = ((df_results['subject']==subject) & 
                        (df_results['sample']==sample) & 
                        (df_results['condition']==condition) & 
                        (df_results['scale']==scale))
            
                if test.any():                
                    entry = df_results[test]
                    assert len(entry) == 1
                    rating = entry.iloc[0]['rating']
                else:
                    rating = np.nan
                    
                ratings.append(rating)
            
            results[scale].append([condition, sample] + ratings)
                
            
# write each element of results in a csv file
for scale in scales:
    
    # open the file in the write mode
    with open('results/results_' + scale + '.csv', 'w') as f:
        
        # create the csv writer
        writer = csv.writer(f)
        
        row = ['condition', 'sample'] + ['subject_' + str(i+1) for i in range(num_subjects)]
        
        writer.writerow(row)
    
        for row in results[scale]:
        
            writer.writerow(row)