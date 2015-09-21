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
    b, a = butter(2, 0.6)
    trip.Speed = filtfilt(b, a, trip.Speed)

    # smooth noisy elevation measurements
    b, a = butter(4, 0.05)
    trip.Elevation = filtfilt(b, a, trip.Elevation)

    locations = trip[['Latitude', 'Longitude']].values

    # add heading
    headings = [compute_heading(lat1=here[0], lat2=there[0], lon1=here[1], lon2=there[1]) for here, there in zip(locations[0:-1], locations[1:])]
    headings.append(0)
    trip['Heading'] = headings

    # add gradient
    planar_distances = [osmapping.haversine(here, there)+1.0 for here, there in zip(locations[0:-1], locations[1:])]
    trip['Gradient'] = trip.Elevation.diff() / ([1.0] + planar_distances)
    trip.loc[0, 'Gradient'] = trip.loc[1, 'Gradient']
    return trip


def compute_heading(lat1, lat2, lon1, lon2):
    lat1, lat2, lon1, lon2 = map(math.radians, [lat1, lat2, lon1, lon2])
    return math.atan2(math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1),
                      math.sin(lon2 - lon1) * math.cos(lat2))