from sklearn.metrics import root_mean_squared_error
from sklearn.preprocessing import OneHotEncoder


def fit_encoder(rows):
    return OneHotEncoder(sparse_output=False, handle_unknown="ignore").fit(rows)


def encode(encoder, rows):
    return encoder.transform(rows).tolist()


def feature_names(encoder, columns):
    return [str(name) for name in encoder.get_feature_names_out(columns)]


def rmse(actual, predicted):
    return round(float(root_mean_squared_error(actual, predicted)), 4)
