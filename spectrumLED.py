import pyaudio as pa
import numpy as np
import scipy.fftpack as sf
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219

# Connect to a matrix via SPI
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)
device.contrast(1)

# Init PyAudio
p = pa.PyAudio()
N = 1024
device_index = 4
device_info = p.get_device_info_by_index(device_index)

# Frequency processing and grouping into bars
T = 1. / 48000
x = np.fft.rfftfreq(N, T)[-N//2:]

a = np.concatenate([np.linspace(47, 1000, 8),
                    np.linspace(1500, 6000, 13),
                    np.linspace(7000, 12000, 7),
                    np.linspace(13000, 17000, 5)
                    ])
bins = np.column_stack((a[:-1], a[1:]))

freq_ind = {}
bins_len = len(bins)

for i in range(32):
    freq_ind[i] = []

for i, f in enumerate(x):
    for j, a in enumerate(bins):
        if f > a[0] and f <= a[1]:
            freq_ind[j].append(i)


win = np.hamming(N*2)
win_sum = np.sum(win)
weights = np.linspace(3, 17, 32) ** 2

# Open a stream
s = p.open(format=pa.paInt16, channels=2,
           rate=int(device_info['defaultSampleRate']), input=True,
           frames_per_buffer=N, input_device_index=device_index)

bins_sum = np.zeros(32, dtype=np.int16)
maximums = np.zeros(64)
maximums[:] = 10000

z = 0
while True:
    try:
        s.start_stream()
        data = np.frombuffer(s.read(N), dtype=np.int16)
    except:
        continue

    y = sf.rfft(data * win)
    y = 2 / win_sum * np.abs(y[:N//2])

    for i, v in freq_ind.items():
        bins_sum[i] = np.mean(y[v])

    bins_sum = bins_sum * weights
    maximums[z] = np.max([np.max(bins_sum), 1000])
    bins_sum = ((bins_sum * 7) / np.mean(maximums)).astype(np.int16)

    with canvas(device) as draw:
        for x, y in enumerate(bins_sum):
            draw.line([x, 8, x, 8 - y], fill=128)

    s.stop_stream()
    z = z + 1 if z < 63 else 0
