__author__ = 'astyler'
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import math
import numpy as np

class TripPredictor(object):
    def __init__(self, trip, features, feature_weights):
        self.features = features
        self.feature_weights = feature_weights

        self.scaler = StandardScaler()
        self.data = self.scaler.fit_transform(trip[features].values)
        self.data *= feature_weights

        self.tree = NearestNeighbors(n_neighbors=1).fit(self.data)

    def predict(self, query_point):
        query_point = self.feature_weights * self.scaler.transform(query_point[self.features].values)
        results = self.tree.kneighbors(X=query_point, n_neighbors=1)
        distance = results[0][0, 0]
        index = results[1][0, 0]
        return distance, index


class EnsemblePredictor(object):
    def __init__(self, trip_list,
                 features=['Latitude', 'Longitude', 'HeadingCosF', 'HeadingSinF', 'SpeedFilt', 'Acceleration', 'Power', 'TotalEnergyUsed'],
                 feature_weights=[1, 1, 0.25, 0.25, 0.1, 0, 0, 0.2]):
        self.ensemble = []
        self.ensemble_weights = []
        self.features = features
        self.feature_weights = feature_weights

        for trip in trip_list:
            self.add_trip(trip)

    def add_trip(self, trip):
        self.ensemble_weights = np.append(self.ensemble_weights, 1.0)
        self.ensemble.append(TripPredictor(trip=trip, features=self.features, feature_weights=self.feature_weights))

    def predict(self, query_point, sigma=1e-4, update_ensemble_weighting=False):
        predictions = []
        for weight, predictor in zip(self.ensemble_weights, self.ensemble):
            # convolve distance with gaussian kernel??  how wide?
            # convolve with ensemble weight
            distance, prediction = predictor.predict(query_point)

            predictions.append((self.norm(distance, sigma), prediction))

        if update_ensemble_weighting:
            self.ensemble_weights = np.multiply(self.ensemble_weights, [p[0] for p in predictions])
        
        self.ensemble_weights /= np.linalg.norm(self.ensemble_weights)

        return [(w, p[0], p[1]) for w, p in zip(self.ensemble_weights, predictions)]

    def norm(self, dist, sigma):
        return math.exp(-dist**2/(2*sigma))

    #def feedback(self, ):

