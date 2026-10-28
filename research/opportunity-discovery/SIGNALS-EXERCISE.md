# First exercise: samples, channels and time

Suggested time: 45–60 minutes. This supports the [learning plan](NEUROINFORMATICS-PLAN.md), independently of whether a software patch is ready. No equipment, account or recording download is needed.

## Read and predict

Start with Neuromatch's [introductory neuro videos](https://compneuro.neuromatch.io/tutorials/intro.html), particularly spiking activity, local field potentials and EEG/MEG. Then read [PyNWB's time-series introduction](https://pynwb.readthedocs.io/en/stable/tutorials/general/plot_file.html#time-series-data).

Before running the code, write answers to these questions:

1. With 100 samples per second, how far apart are successive samples?
2. If the first sample is at zero, what time is the 100th sample?
3. Does an array shaped `(100, 2)` contain 100 channels or two?
4. What additional information would you need before calling these numbers a neural recording?
5. Would preserving every value establish that the measurement or scientific interpretation was correct?

## Run a constructed signal

The following uses only Python's standard library. It produces mathematical sine waves, not a model or measurement of a brain:

```python
import math

rate = 100
times = [i / rate for i in range(100)]
channels = [(math.sin(2 * math.pi * 2 * t), math.sin(2 * math.pi * 12 * t)) for t in times]
print("sampling interval:", times[1] - times[0])
print("last sample time:", times[-1])
print("samples and channels:", len(channels), len(channels[0]))

# Compare 2 Hz and 12 Hz mathematical signals sampled at only 10 Hz.
slow_times = [i / 10 for i in range(10)]
a = [math.sin(2 * math.pi * 2 * t) for t in slow_times]
b = [math.sin(2 * math.pi * 12 * t) for t in slow_times]
print("largest sampled difference:", max(abs(x - y) for x, y in zip(a, b)))
```

The expected first outputs are 0.01 seconds, 0.99 seconds and `(100, 2)`. The two slowly sampled signals have nearly identical sampled values up to floating-point error, despite different underlying frequencies. Read the sampling material before generalising this example to a measurement system.

## Connect the exercise to Kufu's software work

In the NWB replay, rows represent samples and columns represent constructed channels. Replacing rows with zeros changes the stored sequence; preserving those values is a software requirement. Actual channel meaning requires a measurement method, units, reference, calibration and acquisition context. Spikes, LFP and EEG do not represent the same measurement.

Write three short statements: what you observed, why the mathematical example produced it, and what it does not establish about a biological brain. Bring any confusing distinction to the next learning session. No clinical interpretation or scientific discovery is claimed by this exercise.
