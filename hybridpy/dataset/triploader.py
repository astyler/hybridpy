__author__ = 'astyler'
import pandas as pd
import numpy as np
import math


def load(fname):
    trip = pd.read_csv(fname)
    trip['ElapsedSeconds'] = np.cumsum(trip.PeriodMS / 1000.0)
    trip.ElapsedSeconds -= trip.ElapsedSeconds[0]

    headings = []
    for idx in xrange(len(trip) - 1):
        here = trip.iloc[idx]
        there = trip.iloc[idx + 1]
        headings.append(compute_heading(lat1=here.Latitude, lat2=there.Latitude, lon1=here.Longitude, lon2=there.Longitude))

    headings.append(0)
    trip.Heading = headings

    return trip


def compute_heading(lat1, lat2, lon1, lon2):
    lat1, lat2, lon1, lon2 = map(math.radians, [lat1, lat2, lon1, lon2])
    return math.atan2(math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1),
                      math.sin(lon2 - lon1) * math.cos(lat2))