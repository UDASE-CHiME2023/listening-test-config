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

# folder containing the data
data_dir = 'data_normalized'

# list of conditions
conditions = [os.path.basename(x) for x in glob(data_dir + '/C*', recursive = True)]

# unprocessed condition
unprocessed_condition = 'C0'

# reference condition
ref_condition = 'ref'

# number of listening sessions
n_sessions = 4

# output directory 
config_dir = 'config_files'
if not os.path.isdir(config_dir):
    os.makedirs(config_dir)

#%% Preprocess the list of stimuli
'''
Split the list of stimuli into subsets.
Associate each subset to a panel of subjects.
'''

n_subsets = 4 # a listening test is splitted into n_subsets subtests/subsets
n_subjects_per_subset = 8 # number of participants per subset

df_stimuli = pd.DataFrame(columns=['subset', 'stimulus', 'subjects'])    


# get list of stimuli with at most n_spk speakers
# we assume that the stimuli for all conditions have the same wav file 
# names (the reference is the unprocessed condition)
pathpattern = os.path.join(data_dir, unprocessed_condition, '**/*.wav')
stim_list = [x for x in glob(pathpattern, recursive=True)]

# shuffle the list
random.shuffle(stim_list)

# create n_subsets subsets of (approximately) equal size
# from the list of stimuli
stim_subsets = np.array_split(stim_list, n_subsets)
stim_subsets = [list(map(str, list(el))) for el in stim_subsets]

# shuffle the splits
random.shuffle(stim_subsets)

# create dataframe
for n, subset in enumerate(stim_subsets):
    
    subset_ind = n+1
    
    # list of participants for the current subset (or "subtest")
    subjects = np.arange(n*n_subjects_per_subset,(n+1)*n_subjects_per_subset) + 1
    
    # add a row to the dataframe for each stimulus in the current subset
    for stim in subset:
        
        stim_id = stim.split('/')[-2:]
        stim_id = os.path.join(*stim_id)
        
        row = [subset_ind, stim_id, subjects]
        df_stimuli.loc[len(df_stimuli)] = row

# sort dataframe
df_stimuli = df_stimuli.sort_values(by=['subset'])

# save to csv and json
df_stimuli.to_csv(os.path.join(config_dir, 'split_stimuli.csv'))
# df_stimuli.to_json(os.path.join(config_dir, 'split_stimuli.json'), orient='records', indent=1)

#%% Create config files for each subject

# for each subject
for subject_id in range(1,33):
        
    #%% dataframe for the exeprimental conditions
    
    df_subject_exp = pd.DataFrame(columns=['subset', 'session', 'file', 'first_scale'])
    
    # loop over stimuli
    for index, row in df_stimuli.iterrows():  
        
        # consider only stimuli associated with current subject
        if subject_id in row.subjects:
            
            # loop over conditions
            for cond in conditions:
                            
                # path to the stimulus for the current condition
                file = os.path.join(data_dir, cond, row.stimulus)
                
                # add row to dataframe
                # we do not fill in session and first_scale for the moment
                df_subject_exp.loc[len(df_subject_exp)] = [row.subset, 'x', file, 'x']
    
    # shuffle rows
    df_subject_exp = df_subject_exp.sample(frac=1, random_state=SEED, 
                                           ignore_index=True)        
    
    # fill in session and first_scale columns
    n_samples_per_session = len(df_subject_exp)//n_sessions
    
    for index, row in df_subject_exp.iterrows():
            
        # session index
        session_ind = index//n_samples_per_session + 1
        
        # balance the presentation order of the SIG and BAK scales
        if (row.subset == 1 or row.subset == 2) and (session_ind == 1 or session_ind == 2):
            first_scale = 'SIG'
        elif (row.subset == 1 or row.subset == 2) and (session_ind == 3 or session_ind == 4):
            first_scale = 'BAK'
        elif (row.subset == 3 or row.subset == 4) and (session_ind == 1 or session_ind == 2):
            first_scale = 'BAK'
        elif (row.subset == 3 or row.subset == 4) and (session_ind == 3 or session_ind == 4):
            first_scale = 'SIG'
            
        df_subject_exp.at[index,'session'] = session_ind
        df_subject_exp.at[index,'first_scale'] = first_scale
        
    #%% dataframe for the reference conditions
    
    subset = df_subject_exp.subset.iloc[0]
    session = 0
    
    df_subject_ref = pd.DataFrame(columns=['subset', 'session', 'file', 'first_scale'])
    
    ref_file_list = glob(os.path.join(data_dir, ref_condition, '*.wav'))
    random.shuffle(ref_file_list)
    
    first_scale = random.choice(['SIG', 'BAK'])
    
    for i, file in enumerate(ref_file_list):
        if i == len(ref_file_list)//2:
            if first_scale == 'SIG':
                first_scale = 'BAK'
            else:
                first_scale = 'SIG'
        df_subject_ref.loc[len(df_subject_ref)] = [subset, session, file, first_scale]
        
    #%% complete dataframe with all rating scales
    
    # concatenate reference and experimental conditions
    df_subject = pd.concat([df_subject_ref, df_subject_exp])
    
    # init complete dataframe
    df_subject_all_scales = pd.DataFrame(columns=['subset', 'session', 'file', 'scale'])
    
    # fill in dataframe
    for index, row in df_subject.iterrows():
        
        if row.first_scale == 'SIG':
            scale_list = ['SIG', 'BAK', 'OVRL']
        else:
            scale_list = ['BAK', 'SIG', 'OVRL']
            
        [subset, session, file, _] = row
        
        for scale in scale_list:
            row = [subset, session, file, scale]
            df_subject_all_scales.loc[len(df_subject_all_scales)] = row
            
    #%% save to csv and json
    
    output_dir = os.path.join(config_dir, 'csv')
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    df_subject_all_scales.to_csv(os.path.join(output_dir, 'subject_' + str(subject_id) + '.csv'))
        
    output_dir = os.path.join(config_dir, 'json')
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
        
    # df_subject_all_scales.to_json(os.path.join(output_dir,'subject_' + str(subject_id) + '.json'), orient='records', indent=1)
    with open(os.path.join(output_dir,'subject_' + str(subject_id) + '.json'), 'w') as f:
        json.dump(df_subject_all_scales.to_dict('records'), f, indent=1)
    
    