#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversion of linear to db scale for the slider in the volume adjustment
part of the listening test software.
"""

import numpy as np

def db_to_linear(x_db):
    
    x = 0.5*np.exp(np.log(10)/20*x_db)
    
    return x


def linear_to_db(x):
    
    x_db = 20*np.log(x/0.5)/np.log(10)
    
    return x_db

