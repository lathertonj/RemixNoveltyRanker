from subprocess import check_output
import numpy as np

def get_mfccs(release):
    release = str(release)
    mfccs = check_output(["aubiomfcc", "-i", "../anjuna_symlinks/"+release])
    mfccs = mfccs.strip().split('\n')
    
    # Discard the first element of each line; it's a timestamp
    mfccs = [x.split()[1:] for x in mfccs]
    mfccs = [[float(x) for x in group] for group in mfccs]

    # Discard the first MFCC as it relates to loudness? Keep for now.    
    
    # Discard entries that correspond to silence at beginning and end.
    # "Reasonable" values are [-30, -10] ish.  Silence usually is at -263.
    # -200 seems like a good boundary.
    i = 0
    while mfccs[i][0] < -200.0:
        i += 1
    j = len(mfccs) - 1;
    while mfccs[j][0] < -200.0:
        j -= 1
    mfccs = mfccs[i:j+1]
        
    sum = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    count = 0
    
    for group in mfccs:
        sum = sum + np.array(group)
        count += 1
    means = sum / count
    
    variances = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    # Loop instead of list comprehension because doubly nested list comprehension is confusing
    for i in range(13):
        variances[i] = np.var([group[i] for group in mfccs])
    
    return means, variances