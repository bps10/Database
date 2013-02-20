import numpy as np


def wavefilter(data, maxlevel = 6):
    """
    This function requires that the NumPy and PyWavelet packages
    are installed. They are freely available at:
        
        NumPy - http://numpy.scipy.org/
        PyWavelets - http://www.pybytes.com/pywavelets/#download
        from the command line'easy_install PyWavelets' seems to do the trick
                    
        
    Filter a multi-channel signal using wavelet filtering.
	
    :params data: n x m array, \
                    n=number of channels in the signal, \
                    m=number of samples in the signal 
    :params maxlevel: the level of decomposition to perform on the data. This \
                        integer implicitly defines the cutoff frequency of the \ 
                        filter. Specifically, \
                        cutoff frequency = samplingrate/(2^(maxlevel+1))
                        
    :returns: filtered data in same shape as input data
    
    
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
        
def spikeThreshold(bits, option = 0):
    """
    
    A very simple routine for finding the start and end of a spike
    
    :param bits: a thresholded spike train. This should be bianary.
    :type bits: np.array
    :param option: decide wether to return the spike beginnings and endings in \
                    the same array (option = 0) or seperately (option = 1)
    
    
    """
    
    # make sure all runs of ones are well-bounded
    bounded = np.hstack(([0], bits, [0]))
    # get 1 at run starts and -1 at run ends
    difs = np.diff(bounded)
    run_starts = difs > 0
    run_ends = difs < 0

     
    if option == 0:
        return run_starts + run_ends
    if option == 1:
        return run_starts, run_ends