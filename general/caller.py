'''
Created on 18.12.2014

@author: Jaakko Leppakangas
'''
from singleton import Singleton
from wx import PyDeadObjectError
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
from threading import Thread, Event
import copy

import mne
from mne.preprocessing import find_eog_events
from mne.time_frequency import compute_raw_psd
from mne.viz import iter_topography

@Singleton
class Caller():
    raw = None
    groups = dict()
    keyMap = dict()
    e = Event()
    e2 = Event()
    result = None

    def __init__(self):
        print 'Caller created'
        
    def setRaw(self, raw, parent, preload=True):
        """
        Sets the raw data file. 
        Parameters:
        raw     - Raw file name
        preload - Preload data into memory for data manipulation and faster
                  indexing.
        """
        self.e.clear()
        self.result = None
        self.thread = Thread(target = self._setRaw, args=(raw, preload))
        self.thread.start()
        while not (self.e.is_set()):
            sleep(0.5)
            parent.updateUi()
            if self.e.is_set(): break
        if self.result:
            raise Exception(self.result)
        self.e.clear()
        
    def _setRaw(self, raw, preload=True):
        """
        """
        try:
            self.raw = mne.io.Raw(raw, preload=preload)
        except Exception as e:
            self.result = e
            self.e.set()
        self.e.set()

    def findEogEvents(self, params):
        """
        Finds events for the given id.
        Parameters:
        params - A dictionary of parameters for finding the events.
        """
        #eog_events = find_eog_events(raw, event_id=params['event_id'], ch_name=params['ch_name'], 
        #                            verbose=True, tstart=params['tstart'])
        try:
            print type(params['event_id'])
            eog_events = find_eog_events(self.raw, event_id=params['event_id'],
                        l_freq=params['l_freq'], h_freq=params['h_freq'],
                        filter_length=params['filter_length'],
                        ch_name=params['ch_name'], verbose=True,
                        tstart=params['tstart'])
        except Exception as e:
            print "Exception while finding events.\n"
            print str(e)
            return []
        return eog_events
    
    def plotAverageEpochs(self, events, tmin, tmax, event_id):
        """
        Method for plotting average epochs.
        """
        print "Plotting averages...\n"
        try:
            print event_id
            eog_epochs = mne.Epochs(self.raw, events, event_id=event_id,
                                tmin=tmin, tmax=tmax)
        except Exception as e:
            print "Could not create epochs.\n"
            print str(e)
            return
        
        # Average EOG epochs
        eog_evoked = eog_epochs.average()
        try:
            eog_evoked.plot()
        except PyDeadObjectError:
            #For PyDeadObjectError bug:
            pass
        print "Finished\n"
        
    def plotEvents(self, events):
        """
        Method for plotting the event locations in mne_browse_raw.
        Parameters:
        events - A list of events
        """
        print "Plotting events...\n"
        try:
            self.raw.plot(events=events, scalings=dict(eeg=40e-6))
            plt.show()
        except Exception as e:
            print "Exception while plotting events."
            print str(e)
        print "Finished"
    
    def computeSspProj(self, events, tmin, tmax, event_id, n_eeg):
        """
        Computes SSP projection vectors and adds them to the raw data.
        Parameters:
        events    - A list of events for creating the epochs.
        tmin      - Starting time before event for the epochs.
        tmax      - Ending time after the event for the epochs.
        event_id  - The id of the event to consider.
        n_eeg     - The number of vectors for EEG channels.
        """
        # Extract EOG epochs from raw data
        try:
            eog_epochs = mne.Epochs(self.raw, events, event_id=event_id,
                                tmin=tmin, tmax=tmax)
        except Exception as e:
            print "Could not create epochs.\n"
            print str(e)
            return []
        
        # Average EOG epochs
        try:
            eog_evoked = eog_epochs.average()
        
            # Compute SSPs
            proj = mne.compute_proj_evoked(eog_evoked, n_eeg=n_eeg)
            self.raw.add_proj(proj)
        except Exception as e:
            print "Error while computing projections.\n"
            print str(e)
            return []
        return proj
        # Check the effect of the SSPs on the raw data
        #self.raw.plot(events=events, scalings=dict(eeg=40e-6), show_options=True)
        #plt.show()

    def computePowerSpectrum(self, times, fmin, fmax, nfft, logarithm=True):
        """
        Computes power spectral densities for given data.
        Parameters:
        times       - A list of tuples indicating the start and end points for 
                      the trial.
        fmin        - Lower limit for the frequencies.
        fmax        - Higher limit for the frequencies.    
        n_fft       - Length of the tapers (ie. windows).
        logarithm   - A boolean to indicate if logarithmic scale is to be used.
        """
        picks = mne.pick_types(self.raw.info, meg=False, eeg=True,
                                    exclude=[])
        # If no eeg channels found, use all channels.
        if picks == []:
            picks = None
        psdList = []    
        for time in times:
            try:
                self.e2.clear()
                psds, freqs = compute_raw_psd(self.raw, tmin=time[0], tmax=time[1], 
                              fmin=fmin, fmax=fmax, n_fft=nfft, 
                              picks=picks, proj=True, verbose=True)
                self.e2.set()
            except Exception as e:
                self.e2.set()
                print str(e)
                return
            if logarithm:
                psds = 10 * np.log10(psds)
            psdList.append((psds, freqs))

        return psdList
    
    def plotSpectrum(self, parent, params, colors, channelColors, path=""):
        """
        Method for plotting the power spectral densities.
        Parameters:
        parent        - Parent dialog.
        params        - A set of parameters for calculating psds as dictionary.
        colors        - Color for each condition as a list.
        channelColors - A list of tuples indicating color for selected
                        channels.
        path          - A path for saving the images. If left empty, the psds
                        will be plotted to the screen.
        """
        try:
            lout = mne.layouts.read_layout(params['lout'], 
                                           scale=True)
        except Exception:
            raise Exception("Could not read layout file.")
        #self.computeSpectrum(params)
        if path == "":
            self.e.clear()
            self.e2.set()
            self.thread = Thread(target = self.computeSpectrum, args=(params,))
            self.thread.start()
            while not (self.e.is_set()):
                sleep(0.5)
                if self.e2.is_set():
                    parent.updateUi()
                if self.e.is_set(): break
            self.e.clear()
        else:
            self.computeSpectrum(params)
        
        if self.psds == []: return
        
        print "Plotting power spectrum..."
        parent.updateUi()
        
        def my_callback(ax, ch_idx):
            """
            Callback for the interactive plot.
            Opens a channel specific plot.
            """
            for i in xrange(len(self.psds)):
                color = colors[i]
                ax.plot(self.psds[i][1], self.psds[i][0][ch_idx], color=color)
            plt.xlabel('Frequency (Hz)')
            if params['log']:
                plt.ylabel('Power (dB)')
            else:
                plt.ylabel('(uV)')
            plt.show()
           
        # draw topography
        indices = []
        for ax, idx in iter_topography(self.raw.info,
                            fig_facecolor='white', axis_spinecolor='white', 
                            axis_facecolor='white', layout=lout, 
                            on_pick=my_callback):
            for i in xrange(len(self.psds)):
                channel = self.raw.info['ch_names'][idx]
                if (channel in channelColors[i][1]):
                    ax.plot(self.psds[i][0][idx], 
                            color=channelColors[i][0], linewidth=0.2)
                    indices.append(idx)
                else:
                    ax.plot(self.psds[i][0][idx], color=colors[i],
                            linewidth=0.2)
        indices = list(set(indices)) # Remove duplicates
        if path == "":
            print "Saving ASCII file.\n"
            fName = self.raw.info['filename']
            fName = fName.rsplit('.', 1)[0]
            #path = fName.rsplit('/', 1)[0]
            #fName = fName.rsplit('/', 1)[1]
            for cond in xrange(len(self.psds)):
                print "Writing file " + fName + '_cond' + str(cond+1) + '.txt'
                f = open (fName + '_cond' + str(cond+1) + '.txt', 'w')
                f.write('Hz;')
                for i in self.psds[cond][1]:
                    f.write(repr(i) + ';')
                f.write('\n')
                for i in indices:
                    f.write(repr(self.raw.info['ch_names'][i]) + '; ')
                    for j in self.psds[cond][0][i]:
                        f.write(repr(j) + '; ')
                    f.write('\n')
                f.close()
            plt.show()
        else:
            print "Saving image...\n"
            fName = self.raw.info['filename']
            fName = fName.rsplit('.', 1)[0]
            fName = fName.rsplit('/', 1)[1]
            
            plt.gcf().suptitle(fName)
            
            try:
                form = params['format']
                plt.savefig(path +'/'+ fName + "_topo." + form,
                            dpi=params['dpi'], format=form)
            except Exception as e:
                plt.close()
                raise(e)
                return
            print "Saving ASCII file.\n"
            if not self.groups.has_key('conds'):
                self.groups['conds'] = dict()
            for cond in xrange(len(self.psds)):
                if not self.groups['conds'].has_key(cond):
                    self.groups['conds'][cond] = dict()
                f = open (path + '/' + fName + '_cond' + str(cond+1) \
                          + '.txt', 'w')
                f.write('Hz;')
                for i in self.psds[cond][1]:
                    f.write(repr(i) + ';')
                f.write('\n')
                for i in xrange(len(self.psds[cond][0])):
                    if params['groupAverage']:
                        #Group averages:
                        if self.groups.has_key('freqs'):
                            pass
                            #print self.psds[cond][1][i]
                            #self.groups['freqs'].append(self.\
                            #                            psds[cond][1][i])
                        else:
                            #self.groups['freqs'] = []
                            self.groups['freqs'] = copy.deepcopy(self.\
                                                        psds[cond][1])
                        #groupName = 'ch' + self.raw.info['ch_names'][i]# + '_cond' + str(cond+1)
                        if self.groups['conds'][cond].has_key(i): #ChannelGroup exists
                            self.groups['conds'][cond][i].append(self.\
                                                      psds[cond][0][i])
                        else: #Create new entry to dictionary
                            #self.keyMap[i] = 'ch' + self.raw.info['ch_names'][i]
                            #self.keyMap[i] = groupName
                            self.keyMap[i] = self.raw.info['ch_names'][i]
                            self.groups['conds'][cond][i] = []
                            #self.groups['conds'][cond][i].append(self.\
                            #                          psds[cond][0][i])
                            arr = []
                            for j in self.psds[cond][0][i]:
                                arr.append(j)
                            self.groups['conds'][cond][i] = [np.array(arr)]
                            #self.groups['conds'][cond][i] = copy.deepcopy(self.psds[cond][0][i])
                            
                    if i in indices:
                        if params['plotChannels']:
                            print "Plotting individual channels..."
                            pos = lout.pos.copy()
                            ax = plt.axes(pos[i])
                            chFName = path + '/' + fName + '_cond' + \
                                        str(cond+1) + '_channel' + \
                                        self.raw.info['ch_names'][i] + \
                                        '.' + params['format']
                            self.plotChannelPsds(i, chFName, channelColors,
                                            params['format'], params['dpi'],
                                            params['log'])
                        f.write(repr(self.raw.info['ch_names'][i]) + '; ')
                        
                        for j in self.psds[cond][0][i]:
                            f.write(repr(j) + '; ')
                        f.write('\n')
                    parent.updateUi()
        
                f.close()
        plt.close() 
        print "Finished"
        
    def createGroupAverage(self, path, colors, channelColors, form, dpi, log, layout):
        """
        Computes mean average from values stored in array 'groups'.
        Parameters:
        path - The path for the file to save.
        form - A format for the images ('png', 'pdf', 'svg').
        dpi  - Resolution for the images.
        log  - Boolean to indicate if logarithmic scale is in use.
        """        
        try:
            print len(self.groups['conds'][0][0])
            f = open(path + '/group_average.txt', 'w')
            f.write('freq;')
            for i in self.groups['freqs']:
                f.write(repr(i) + '; ')
            f.write('\n')

            for cond in self.groups['conds'].keys():
                #plt.clf()
                #if k == 'freqs': continue
                for k in self.groups['conds'][cond].keys():
                    f.write(repr(self.keyMap[k]) + 'cond_' + str(cond+1) + '; ')
                    mean = np.mean(self.groups['conds'][cond][k], 0)
                    for j in mean:
                        f.write(repr(j) + '; ')
                    f.write('\n')
                #overwrites the groups for plotting
                    self.groups['conds'][cond][k] = mean

            """
                plt.plot(self.groups['freqs'], mean)
                plt.xlabel('Frequency (Hz)')
                if log:
                    plt.ylabel('Power (dB)')
                else: 
                    plt.ylabel('(uV)')
                plt.savefig(path + '/average_channel_' + k, format=form,
                            dpi=dpi)
                plt.close()
            """
        except Exception as e:
            print 'Error while writing group averages!'
            print str(e)
        finally:
            f.close()
        print len(self.groups['conds'][0][0])
        lout = mne.layouts.read_layout(layout, scale=True)
        def my_callback(ax, ch_idx):
            #i = self.keyMap[ch_idx]
            for cond in self.groups['conds'].keys():
                ax.plot(np.array(self.groups['freqs']), self.groups['conds'][cond][ch_idx], color=colors[cond])
            ax.set_xlabel='Frequency (Hz)'
            ax.set_ylabel='Power (dB)'
            plt.show()
        plt.clf()
        for ax, idx in iter_topography(self.raw.info, fig_facecolor='white',
                           axis_spinecolor='white', axis_facecolor='white',
                           layout=lout, on_pick=my_callback):
            i = self.keyMap[idx]
            print idx
            print i
            for cond in self.groups['conds'].keys():
                if (self.keyMap[idx] in channelColors[cond][1]):
                    color = channelColors[cond][0]
                else:
                    color = colors[cond]
                ax.plot(self.groups['conds'][cond][idx], color=color, linewidth=0.2)
        
        plt.show()
        self.keyMap.clear()
        self.groups.clear()
        
    def plotChannelPsds(self, ch_idx, fName, chColors, form, dpi, log):
        """
        Method for saving an image of channel specific psds.
        Parameters:
        ch_idx    - Index of the selected channel.
        fName     - File name for the image.
        chColors  - List of colors for the channels.
        form      - Image file format.
        log       - Boolean to indicate if logarithmic scale is in use.
        """
        plt.clf()
        for i in xrange(len(self.psds)):
            plt.plot(self.psds[i][1], self.psds[i][0][ch_idx],
                     color=chColors[i][0])
        plt.xlabel('Frequency (Hz)')
        if log:
            plt.ylabel('Power (dB)')
        else: 
            plt.ylabel('(uV)')
        plt.savefig(fName, dpi=dpi, format=form)
        
    def computeSpectrum(self, params):
        """
        Method for computing the power spectrum.
        Performed in a worker thread.
        Parameters:
        params - A dictionary of parameters for computing psds.
        """
        try:
            self.psds = self.computePowerSpectrum(params['times'],
                                                  params['fmin'],
                                                  params['fmax'], 
                                                  params['nfft'],
                                                  params['log'])
        except Exception as e:
            print "Exception while computing power spectrum.\n"
            print str(e)
            self.e.set()
            return
        print "Done"
        self.e.set()
        
    def clearGroups(self):
        self.keyMap.clear()
        self.groups.clear()
        