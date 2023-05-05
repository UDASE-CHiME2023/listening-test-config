#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import numpy as np
import pandas as pd
import os
from glob import glob
import random

# folder containing the data
data_dir = 'data_normalized'

# list of conditions
conditions = [os.path.basename(x) for x in glob(data_dir + '/C*', recursive = True)]

# unprocessed condition
unprocessed_condition = 'C0'

# reference condition
ref_condition = 'ref'


#%% Preprocess the list of stimuli
'''
Split the list of stimuli into subsets.
Associate each subset to a panel of subjects.
Split each subset into listening sessions.
Define the rating scale order for each stimulus.
'''

n_subsets = 4 # a listening test is splitted into n_subsets subtests/subsets
n_subjects_per_subset = 8 # number of participants per subset
n_sessions = 4 # each subset is made of n_sessions listening sessions
n_split = n_subsets*n_sessions # total number of splits

df_stimuli = pd.DataFrame(columns=['subset', 'session', 'stimulus',
                                   'first_scale', 'subjects'])    


# get list of stimuli with at most n_spk speakers
# we assume that the stimuli for all conditions have the same wav file 
# names (the reference is the unprocessed condition)
pathpattern = os.path.join(data_dir, unprocessed_condition, '**/*.wav')
stim_list = [x for x in glob(pathpattern, recursive=True)]

# shuffle the list
random.shuffle(stim_list)

# create n_split splits of (approximately) equal size
# from the list of stimuli
stim_splits = np.array_split(stim_list, n_split)
stim_splits = [list(map(str, list(el))) for el in stim_splits]

# shuffle the splits
random.shuffle(stim_splits)

# create dataframe
for n, split in enumerate(stim_splits):
    
    subset_ind = n//n_subsets + 1 # index of the subset (or "subtest")
    session_ind = np.mod(n, n_subsets) + 1 # index of listening session
    
    # balance the presentation order of the SIG and BAK scales
    if (subset_ind == 1 or subset_ind == 2) and (session_ind == 1 or session_ind == 2):
        first_scale = 'SIG'
    elif (subset_ind == 1 or subset_ind == 2) and (session_ind == 3 or session_ind == 4):
        first_scale = 'BAK'
    elif (subset_ind == 3 or subset_ind == 4) and (session_ind == 1 or session_ind == 2):
        first_scale = 'BAK'
    elif (subset_ind == 3 or subset_ind == 4) and (session_ind == 3 or session_ind == 4):
        first_scale = 'SIG'
    
    # list of participants for the current subset (or "subtest")
    subjects = np.arange((subset_ind-1)*n_subjects_per_subset,subset_ind*n_subjects_per_subset)+1
    
    # add a row to the dataframe for each stimulus in the current split
    for stim in split:
        
        stim_id = stim.split('/')[-2:]
        stim_id = os.path.join(*stim_id)
        
        row = [subset_ind, session_ind, stim_id, first_scale, subjects]
        df_stimuli.loc[len(df_stimuli)] = row

# sort dataframe
df_stimuli = df_stimuli.sort_values(by=['subset', 'session'])

# save to csv and json
df_stimuli.to_csv('config.csv')
df_stimuli.to_json('config.json', orient='records', indent=1)

#%% Create config file for each subject

subject_id = 1

# get the list of stimuli for the subject
df_subject = pd.DataFrame(columns=['subset', 'session', 'file', 'first_scale'])

# reference conditions

ref_file_list = glob(os.path.join(data_dir, ref_condition, '*.wav'))
random.shuffle(ref_file_list)

first_scale = random.choice(['SIG', 'BAK'])

for i, file in enumerate(ref_file_list):
    
    subset = 'x'
    session = 0
    
    if i == len(ref_file_list)//2:
        
        if first_scale == 'SIG':
            first_scale = 'BAK'
        else:
            first_scale = 'SIG'
    
    df_subject.loc[len(df_subject)] = [subset, session, file, first_scale]

# experimental conditions
for index, row in df_stimuli.iterrows():
    
    if subject_id in row.subjects:
        
        for cond in conditions:
            
            file = os.path.join(data_dir, cond, row.stimulus)
            
            [subset, session, stim, first_scale, _] = row
            
            df_subject.loc[len(df_subject)] = [subset, session, file, first_scale]


toto = df_subject[df_subject.session == 1].sample(frac=1)        
df_subject.loc[df_subject.session == 1] = toto