#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to simulate data for developing the listening test software.
"""

import os
import numpy as np
import glob
import random 
import shutil

input_dir = '/data2/datasets/UDASE-CHiME2023/CHiME-5/eval'
output_dir = 'data'


n_conditions = 5
n_files = 232
n_spk = [1, 2, 3]
prop_per_spk_num = [0.5, 0.375, 0.125]

n_files_per_spk_num = []
n_files_per_spk_num.append(int(prop_per_spk_num[0]*n_files))
n_files_per_spk_num.append(int(prop_per_spk_num[1]*n_files))
n_files_per_spk_num.append(n_files - sum(n_files_per_spk_num))

for i, spk in enumerate(n_spk):

    src_file_list = glob.glob(os.path.join(input_dir, str(spk), '*.wav'))
    
    src_file_list = random.sample(src_file_list, k=n_files_per_spk_num[i])    

    for cond_ind in range(n_conditions):
         
        cond_path = os.path.join(output_dir, 'C' + str(cond_ind), str(spk))

        if not os.path.isdir(cond_path):
            os.makedirs(cond_path)
        
        for src_file in src_file_list:
            
            mix_id = os.path.basename(src_file)[:-4]
            dst_filename = mix_id + '_output.wav'
            dst_file = os.path.join(cond_path, dst_filename)
            
            shutil.copy(src_file, dst_file)
            
    