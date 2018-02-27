# spectrumLED

*spectrumLED* is a simple spectrum analyzer meant to be used with a 32x8 LED matrix (MAX7219). Though it can be easily modified to fit the other sizes and matrices.

## Build setup

* Hardware:
	* Orange Pi PC (Raspberry PI will hopefully work too)
	* PCM5102 DAC (or any soundcard)
* Software:
	* Armbian (latest stable)
	* Python 3.6 and third-party packages:
		* NumPy, SciPy, Luma, and PyAudio
	* ALSA

## Video

## Configuration

1. Load a loopback kernel module with:
```
# modprobe snd-aloop
```

2. Configure ALSA to output multiple streams with `multi` plugin. Example configuration is listed in `asound.conf` file: `hw:1,0` is a normal soundcard, `hw:3,0` is a loopback output, `hw:3,1` is a loopback input. Just copy it with:

```
# cp asound.conf /etc/
```

Change these settings if needed: run `aplay -l` to list all devices and correct card and device indices in the configuration file.

3. Configure an audio player. If you are using cmus, refer to `cmus.rc` file. I had no sound when `default` was specified in `dsp.alsa.device` option. Though `out` wrapper works fine.

...
