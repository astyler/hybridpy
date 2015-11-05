__author__ = 'astyler'
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


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
                 features=['Latitude', 'Longitude', 'Bearing', 'Speed', 'Acceleration', 'Power', 'TotalEnergyUsed'],
                 feature_weights=[1, 1, 0.5, 0.1, 0, 0, 0.2]):
        self.ensemble = []
        self.features = features
        self.feature_weights = feature_weights

        for trip in trip_list:
            self.add_trip(trip)

    def add_trip(self, trip):
        self.ensemble.append(TripPredictor(trip=trip, features=self.features, feature_weights=self.feature_weights))

    def predict(self, query_point):
        predictions = []
        for predictor in self.ensemble:
            predictions.append(predictor.predict(query_point))
        return predictions

