from subprocess import check_output
import numpy as np
import matplotlib.pyplot as plt

def bpms():
    f = open('bpms.txt')
    bpms = {}
    line = f.readline()
    while line != "" and line != "\n":
        k, v = line.strip().split(',')
        bpms[k] = float(v)
        line = f.readline()
    f.close()
    return bpms
    

bpms = bpms()

def get_event_histogram(release):
    release = str(release)
    events = check_output(["aubioonset", "-i", "../anjuna_symlinks/"+release, "-O", "kl"])
    events = [float(x) for x in events.split()]
    # We want to scan for 16ths: units of window are seconds per 16th note 
    window = 15.0 / bpms[release]
    # The first event should be exactly halfway through its window.
    x0 = events[0]
    events = [x - x0 + (window/2.0) for x in events]
    
    histogram = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    sum = 0
    
    for e in events:
        # Scale events into a 1 measure space
        scaled_e = e % (16.0 * window)
        # Find which bin this is in
        bin_e = int(scaled_e / window)
        histogram[bin_e] += 1
        sum += 1
    
    return histogram * 1.0 / sum
    
def plot_histogram(h):
    b = plt.bar(np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]), h, orientation='vertical')
    plt.show()
    
def ph(r):
    plot_histogram(get_event_histogram(r))
    
def find_errors():
    for k in bpms: 
        try:
            h = get_event_histogram(k)
        except:
            print k + " has formatting issues."