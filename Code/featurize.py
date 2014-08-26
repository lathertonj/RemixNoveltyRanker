import os.path
import pitch_histogram
import mfccs
import event_histogram

file = './features.csv'

def featurize(releases):
    releases = [str(x) for x in releases]
    if not os.path.isfile(file):
        features = open(file, 'a')
        features.write('release,tatum_distribution,pitch_distribution,mel_frequency_cepstrum_coefficients\n')
    else:
        features = open(file, 'a')
    for release in releases:
        try:
            result = [release]
            result += [float(x) for x in list(event_histogram.get_event_histogram(release))]
            result += [float(x) for x in list(pitch_histogram.get_pitch_histogram(release))]
            mfs = mfccs.get_mfccs(release)
            mfs = list(mfs[0]) + list(mfs[1])
            result += [float(x) for x in mfs]
    
            line = ','.join([str(x) for x in result]) + '\n'
    
            features.write(line)
        except:
            features.write(release + " failed featurization\n")
    
    features.close()
    
to_run_on = pitch_histogram.keys.keys()
to_run_on = [float(x) for x in to_run_on]
to_run_on.sort()
to_run_on = [str(x) for x in to_run_on]