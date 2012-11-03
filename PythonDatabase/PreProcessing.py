# -*- coding: utf-8 -*-
"""
Created on Thu Nov 01 12:19:20 2012

@author: Brian
"""

import numpy as np


def wavefilter(data, maxlevel = 6):
    """
    This function requires that the NumPy and PyWavelet packages
    are installed. They are freely available at:
        
        NumPy - http://numpy.scipy.org/
        PyWavelets - http://www.pybytes.com/pywavelets/#download
        from the command line'easy_install PyWavelets' seems to do the trick
                    
        
    Filter a multi-channel signal using wavelet filtering.
	
    data     - n x m array, n=number of channels in the signal, 
				m=number of samples in the signal
    maxlevel - the level of decomposition to perform on the data. This integer
				implicitly defines the cutoff frequency of the filter.
				Specifically, cutoff frequency = samplingrate/(2^(maxlevel+1))
    """
	

    import pywt
    # We will use the Daubechies(4) wavelet
    wname = "db4"
    data = np.atleast_2d(data)
    numwires, datalength = data.shape

    # Initialize the container for the filtered data
    fdata = np.empty((numwires, datalength))
    for i in range(numwires):
        # Decompose the signal
        print 'processing data, please wait ... '
        
        c = pywt.wavedec(data[i,:], wname, level=maxlevel)

        # Destroy the approximation coefficients
        c[0][:] = 0
        # Reconstruct the signal and save it
        fdata[i,:] = pywt.waverec(c, wname)
        
    if fdata.shape[0] == 1:
        return fdata.ravel() # If the signal is 1D, return a 1D array
    else:
        return fdata # Otherwise, give back the 2D array