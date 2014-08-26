import numpy as np
# precondition: vector has 16 + 12 + 13 + 13 elements
# returns a np array
def preprocess(vector):
    vector = np.array(vector)
    
    vector[0:16] *= 10  # Tatum frequencies
    vector[16:28] *= 10 # Pitch frequencies
    vector[28] /= 10.0  # First MFCC
    vector[41] /= 10.0  # First MFCC variance
    
    # Leave off MFCC variances
    vector = vector[0:41]
    
    return vector

def rhythm(vector):
    return vector[:16]

def pitch(vector):
    return vector[16:28]

def mfccs(vector):
    return vector[28:]
