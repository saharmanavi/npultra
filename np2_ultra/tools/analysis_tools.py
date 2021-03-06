import os
import json
import numpy as np
import shutil


def create_flags_txt(probe_data_dir, flag_text):
    """probe_data_dir is the path to the folder where the continuous.dat file is for the probe/recording
    flag_text is a dictionary with common keys 'skip_kilosort' and 'other_notes'"""

    flag_file = os.path.join(folder_loc, "flags.json")
    with open(flag_file, 'w') as t:
        json.dump(flag_text, t)

def check_flags_file(key, probe_data_dir, default_cond=False):
    condition = default_cond
    flags_file = os.path.join(probe_data_dir,'flags.json')
    if os.path.exists(flags_file):
        with open(flags_file, 'r') as f:
            flags = json.load(f)
            condition = flags[key]
    return condition

def fix_spike_times(spike_times_file_path, timestamps_file, probe_data_dir):
    spike_times = np.load(spike_times_file_path)
    if 'spike_times_old.npy' not in os.listdir(probe_data_dir):
        shutil.copy(spike_times_file_path, os.path.join(os.path.dirname(spike_times_file_path), 'spike_times_old.npy'))
        t0 = np.load(timestamps_file)[0]
        spike_times = spike_times + t0
        np.save(spike_times_file_path, spike_times)
    spike_times_old = np.load(os.path.join(probe_data_dir, 'spike_times_old.npy'))
    return spike_times, spike_times_old


def signaltonoise(a, axis=0, ddof=0):
    '''
    Created on Sat Sep 12 15:52:39 2020
    @author: svc_ccg
    '''
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)

def bootstrap_resample(X, n=None):
    """ Bootstrap resample an array.
    Sample with replacement.
    From analysis/sampling.py.
    Parameters
    ----------
    X : array_like
      data to resample
    n : int, optional
      length of resampled array, equal to len(X) if n==None
    Results
    -------
    returns X_resamples
    """
    if n == None:
        n = len(X)

    resample_i = np.floor(np.random.rand(n)*len(X)).astype(int)
    X_resample = X[resample_i]
    return X_resample

def getPSTH(spikes,startTimes,windowDur,binSize=0.01,avg=True):
    '''
    Created on Sat Sep 12 15:52:39 2020
    @author: svc_ccg
    '''
    bins = np.arange(0,windowDur+binSize,binSize)
    counts = np.zeros((len(startTimes),bins.size-1))
    for i,start in enumerate(startTimes):
        counts[i] = np.histogram(spikes[(spikes>=start) & (spikes<=start+windowDur)]-start,bins)[0]
    if avg:
        counts = counts.mean(axis=0)
    counts /= binSize
    t = bins[:-1]
    return counts,t

def get_sync_line_data(syncDataset, line_label=None, channel=None):
    ''' Get rising and falling edge times for a particular line from the sync h5 file

        Parameters
        ----------
        dataset: sync file dataset generated by sync.Dataset
        line_label: string specifying which line to read, if that line was labelled during acquisition
        channel: integer specifying which channel to read in line wasn't labelled

        Returns
        ----------
        rising: npy array with rising edge times for specified line
        falling: falling edge times
    '''
    if isinstance(line_label, str):
        try:
            channel = syncDataset.line_labels.index(line_label)
        except:
            print('Invalid line label')
            return
    elif channel is None:
        print('Must specify either line label or channel id')
        return

    sample_freq = syncDataset.meta_data['ni_daq']['counter_output_freq']
    rising = syncDataset.get_rising_edges(channel)/sample_freq
    falling = syncDataset.get_falling_edges(channel)/sample_freq

    return rising, falling
