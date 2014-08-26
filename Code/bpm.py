from subprocess import check_output
from event_histogram import bpms
import numpy as np

def get_bpm(release, num_beats=4):
    release = str(release)
    beats = check_output(["aubiotrack", "-i", "../anjuna_symlinks/"+release, "-B", "1024", "-H", "512"])
    beats = beats.split()
    return round(60.0 * num_beats / (float(beats[num_beats]) - float(beats[0])))

def check_bpms(num_beats=128):
    differences = {}
    for release in bpms:
        correct = bpms[release]
        test = get_bpm(release, num_beats)
        differences[release] = (correct - test)
        print release, '\t', correct, '\t', test, '\t', differences[release]
    print np.mean(differences.values())
    print np.mean(map(abs, differences.values()))
    print np.std(differences.values())
