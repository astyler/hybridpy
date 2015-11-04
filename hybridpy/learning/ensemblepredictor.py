__author__ = 'astyler'
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


class TripPredictor(object):
    def __init__(self, trip, feature_weights):
        self.scaler = StandardScaler()
        self.features = self.scaler.fit_transform(trip.values)
        self.tree = NearestNeighbors(n_neighbors=1).fit(self.features)

    def predict(self, query_point):
        query_point = self.scaler.transform(query_point)
        return self.tree.kneighbors(X=query_point, n_neighbors=1)


class EnsemblePredictor(object):
    def __init__(self, trip_list, feature_weights):
        self.ensemble = []
        self.feature_weights = feature_weights

        for trip in trip_list:
            self.add_trip(trip)

    def add_trip(self, trip):
        self.ensemble.append(TripPredictor(trip=trip, feature_weights=self.feature_weights))

    def predict(self, query_point):
        predictions = []
        for predictor in self.ensemble:
            predictions.append(predictor.predict(query_point))
        return predictions

