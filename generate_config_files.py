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
data_dir = 'data'

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
    
#%% create a list that contains the information for each subject

# number of subsets of the complete listening test dataset
n_subsets = 4 

# number of subjects associated to each subset
n_subjects_per_subset = 8

# total number of subjects
n_subjects = n_subsets*n_subjects_per_subset

# create a list where each element is a dataframe containing the stimuli 
# for a given subset
df_subsets = [] 

for i in range(n_subsets):
    df_subset = pd.read_csv('samples_subset_' + str(i+1) + '.csv')
    df_subsets.append(df_subset)


# create a list where each element contains a dictionary corresponding 
# to one subject. The dictionary contains:
# subject_id: the id of the subject (integer)
# subset_id: the id of the subset containing the stimuli for this subject (integer)
# df_stimuli: the dataframe containing the list of stimuli for subset subset_id
# df_subject_exp: the dataframe containing the configuration file for the listening
# experiment of this subject. Each row is a stimulus. It contains the following columns:
# subset: the subset of all stimuli
# session: the listening session index
# file: the stimulus path (wav file)
# first_scale: the first rating scale
subject_data_list = []

# associate each subset to a panel of subjects.
for i in range(n_subjects):
    
    # subjects 1 to 8 --> subset/subset 1, subjects 9 to 816 --> subset/subset 2, etc.
    subset_id = i//n_subjects_per_subset + 1
    
    subject_data = {'subject_id': i+1,
                    'subset_id': subset_id,
                    'df_stimuli': df_subsets[subset_id-1],
                    'df_subject_exp': pd.DataFrame(columns=['subset', 'session', 'file', 'first_scale'])}
    
    
    subject_data_list.append(subject_data)
    
#%% Fill in df_subject_exp for each subject

# for each subject
for subject_ind in range(n_subjects):
        
    # dataframe containing the configuration file for the listening
    # experiment of the current subject
    df_subject_exp = subject_data_list[subject_ind]['df_subject_exp']
    
    # dataframe containing the list of stimuli for the current subset
    df_stimuli = subject_data_list[subject_ind]['df_stimuli']
    
    # loop over stimuli
    for index, row in df_stimuli.iterrows():  
                    
        # loop over conditions
        for cond in conditions:
                        
            # path to the stimulus for the current condition
            file = os.path.join(data_dir, cond, row.wavfile)
            
            # add row to dataframe
            # we do not fill in session and first_scale for the moment
            df_subject_exp.loc[len(df_subject_exp)] = [subject_data_list[subject_ind]['subset_id'], 'x', file, 'x']
        
    # # shuffle rows
    df_subject_exp = df_subject_exp.sample(frac=1, random_state=SEED, ignore_index=True)
    
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
    
    # init dataframe
    df_subject_ref = pd.DataFrame(columns=['subset', 'session', 'file', 'first_scale'])
    
    # list of wav files for the reference conditions
    ref_file_list = glob(os.path.join(data_dir, ref_condition, '*.wav'))
    
    # shuffle file list
    random.shuffle(ref_file_list)
    
    # assign first scale
    if (subset == 1 or subset == 2):
        first_scale = first_scale = 'SIG'
    else:
        first_scale = first_scale = 'BAK'
    
    
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
    df_subject_all_scales.to_csv(os.path.join(output_dir, 'subject_' + str(subject_ind+1) + '.csv'))
        
    output_dir = os.path.join(config_dir, 'json')
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
        
    with open(os.path.join(output_dir,'subject_' + str(subject_ind+1) + '.json'), 'w') as f:
        json.dump(df_subject_all_scales.to_dict('records'), f, indent=1)
    
    