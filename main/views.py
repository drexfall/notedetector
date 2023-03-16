from django.shortcuts import render, HttpResponseRedirect
import numpy as np
import wave
import struct
import os
# Create your views here.


def find_nearest(array, value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]


def get_notes(filename):
    window_size = 2205    # Size of window to be used for detecting silence
    beta = 1   # Silence detection parameter
    max_notes = 100    # Maximum number of notes in file, for efficiency
    sampling_freq = 44100  # Sampling frequency of audio signal
    threshold = 15
    array = [16.35,	17.32,	18.35,	19.45,	20.60,	21.83,	23.12,	24.50,	25.96,	27.50,	29.14,	30.87,
             32.70,	34.65,	36.71,	38.89,	41.20,	43.65,	46.25,	49.00,	51.91,	55.00,	58.27,	61.74,
             65.41,	69.30,	73.42,	77.78,	82.41,	87.31,	92.50,	98.00,	103.8,	110.0,	116.5,	123.5,
             130.8,	138.6,	146.8,	155.6,	164.8,	174.6,	185.0,	196.0,	207.7,	220.0,	233.1,	246.9,
             261.6,	277.2,	293.7,	311.1,	329.6,	349.2,	370.0,	392.0,	415.3,	440.0,	466.2,	493.9,
             523.3,	554.4,	587.3,	622.3,	659.3,	698.5,	740.0,	784.0,	830.6,	880.0,	932.3,	987.8,
             1047,	1109,	1175,	1245,	1319,	1397,	1480,	1568,	1661,	1760,	1865,	1976,
             2093,	2217,	2349,	2489,	2637,	2794,	2960,	3136,	3322,	3520,	3729,	3951,
             4186,	4435,	4699,	4978,	5274,	5588,	5920,	6272,	6645,	7040,	7459,	7902,

             ]

    notes = ['C',	'C#',	'D',	'Eb',	'E',	'F',	'F#',	'G',	'G#',	'A',	'Bb',	'B',
             'C1',	'C#1',	'D1',	'Eb1',	'E1',	'F1',	'F#1',	'G1',	'G#1',	'A1',	'Bb1',	'B1',
             'C',	'C#2',	'D2',	'Eb2',	'E2',	'F2',	'F#2',	'G2',	'G#2',	'A2',	'Bb2',	'B2',
             'C',	'C#3',	'D3',	'Eb3',	'E3',	'F3',	'F#3',	'G3',	'G#3',	'A3',	'Bb3',	'B3',
             'C',	'C#4',	'D4',	'Eb4',	'E4',	'F4',	'F#4',	'G4',	'G#4',	'A4',	'Bb4',	'B4',
             'C',	'C#5',	'D5',	'Eb5',	'E5',	'F5',	'F#5',	'G5',	'G#5',	'A5',	'Bb5',	'B5',
             'C',	'C#6',	'D6',	'Eb6',	'E6',	'F6',	'F#6',	'G6',	'G#6',	'A6',	'Bb6',	'B6',
             'C',	'C#7',	'D7',	'Eb7',	'E7',	'F7',	'F#7',	'G7',	'G#7',	'A7',	'Bb7',	'B7',
             'C',	'C#8',	'D8',	'Eb8',	'E8',	'F8',	'F#8',	'G8',	'G#8',	'A8',	'Bb8',	'B8',]
    Identified_Notes = []
    frequencies = []

    # Read file
    sound_file = wave.open(filename, 'r')
    file_length = sound_file.getnframes()

    sound = np.zeros(file_length)
    mean_square = []
    sound_square = np.zeros(file_length)
    for i in range(file_length):
        data = sound_file.readframes(1)
        data = struct.unpack("<h", data)
        sound[i] = int(data[0])

    sound = np.divide(sound, float(2**15))  # Normalize data in range -1 to 1

    ######################### DETECTING SCILENCE ##################################

    sound_square = np.square(sound)
    frequency = []
    dft = []
    i = 0
    j = 0
    k = 0
    # traversing sound_square array with a fixed window_size
    while (i <= len(sound_square)-window_size):
        s = 0.0
        j = 0
        while (j < window_size):
            s = s + sound_square[i+j]
            j = j + 1
    # detecting the silence waves
        if s < threshold:
            if (i-k > window_size*4):
                dft = np.array(dft)  # applying fourier transform function
                dft = np.fft.fft(sound[k:i])
                dft = np.argsort(dft)

                if (dft[0] > dft[-1] and dft[1] > dft[-1]):
                    i_max = dft[-1]
                elif (dft[1] > dft[0] and dft[-1] > dft[0]):
                    i_max = dft[0]
                else:
                    i_max = dft[1]
    # calculating frequency
                frequency.append((i_max*sampling_freq)/(i-k))
                dft = []
                k = i+1
        i = i + window_size

    for i in frequency:
        frequencies.append(i)
        idx = (np.abs(array-i)).argmin()
        Identified_Notes.append(notes[idx])

    return {"frequency": frequencies, "notes": Identified_Notes}


def index(request):
    result = {}
    if request.method == "POST":
        if request.FILES:
            f = request.FILES['filename']
            with open(os.getcwd()+'/static/upload/audio.wav', 'wb+') as destination:
                destination.truncate(0)  
                for chunk in f.chunks():  
                    destination.write(chunk) 
            result = get_notes(os.getcwd()+'/static/upload/audio.wav')
    return render(request, "index.html", result)
