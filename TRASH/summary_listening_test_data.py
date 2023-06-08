#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 10:27:07 2023

Les locuteurs sont accessibles dans "words", le nombre de personnes qui parlent 
en même temps dans "num_spk" et le lieu dans "location". J'ai aussi ajouté les 
temps où x personnes parlent simultanément (0_spk_time, 1_spk_time, etc.) et 
le sexe des locuteurs (F, M ou FM).
"""


import os
import json
import glob
import pandas as pd
import numpy as np
import random
from collections import Counter
import sys

json_path = '/data/recherche/python/UDASE-CHiME2023/unlabeled_data/json_files/eval'
json_file_list = glob.glob(os.path.join(json_path, '*listening_test.json'))

df = pd.DataFrame(columns=['wavfile', 'duration', 'duration_0_spk', 
                           'duration_1_spk', 'duration_2_spk',
                           'duration_3_spk', 'n_spk', 'speakers', 'sex', 
                           'session', 'location', 'transcription'])

for file in json_file_list:
    
    head, tail = os.path.split(file)
    session = tail[:3] # session ID
    ref_spk = tail[4:7] # ref speaker
    num_active_spk = tail[8:-5] # subfolder where the audio is saved (0, 1, 2, 3 or listening_test)
    split = os.path.basename(head) # train, dev or eval
    
    with open(file) as f:  
        data = json.load(f)
        
    for mix in data:
        
        wavfile = session + '_' + ref_spk + '_' + mix['mix'] + '.wav'
        
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
        
df.to_csv('listening_test_samples.csv')


#%% compute distribution

# list of effects
list_session = list(df['session'].unique())
list_sex = list(df['sex'].unique())
list_location = list(df['location'].unique())

# distribution of the effects in the orignal complete dataset and in the blocks
distribution_labels = []
distributions = {'original': [],
                 'block_1': [],
                 'block_2': [],
                 'block_3': [],
                 'block_4': []}

# number of blocks
num_blocks = 4

# list of dataframe for each block
df_blocks = []
for i in range(num_blocks):
    df_blocks.append(pd.DataFrame(columns=['wavfile', 'duration', 'duration_0_spk', 
                                           'duration_1_spk', 'duration_2_spk',
                                           'duration_3_spk', 'n_spk', 'speakers', 'sex', 
                                           'session', 'location', 'transcription']))    

# target number of samples in each block
target_numel_per_block = 58

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
                
                # number of samples to draw for each block
                numel_to_sample = int(np.rint(target_numel_per_block*proportion))
                
                # if the total number of samples (for all blocks) is greater than
                # the total number of samples in the original dataset, then 
                # decrement it
                if len(sub_df) < numel_to_sample*num_blocks and numel_to_sample > 1:
                    numel_to_sample -= 1
                
                # if we have enough samples in the original dataset
                if len(sub_df) >= numel_to_sample*num_blocks:
                    
                    # list of indices from 0 to 3, shuffled
                    block_indices = list(range(num_blocks))
                    random.shuffle(block_indices)
                    
                    # equivalent to selecting randomly a block
                    for i in block_indices:
                                    
                            # extract numel_to_sample samples from the original
                            # dataset (samples that fit the combination of effects)
                            df_subset = sub_df.sample(numel_to_sample)
                            
                            # add these samples to the block
                            df_blocks[i] = pd.concat([df_blocks[i], df_subset])
                            
                            # remove the samples from the pool of available samples
                            sub_df = sub_df.drop(df_subset.index)
                            
                            print(len(sub_df))
                            
                else:
                    
                    print('not enough samples for ' + label + ': required %d, available %d' % (numel_to_sample*4, len(sub_df)))
                    
                
                print(label)
                print('... all: %d' % numel)
                
                for i, df_block in enumerate(df_blocks):
                    
                    numel_block = len(df_block[(df_block['session']==session) & 
                                               (df_block['location']==location) & 
                                               (df_block['sex']==sex)])
                    
                    distributions['block_'+str(i+1)].append(numel_block)
                    
                    print('... block %d: %d' % (i+1, numel_block))
            

for i, df_block in enumerate(df_blocks):
    distributions['block_'+str(i+1)] = [round(x/len(df_block)*100) for x in distributions['block_'+str(i+1)]]

sys.exit()

#%% tree with speakers

from anytree import Node, RenderTree

from anytree.dotexport import RenderTreeGraph

import yaml
from anytree import AnyNode
from anytree.exporter import DictExporter
import json


list_session = list(df['session'].unique())
list_n_spk = list(df['n_spk'].unique())
list_sex = list(df['sex'].unique())
list_location = list(df['location'].unique())

nodes_session = []
nodes_location = []
nodes_n_spk = []
nodes_sex = []
nodes_speakers = []

node_dataset = Node('dataset')

for session in list_session:
    
    label = session
    
    node_session = Node(label, parent=node_dataset)
    
    nodes_session.append(node_session)
    
    for location in list_location:
        
        label = session + '_' + location
        
        node_location = Node(label, parent=node_session)
        
        nodes_location.append(node_location)
        
        for n_spk in list_n_spk:
            
            label = session + '_' + location + '_' + str(n_spk)
            
            node_n_spk = Node(label, parent=node_location)
            
            nodes_n_spk.append(node_n_spk)
            
            for sex in list_sex:
                
                label = session + '_' + location + '_' + str(n_spk) + '_' + sex
                
                node_sex = Node(label, parent=node_n_spk)
                
                nodes_sex.append(node_sex)
                
                sub_df = df[(df['session']==session) & 
                           (df['location']==location) & 
                           (df['n_spk']==n_spk) & 
                           (df['sex']==sex)]
                
                
                list_speakers = list(sub_df['speakers'].unique())
                
                for speakers in list_speakers:
                    
                    label = session + '_' + location + '_' + str(n_spk) + '_' + sex + '_' + speakers
                    
                    node_speakers = Node(label, parent = node_sex)
                    
                    nodes_speakers.append(node_speakers)
                    
                    sub_df = df[(df['session']==session) & 
                               (df['location']==location) & 
                               (df['n_spk']==n_spk) & 
                               (df['sex']==sex) & 
                               (df['speakers']==speakers)]
                    
                
                    for index, row in sub_df.iterrows():
                        
                        wavfile = row['wavfile']
                        node_wavfile = Node(wavfile, parent=node_speakers)
                    
dct = DictExporter().export(node_dataset)

with open('dataset.json', 'w') as file:
    json.dump(dct, file, indent=4)     
    
RenderTreeGraph(nodes_session[0]).to_picture("S01.svg")
RenderTreeGraph(nodes_session[1]).to_picture("S21.svg")


# print(RenderTree(node_dataset))

#%%



list_session = list(df['session'].unique())
list_n_spk = list(df['n_spk'].unique())
list_sex = list(df['sex'].unique())
list_location = list(df['location'].unique())

nodes_session = []
nodes_location = []
nodes_n_spk = []
nodes_sex = []
nodes_speakers = []

node_dataset = Node('dataset')

conditions = {'name':[], 'num_el':[]}

for session in list_session:
    
    label = session
    
    node_session = Node(label, parent=node_dataset)
    
    nodes_session.append(node_session)
    
    for location in list_location:
        
        label = session + '_' + location
        
        node_location = Node(label, parent=node_session)
        
        nodes_location.append(node_location)

        for sex in list_sex:
            
            label = session + '_' + location  + '_' + sex
            
            node_sex = Node(label, parent=node_location)
            
            nodes_sex.append(node_sex)
            
            sub_df = df[(df['session']==session) & 
                       (df['location']==location) & 
                       (df['sex']==sex)]
            
            conditions['name'].append(node_sex.name)
            conditions['num_el'].append(len(sub_df))
            
            for index, row in sub_df.iterrows():
                
                wavfile = row['wavfile']
                node_wavfile = Node(wavfile, parent=node_sex)
                    
dct = DictExporter().export(node_dataset)

with open('dataset.json', 'w') as file:
    json.dump(dct, file, indent=4)     
    
RenderTreeGraph(nodes_session[0]).to_picture("S01.svg")
RenderTreeGraph(nodes_session[1]).to_picture("S21.svg")


#%%

import matplotlib.pyplot as plt

plt.close('all')
plt.bar(conditions['name'], conditions['num_el'])
plt.xticks(rotation=30)

#%%

with open('dataset.json', 'r') as file:

    dataset_dict = json.load(file)