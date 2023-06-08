#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to normalize audio files to -30 LUFS.
"""

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import os
import glob
import warnings
warnings.filterwarnings("ignore")

def normalize(x, target_loudness=-30, clipping_threshold=1.0, meter=None, 
                   sr=16000):
    """
    LUFS normalization of a signal using pyloudnorm.
    
    Parameters
    ----------
    x : ndarray
        Input signal.
    target_loudness : float, optional
        Target loudness of the output in dB LUFS. The default is -30.
    clipping_threshold : float, optional
        Value above which the normalized signal is considered as clipping. 
        The default is 1.0.
    meter : Meter, optional
        The pyloudnorm BS.1770 meter. The default is None.
    sr : int, optional
        Sampling rate. The default is 16000.

    Returns
    -------
    x_norm : ndarray
        Normalized output signal.
    is_clipping : bool
        Boolean indicating if the signal clips after normalization.
    """
    
    if meter is None:
        meter = pyln.Meter(sr) # create BS.1770 meter
    
    # peak normalize to 0.7 to ensure that the meter does not return -inf
    x = x/np.max(np.abs(x))*0.7 
            
    # measure the loudness first 
    loudness = meter.integrated_loudness(x)
    
    # loudness normalize audio to target_loudness LUFS
    x_norm = pyln.normalize.loudness(x, loudness, target_loudness)  
    
    # check if clipping
    is_clipping = np.max(np.abs(x_norm)) >= clipping_threshold
    
    return x_norm, is_clipping

#%%
    
target_loudness = -30.0 # target LUFS
clipping_threshold = 1.0 # magnitude threshold to decide if a signal clips
sr = 16000 # sampling rate
meter = pyln.Meter(sr) # create BS.1770 meter

input_dir = '/data/recherche/python/UDASE-CHiME2023/listening-test-config/data/C0_unnormalized'
output_dir = '/data/recherche/python/UDASE-CHiME2023/listening-test-config/data/C0'

src_file_list = glob.glob(os.path.join(input_dir, '*.wav'), recursive=True)

for file in src_file_list:
    
    x, sr = sf.read(file)
    
    x_norm, _ = normalize(x, target_loudness=target_loudness, 
                          clipping_threshold=clipping_threshold,
                          meter=meter,sr=sr)
    
    # output_file = file.split('/')
    # output_file[0] = output_dir
    # output_file = os.path.join(*output_file)
    
    
    output_file = os.path.join(output_dir, os.path.basename(file))
    
    
    if not os.path.isdir(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    
    sf.write(output_file, x_norm, sr, 'PCM_16')


