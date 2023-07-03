#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check the distribution of the data after manually discarding some samples.
Samples to discard are labeled as 'C' or 'D' in metadata/samples_manual_annotations.csv
"""


import os
import pandas as pd
import json
import glob
import numpy as np
from collections import Counter

#%% dataframe with all samples

# path to the json file for the listening test
json_path = '/data/recherche/python/UDASE-CHiME2023/unlabeled_data/json_files/eval'
json_file_list = glob.glob(os.path.join(json_path, '*listening_test.json'))
json_file_list.sort()

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

df = df.sort_values(by=['wavfile'])

#%% remove samples rated as 'C'

df_annot = pd.read_csv('metadata/samples_manual_annotations.csv')

for index, row in df_annot.iterrows():
        
    df_annot.iloc[index]['wavfile'] = os.path.basename(df_annot.iloc[index]['wavfile'])
    
files_to_remove = list(df_annot[(df_annot['rating']=='C') | (df_annot['rating']=='D')]['wavfile'])


for index, row in df.iterrows():
    
    wavfile = row['wavfile']
    
    if wavfile in files_to_remove:
        
        df = df.drop(index)
        
#%% compute stats

c_session = Counter(df.session)
c_location = Counter(df.location)
c_sex = Counter(df.sex)

cs = [c_session, c_location, c_sex]

for c in cs:            
        print('...', end = '')
        print(dict(c))


    