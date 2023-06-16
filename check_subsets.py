#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check the audio samples in the different subsets
"""

import os
import pandas as pd
import json
import glob
import numpy as np
import shutil
from collections import Counter
import soundfile as sf
import pyloudnorm as pyln


def check_loudness(wav_file):
    
    x, _ = sf.read(wav_file)
    loudness = meter.integrated_loudness(x)
    
    return np.isclose(loudness, -30.0, rtol=0.5)
    

sr = 16000
meter = pyln.Meter(sr) # create loudness meter


audio_input_dir = 'data/C0'


for subject in range(4):
    
    csv_file = 'metadata/samples_subset_' + str(subject+1) + '.csv'
    
    df = pd.read_csv(csv_file)
    
    audio_output_dir = os.path.join('/data/tmp/subset_' + str(subject+1))
       
    if not os.path.isdir(audio_output_dir):
        os.makedirs(audio_output_dir)
    
    for index, row in df.iterrows():
        
        wavfile = row['wavfile']
        
        src = os.path.join(audio_input_dir, wavfile)
        dst = os.path.join(audio_output_dir, wavfile)
        
        shutil.copy(src, dst)
        
        assert check_loudness(dst)
        
        
        
    
    