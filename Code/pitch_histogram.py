from aubio import freqtomidi
from subprocess import check_output
import numpy as np
import matplotlib.pyplot as plt

key_relations = {'C':0,
                 'C#':1, 'Db':1,
                 'D':2,
                 'D#':3, 'Eb':3,
                 'E':4,
                 'F':5,
                 'F#':6, 'Gb':6,
                 'G':7,
                 'G#':8, 'Ab':8,
                 'A':9,
                 'A#':10, 'Bb':10,
                 'B':11 }

def keys():
    f = open('keys.txt')
    keys = {}
    # Number of steps above C
    line = f.readline()
    while line != "" and line != "\n":
        k, v = line.strip().split(',')
        keys[k] = key_relations[v]
        line = f.readline()
    f.close()
    return keys

keys = keys()

def get_pitch_histogram(release):
    release = str(release)
    #pitches = check_output(["aubiopitch", "-i", "../anjuna_symlinks/"+release, "-u", "midi", "-p", "fcomb", "-B", "8192", "-H", "4048"])#orig 8k 4k, then 4k 1k, then 2k .5k.  4k 1k seemed best.
    pitches = check_output(["sonic-annotator", "-t", "./pitch.t", "../anjuna_symlinks/"+release, "-w", "csv", "--csv-stdout"])
    # pitches ( file ) --> pitches [ lines ]
    pitches = [x for x in pitches.split('\n')[1:] if x != ""]
    # --> float values (Hz)
    pitches = [float(x.split(',')[-1]) for x in pitches]
    # --> valid midi note numbers
    pitches = [round(freqtomidi(x)) for x in pitches if x >= 20.0]
    
    
    key = keys[release]
    # Subtract out the key's distance to C to force all to C
    # This is guaranteed to be positive since it is at least 15 - 11 = 4
    pitches = [x - key for x in pitches]
    
    histogram = np.array([0,0,0,0,0,0,0,0,0,0,0,0])
    sum = 0
    
    for p in pitches:
        # Scale pitches into 1 octave / fit into note name bins
        scaled_p = round(p) % 12.0
        histogram[scaled_p] += 1
        sum += 1
    
    return histogram * 1.0 / sum
    
def plot_histogram(h):
    b = plt.bar(np.array([0,1,2,3,4,5,6,7,8,9,10,11]), h, orientation='vertical')
    plt.show()
    
def ph(r):
    plot_histogram(get_pitch_histogram(r))
