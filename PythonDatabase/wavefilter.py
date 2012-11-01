# Python code for wavelet filtering.
# Information on the Python language - http://www.python.org/

def wavefilter(data, maxlevel = 6):
	"""
	This function requires that the NumPy and PyWavelet packages
	are installed. They are freely available at:
	
	NumPy - http://numpy.scipy.org/
	PyWavelets - http://www.pybytes.com/pywavelets/#download
	
	Filter a multi-channel signal using wavelet filtering.
	
	data     - n x m array, n=number of channels in the signal, 
				m=number of samples in the signal
	maxlevel - the level of decomposition to perform on the data. This integer
				implicitly defines the cutoff frequency of the filter.
				Specifically, cutoff frequency = samplingrate/(2^(maxlevel+1))
	"""
	
	import numpy as N
	import pywt
	
	# We will use the Daubechies(4) wavelet
	wname = "db4"
	
	data = N.atleast_2d(data)
	numwires, datalength = data.shape
	
	# Initialize the container for the filtered data
	fdata = N.empty((numwires, datalength))
	
	for i in range(numwires):
		# Decompose the signal
		c = pywt.wavedec(data[i,:], wname, level=maxlevel)
		# Destroy the approximation coefficients
		c[0][:] = 0
		# Reconstruct the signal and save it
		fdata[i,:] = pywt.waverec(c, wname)
		
	if fdata.shape[0] == 1:
		return fdata.ravel() # If the signal is 1D, return a 1D array
	else:
		return fdata # Otherwise, give back the 2D array