# Plotting FFT in real time

<img src="/FFT/assets/interface_01.png" alt="image" width="500"/>

## Installation requeriments

1. (Recommended) Create a virtual enviroment before running the application
2. Run the following pip install command to install all the libraries used

```bash
pip install numpy scipy sounddevice pyqt6 pyqtgraph

```

## Runnig application

1. Open a new terminal and run the following command

```bash
python main.py

```

## Main Layout


### Upload an audio file (.wav, mp3, .aac)
    Select an audio from device to plot and filter
### Save Changes
    Save the filtered file name in your device
### Apply FIters
1.- LOW PASS Filter
Creates a Butterwhole filtering the high frequencies,
modify the cutoff frequencies using the bottom slides
2.- HIGH PASS Filter
Creates a Butterwhole filtering the low frequencies,
modify the cutoff frequencies using the bottom slides
### Examples

<table>
  <tr>
    <td align="center">
        <img src="/FFT/assets/interface_02.png" alt="Video 1" width="500"/>
      <h2>Using the low pass filter to clean high frequencies below 700 hz</h2>
    </td>
    <td align="center">
        <img src="/FFT/assets/interface_03.png" alt="Video 2" width="500"/>
      <h2>Using the high pass filter to clean low frequencies above 2000 hz</h2>
    </td>
  </tr>
</table>
