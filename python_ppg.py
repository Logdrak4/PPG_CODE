
import cv2

import numpy as np
import sys
import csv
import json
from scipy.signal.windows import hann
from scipy.signal import detrend, filtfilt, butter, find_peaks, welch

from scipy.stats import median_abs_deviation


#can use environemnt variables to pass information, command line, or csv files

# Section 1.1
# Video import
videoName = r'C:\Users\drake\OneDrive - clarkson.edu\PPG_Research\videos\Oct21_Logan01.mp4'
# Use this to pass filename as an argument
# videoName = sys.argv[1]

# Section 2.1
# Video processing
videoInput = cv2.VideoCapture(videoName)

# Video properties
videoHeight = int(videoInput.get(cv2.CAP_PROP_FRAME_HEIGHT))
videoWidth = int(videoInput.get(cv2.CAP_PROP_FRAME_WIDTH))
videoFrameRate = videoInput.get(cv2.CAP_PROP_FPS)
numFrames = int(videoInput.get(cv2.CAP_PROP_FRAME_COUNT))

# Creating variables to store total intensities
totalRed = np.zeros(numFrames)
totalBlue = np.zeros(numFrames)

# Loop through each frame in the video
for k in range(numFrames):
    ret, frame = videoInput.read()
    if not ret:
        break

    # Extract red and blue channels
    redValues = frame[:, :, 2].flatten()  # Red channel
    blueValues = frame[:, :, 0].flatten()  # Blue channel

    # Summing red and blue pixel values
    totalRed[k] = np.sum(redValues)
    totalBlue[k] = np.sum(blueValues)

# Close video file
videoInput.release()


# export the red signal as a csv file
# with open('red_signal.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerows(totalRed)
# print("Signal saved to raw_red_signal.csv")

# export the red signal as a json file
totalRed_json = totalRed.tolist()
with open('red_signal.json', 'w') as f:
    json.dump(totalRed_json, f)
print("Signal saved to raw_red_signal.json")

# Detrend the data
detrendRed = detrend(totalRed)
detrendBlue = detrend(totalBlue)

# Section 3.1
# Filtering and Noise Reduction

# Define bounds to clean PPG signal (cut off the first and last parts)
farLeft = int(numFrames * 0.2)
farRight = int(numFrames * 0.9)

# Moving average filter of order L
L = 8
b = np.ones(L-1)
a = 1

# Apply filter to red channel
totalRed_clean = detrendRed[farLeft:farRight]
RedReconstructedSig = filtfilt(b, a, totalRed_clean)

# Apply filter to blue channel
totalBlue_clean = detrendBlue[farLeft:farRight]
BlueReconstructedSig = filtfilt(b, a, totalBlue_clean)

# Section 4.1
# Find Pulse Rate

# Detect peaks with prominence
pks, _ = find_peaks(RedReconstructedSig, prominence=0.02)

# Calculate intervals between peaks and filter out close peaks
peakIntervals = np.diff(pks)
medianInterval = np.median(peakIntervals)
minIntervalThreshold = 0.65 * medianInterval
validPeaksIdx = np.hstack(([True], peakIntervals >= minIntervalThreshold))  # Keep the first peak
filteredPeaks = pks[validPeaksIdx]

# Calculate average distance between consecutive peaks (in frames)
automatic_avgDisbwPks = np.mean(np.diff(filteredPeaks))

# Period in seconds
autoPeriod = automatic_avgDisbwPks * (1 / videoFrameRate)

# Frequency in beats per second
autoFrequency = 1 / autoPeriod






# Convert to beats per minute (BPM)
autoPulseRate = autoFrequency * 60
print(f'Estimated Pulse Rate: {autoPulseRate:.2f} BPM')

# Section 5.1
# Estimate Oxygen Saturation (SpO2)

dcRed = np.mean(RedReconstructedSig)
dcBlue = np.mean(BlueReconstructedSig)
acRed = np.std(RedReconstructedSig)
acBlue = np.std(BlueReconstructedSig)

# Oxygen saturation calculation
A = 100
B = 5
SpO2 = A - B * ((acRed / dcRed) / (acBlue / dcBlue))
print(f'Estimated Oxygen Saturation (SpO2): {SpO2:.2f}%')

# Section 6.1
# Estimate Respiratory Rate

# Butterworth low-pass filter to isolate respiratory component
fc = 0.5  # Cut-off frequency (Hz)
b, a = butter(4, fc / (videoFrameRate / 2), btype='low')
filteredPPG = filtfilt(b, a, RedReconstructedSig)

# Apply Hampel filter to remove outliers (using MAD)
def hampel_filter(data, window_size, n_sigmas):
    n = len(data)
    new_data = np.copy(data)
    k = 1.4826  # Scale factor for Gaussian distribution
    for i in range(window_size, n - window_size):
        window = data[i - window_size:i + window_size + 1]
        median = np.median(window)
        mad = k * median_abs_deviation(window)
        threshold = n_sigmas * mad
        if np.abs(data[i] - median) > threshold:
            new_data[i] = median
    return new_data

cleanPPG = hampel_filter(filteredPPG, 6, 3)

# Welch’s method for power spectral density (PSD) estimation
window = hann(len(cleanPPG))
noverlap = int(0.5 * len(window))
nfft = len(cleanPPG)
f, pxx = welch(cleanPPG, fs=videoFrameRate, window=window, noverlap=noverlap, nfft=nfft, scaling='density')

# Find dominant frequency corresponding to respiratory rate
dominantFrequency = f[np.argmax(pxx)]

# Convert dominant frequency to breaths per minute
respiratoryRate = dominantFrequency * 60
print(f'Estimated Respiratory Rate: {respiratoryRate:.2f} breaths per minute')
