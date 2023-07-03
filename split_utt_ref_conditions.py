#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The reference conditions are described in [1] and are available 
at: https://github.com/microsoft/P.808/tree/master/p835_reference_conditions/3gpp_p501_FB.

They were created by concatenating two utterances. 
We will only keep the second one to reduce the audio duration from 8 s to 4 s, 
as the ITU-T P.835 recommendation mentions that 4 s is enough.

The time instant used to separate the two utterances in each speech sample is:

- f1: 3.65 s
- f2: 3.60 s
- m1: 3.30 s
- m2: 3.65 s

This script splits the original audio files of the reference conditions in two
separate utterances.

WARNING: The reference conditions should be further normalized to -30 LUFS for
the UDASE listening test. The script to perform this normalization is in the
py folder of the listening test repository.

[1] Naderi, Babak and Cutler, Ross, "Subjective Evaluation of Noise Suppression
 Algorithms in Crowdsourcing", Interspeech, 2021.

"""

import soundfile as sf
import numpy as np
import glob
import os
import librosa
import soundfile as sf

input_dir = '/data2/datasets/UDASE-CHiME2023/reference_conditions/UDASE-CHiME2023'
utt1_output_dir = os.path.join(input_dir, 'utt1')
utt2_output_dir = os.path.join(input_dir, 'utt2')

for p in [utt1_output_dir, utt2_output_dir]:
    if not os.path.isdir(p):
        os.makedirs(p)
    
src_file_list = glob.glob(os.path.join(input_dir, '*.wav'))

split_time = {'f1': 3.65,
              'f2': 3.60,
              'm1': 3.30,
              'm2': 3.65}

for file in src_file_list:
    
    x, sr = librosa.load(file, sr=16000, mono=True)
    
    spk = os.path.basename(file)[:-4].split('_')[1]
    split_ind = int(split_time[spk]*sr)
    
    x_1 = x[:split_ind]
    x_2 = x[split_ind:]
    
    sf.write(os.path.join(utt1_output_dir, os.path.basename(file)), x_1, sr, 
             'PCM_16')
    
    sf.write(os.path.join(utt2_output_dir, os.path.basename(file)), x_2, sr, 
             'PCM_16')
    