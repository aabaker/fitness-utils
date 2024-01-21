#!/usr/bin/env python3

# SPDX-License-Identifier: BSD-2-Clause
# Copyright Adam Baker 2021

from fitparse import FitFile
import sys
import matplotlib

# Fields in a record are:
# timestamp
# position_lat
# position_long
# distance
# enhanced_altitude
# altitude
# enhanced_speed
# speed
# unknown_61
# unknown_66
# heart_rate
# temperature

fitfile = FitFile(sys.argv[1])

timestamp = []
heartrate = []
gradient = []
temperature = []
altitude = []
distance = []
speed = []
records = fitfile.get_messages('record')
for record in records:
    try:
        ts = record.get('timestamp').value
        hr = record.get('heart_rate').value
        te = record.get('temperature').value
        al = record.get('enhanced_altitude').value
        # Speed is missing for indoor data
        sp = record.get('enhanced_speed').value
        ds = record.get('distance').value
    except AttributeError:
        continue
    timestamp.append(ts)
    heartrate.append(hr)
    temperature.append(te)
    altitude.append(al)
    speed.append(sp)
    distance.append(ds)


fig, ax = matplotlib.pyplot.subplots()

ax.plot_date(timestamp, heartrate, fmt='-', color="red")
ax2 = ax.twinx()
ax2.plot_date(timestamp, speed, fmt='-')
# ax.plot(distance, heartrate, color = "red")
ax.set_ylabel("Heart Rate (bpm)", color="red")
ax.grid(True)
# ax2.plot(distance, speed)
matplotlib.pyplot.show()
