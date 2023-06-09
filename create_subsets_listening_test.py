#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
From Léonie: Les locuteurs sont accessibles dans "words", le nombre de personnes qui parlent 
en même temps dans "num_spk" et le lieu dans "location". J'ai aussi ajouté les 
temps où x personnes parlent simultanément (0_spk_time, 1_spk_time, etc.) et 
le sexe des locuteurs (F, M ou FM).
"""

SEED = 0
import os
import json
import glob
import pandas as pd
import numpy as np
np.random.seed(SEED)
import random
random.seed(SEED)
import matplotlib.pyplot as plt
from collections import Counter
    

#%% parameters

# S01_P04_63.wav does not contain speech
# S01_P02_12.wav almost only contains laughings
samples_to_ignore = ['S01_P04_63_output.wav', 'S01_P02_12_output.wav']

# number of subsets
num_subsets = 4

# target number of samples (elements) in each subset
target_numel_per_subset = 32 # 58, 41, 32

VERBOSE = False

#%% dataframe with all samples

# path to the json file for the listening test
json_path = '/data/recherche/python/UDASE-CHiME2023/unlabeled_data/json_files/eval'
json_file_list = glob.glob(os.path.join(json_path, '*listening_test.json'))

list_columns_df = ['wavfile', 'duration', 'duration_0_spk', 
                    'duration_1_spk', 'duration_2_spk',
                    'duration_3_spk', 'n_spk', 'speakers', 'sex', 
                    'session', 'location', 'transcription']

# dataframe
df = pd.DataFrame(columns=list_columns_df)

for file in json_file_list:
    
    head, tail = os.path.split(file)
    session = tail[:3] # session ID
    ref_spk = tail[4:7] # ref speaker
    num_active_spk = tail[8:-5] # subfolder where the audio is saved (0, 1, 2, 3 or listening_test)
    split = os.path.basename(head) # train, dev or eval
    
    with open(file) as f:  
        data = json.load(f)
        
    for mix in data:
        
        wavfile = session + '_' + ref_spk + '_' + mix['mix'] + '_output.wav'
        
        if wavfile in samples_to_ignore:
            continue
        
        duration = '{:.2f}'.format(float(mix['duration']))
        
        duration_0_spk = '{:.2f}'.format(float(mix['0_spk_time']))
        duration_1_spk = '{:.2f}'.format(float(mix['1_spk_time']))
        duration_2_spk = '{:.2f}'.format(float(mix['2_spk_time']))
        duration_3_spk = '{:.2f}'.format(float(mix['3_spk_time']))
        
        n_spk = int(mix['num_spk'])
        
        transcription = mix['words']
        
        speakers = []
        for w in transcription.split(' '):
            if len(w)==5 and w[0]=='(' and w[1]=='P' and w[-1]==')':
                speakers.append(w[1:4])
        speakers = list(np.unique(speakers))
        speakers.sort()     
        
        speakers_list = ''
        for i, spk in enumerate(speakers):
            if i==0:
                speakers_list = speakers_list + spk
            else:
                speakers_list = speakers_list + ' ' + spk
        
        
        sex = mix['sex']
        
        location = mix['location']
        
        row = [wavfile, duration, duration_0_spk, duration_1_spk, 
               duration_2_spk, duration_3_spk, n_spk, speakers_list, sex, 
               session, location, transcription]
        
        df.loc[len(df)] = row
        
df.to_csv('samples_all.csv')


#%% split dataset into balanced subsets

# list of effects (sessions, locations, sex)
list_session = list(df['session'].unique())
list_sex = list(df['sex'].unique())
list_location = list(df['location'].unique())

# distribution of the effects in the orignal complete dataset and in the subsets
distribution_labels = []
distributions = {'original': [],
                 'subset_1': [],
                 'subset_2': [],
                 'subset_3': [],
                 'subset_4': []}


# list of dataframe for each subset
df_subsets = []
for i in range(num_subsets):
    df_subsets.append(pd.DataFrame(columns=list_columns_df))    


# total number of samples in the original dataset
total_numel = len(df)

for session in list_session:
    
    for location in list_location:
        
            for sex in list_sex:
                
                # label for the effects combination
                label = session + '_' + location  + '_' + sex
                distribution_labels.append(label)
                
                # select the samples in the original dataset that correspond
                # to this combination of the effects
                sub_df = df[(df['session']==session) & 
                           (df['location']==location) & 
                           (df['sex']==sex)]
                
                # total number of samples for this combination of effects in the
                # original dataset
                numel = len(sub_df)
                distributions['original'].append(round(numel/total_numel*100))
                
                # proportion of samples in the original dataset for this 
                # combination of effects
                proportion = numel/total_numel
                
                # number of samples to draw for each subset
                numel_to_sample = int(np.rint(target_numel_per_subset*proportion))
                
                # if the total number of samples (for all subsets) is greater than
                # the total number of samples in the original dataset, then 
                # decrement it
                if len(sub_df) < numel_to_sample*num_subsets and numel_to_sample > 1:
                    numel_to_sample -= 1
                
                # if we have enough samples in the original dataset
                if len(sub_df) >= numel_to_sample*num_subsets:
                    
                    # list of indices from 0 to 3, shuffled
                    subset_indices = list(range(num_subsets))
                    random.shuffle(subset_indices)
                    
                    # equivalent to selecting randomly a subset
                    for i in subset_indices:
                                    
                            # extract numel_to_sample samples from the original
                            # dataset (samples that fit the combination of effects)
                            df_subset = sub_df.sample(numel_to_sample, random_state=SEED)
                            
                            # add these samples to the subset
                            df_subsets[i] = pd.concat([df_subsets[i], df_subset])
                            
                            # remove the samples from the pool of available samples
                            sub_df = sub_df.drop(df_subset.index)
                            
                            
                            if VERBOSE:
                                print(len(sub_df))
                            
                else:
                    
                    print('not enough samples for ' + label + ': required %d, available %d' % (numel_to_sample*4, len(sub_df)))
                    
                if VERBOSE:
                    print(label)
                    print('... all: %d' % numel)
                
                for i, df_subset in enumerate(df_subsets):
                    
                    numel_subset = len(df_subset[(df_subset['session']==session) & 
                                               (df_subset['location']==location) & 
                                               (df_subset['sex']==sex)])
                    
                    distributions['subset_'+str(i+1)].append(numel_subset)
                    
                    if VERBOSE:
                        print('... subset %d: %d' % (i+1, numel_subset))
            

for i, df_subset in enumerate(df_subsets):
    distributions['subset_'+str(i+1)] = [round(x/len(df_subset)*100) for x in distributions['subset_'+str(i+1)]]
    df_subset.to_csv('samples_subset_'+str(i+1)+'.csv')
    
#%% check dataframes are different

for i in range(len(df_subsets)):
    for j in range(len(df_subsets)):
        
        if j==i: continue
        
        assert not np.any(df_subsets[i].isin(df_subsets[j]))

#%% plot distributions

plt.close('all')
fig, axs = plt.subplots(5,1)

for i, label in enumerate(list(distributions.keys())):

    axs[i].bar(distribution_labels, distributions[label])
    axs[i].set_title(label)
    axs[i].set_ylabel('prop. (\%)')
    if i < len(list(distributions.keys()))-1:
        axs[i].set_xticks([])
    
plt.xticks(rotation = 45)

#%% count conditions

data_labels = list(distributions.keys())

data = [df] + df_subsets

for i, label in enumerate(data_labels):

        print(label + ' - %d samples' % len(data[i]))

        c_session = Counter(data[i].session)
        c_location = Counter(data[i].location)
        c_sex = Counter(data[i].sex)
        
        cs = [c_session, c_location, c_sex]
        
        for c in cs:            
                print('...', end = '')
                print(dict(c))