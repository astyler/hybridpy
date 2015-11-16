__author__ = 'astyler'
import pandas as pd
import numpy as np
import math
import osmapping
from scipy.signal import butter, filtfilt

def load(fname):
    trip = pd.read_csv(fname)
    elapsed = np.cumsum(trip.PeriodMS / 1000.0)
    elapsed -= elapsed[0]
    trip['ElapsedSeconds'] = elapsed

    # smooth speed
    b, a = butter(2, 0.5)
    trip.Speed = filtfilt(b, a, trip.Speed)

    trip.Acceleration = trip.Speed.diff()
    trip.Acceleration[0] = 0

    # smooth noisy elevation measurements
    b, a = butter(4, 0.05)
    trip.Elevation = filtfilt(b, a, trip.Elevation)

    locations = trip[['Latitude', 'Longitude']].values

    # add heading
    headings = [compute_heading(lat1=here[0], lat2=there[0], lon1=here[1], lon2=there[1]) for here, there in zip(locations[0:-1], locations[1:])]
    headings.append(headings[-1])

    filtered_headings = [headings[0]]

    for heading, speed in zip(headings[1:], trip.Speed.values[1:]):
        if speed < 1:
            filtered_headings.append(filtered_headings[-1])
        else:
            filtered_headings.append(heading)

    b, a = butter(2, 0.2)
    trip['Heading'] = filtfilt(b,a,filtered_headings)

    # add gradient
    planar_distances = [osmapping.haversine(here, there)+1.0 for here, there in zip(locations[0:-1], locations[1:])]
    trip['Gradient'] = trip.Elevation.diff() / ([1.0] + planar_distances)
    trip.loc[0, 'Gradient'] = trip.loc[1, 'Gradient']
    return trip


def compute_heading(lat1, lat2, lon1, lon2):
    lat1, lat2, lon1, lon2 = map(math.radians, [lat1, lat2, lon1, lon2])
    return math.atan2(math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1),
                      math.sin(lon2 - lon1) * math.cos(lat2))