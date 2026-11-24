from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder


def fit_encoder(rows):
    return OneHotEncoder(sparse=False, handle_unknown="ignore").fit(rows)


def encode(encoder, rows):
    return encoder.transform(rows).tolist()


def feature_names(encoder, columns):
    return [str(name) for name in encoder.get_feature_names(columns)]


def rmse(actual, predicted):
    return round(float(mean_squared_error(actual, predicted, squared=False)), 4)
