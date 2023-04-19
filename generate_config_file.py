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
data_dir = 'data'

# list of conditions
conditions = [os.path.basename(x) for x in glob(data_dir + '/*', recursive = True)]

# unprocessed condition
unprocessed_condition = 'C0'

#%%

n_subsets = 4 # a listening test is splitted into n_subsets subtests/subsets
n_subjects_per_subset = 8 # number of participants per subset
n_sessions = 4 # each subset is made of n_sessions listening sessions
n_split = n_subsets*n_sessions # total number of splits

df_stimuli = pd.DataFrame(columns=['subset', 'session', 'identifier', 'num_spk', 
                                   'first_scale', 'subjects'])    

# loop over the data subsets defined by the number of simultaneously-active speakers
for n_spk in [1, 2, 3]:
    
    # get list of stimuli with at most n_spk speakers
    # we assume that the stimuli for all conditions have the same wav file 
    # names (the reference is the unprocessed condition)
    pathpattern = os.path.join(data_dir, unprocessed_condition, str(n_spk)+'/*.wav')
    stim_list = [os.path.basename(x)[:-4] for x in glob(pathpattern)]
    
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
            row = [subset_ind, session_ind, stim, n_spk, first_scale, subjects]
            df_stimuli.loc[len(df_stimuli)] = row

# sort dataframe
df_stimuli = df_stimuli.sort_values(by=['subset', 'num_spk'])

# save to csv and json
df_stimuli.to_csv('config.csv')
df_stimuli.to_json('config.json', orient='records', indent=1)

#%% print summary

summary = []

for subset in np.arange(n_subsets):
    
    df_subset = df_stimuli[df_stimuli['subset'] == subset]
    
    print('subset: %d' % (subset+1))
    
    for n_spk in [1, 2, 3]:
        
        print('...n_spk: %d' % n_spk)
        
        print('............... %d' % len(df_stimuli[(df_stimuli['subset'] == subset+1) & (df_stimuli['num_spk'] == n_spk)]))
    
    print('number of stimuli: %d\n' % len(df_stimuli[(df_stimuli['subset'] == subset+1)]))