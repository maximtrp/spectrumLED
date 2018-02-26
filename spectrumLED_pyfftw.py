import pyaudio as pa
import numpy as np
import pyfftw.interfaces.scipy_fftpack as pf
import time
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219

# Connect to a LED matrix (MAX7219) via SPI
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)
device.contrast(1)

# Init PyAudio
p = pa.PyAudio()
N = 1024
device_index = 4
device_info = p.get_device_info_by_index(device_index)

# Process frequencies and group into bars
T = 1. / 48000
x = np.fft.rfftfreq(N, T)[-N//2:]

a = np.concatenate([np.linspace(47, 1000, 8), np.linspace(1500, 6000, 13), np.linspace(7000, 12000, 7), np.linspace(13000, 17000, 5)])
bins = np.column_stack((a[:-1], a[1:]))

freq_ind = {}
bins_len = len(bins)

for i in range(32):
	freq_ind[i] = []

for i, f in enumerate(x):
	for j, a in enumerate(bins):
		if f > a[0] and f <= a[1]:
			freq_ind[j].append(i)

# Window and weight settings
win = np.hamming(N*2)
win_sum = np.sum(win)
weights = np.linspace(3, 17, 32) ** 2

# Open a stream
s = p.open(format=pa.paInt16, channels=2, rate=int(device_info['defaultSampleRate']), input=True, frames_per_buffer=N, input_device_index=device_index)

while True:
	try:
		bins_sum = np.zeros(32, dtype=np.int16)
		s.start_stream()
		data = np.frombuffer(s.read(N), dtype=np.int16)

		# Fourier transformations
		y = pf.rfft(data * win)
		y = 2 / win_sum * np.abs(y[:N//2])

		# Grouping into bars and scaling within 0...7
		for i, v in freq_ind.items():
			bins_sum[i] = np.mean(y[v])

		bins_sum = bins_sum * weights
		bins_sum = ((bins_sum * 7) / 15000).astype(np.int16)

		# Drawing
		with canvas(device) as draw:
			for x, y in enumerate(bins_sum):
				draw.line([x, 8, x, 8 - y], fill=128)

		s.stop_stream()
	except:
		continue
