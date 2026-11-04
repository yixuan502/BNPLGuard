"""Codebook-driven transformations. Statistical fitting stays inside Pipeline."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from .common import read_json

def map_target(series):
    spec = read_json('config/label_mapping.json')
    allowed = {int(k) for k in spec['mapping']} | {int(k) for k in spec['missing_codes']}
    bad = series.notna() & ~series.isin(allowed)
    if bad.any():
        raise ValueError(f'Invalid ENDSMEET codes: {series[bad].unique().tolist()}')
    return series.map({int(k): v for k, v in spec['mapping'].items()})

def clean_features(frame, schema=None):
    """Validate raw PUF codes and collapse documented categories without learning statistics."""
    if schema is None:
        schema = read_json('config/feature_schema.json')['features']
    absent = set(schema) - set(frame.columns)
    if absent:
        raise ValueError(f'Missing required columns: {sorted(absent)}')
    result = pd.DataFrame(index=frame.index)
    for name, meta in schema.items():
        s = frame[name]
        allowed = {int(k) for k in meta['labels']} | {int(k) for k in meta['missing_codes']}
        bad = s.notna() & ~s.isin(allowed)
        if bad.any():
            raise ValueError(f'Invalid {name} codes: {s[bad].unique().tolist()}')
        s = s.replace({int(k): np.nan for k in meta['missing_codes']}).astype(float)
        if 'transform' in meta:
            s = s.map({int(k): float(v) for k, v in meta['transform'].items()})
        result[name] = s
    return result

class CodebookTransformer(TransformerMixin, BaseEstimator):
    """Persist the exact raw-input mapping inside each fitted artifact."""
    def __init__(self, schema):
        self.schema = schema

    def fit(self, X, y=None):
        clean_features(X, self.schema)
        self.n_features_in_ = len(self.schema)
        self.feature_names_in_ = np.array(list(self.schema), dtype=object)
        return self

    def transform(self, X):
        return clean_features(X, self.schema)

def build_pipeline(estimator):
    schema = read_json('config/feature_schema.json')['features']
    columns = list(schema)
    categorical = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent', keep_empty_features=True)),
        ('onehot', OneHotEncoder(handle_unknown='ignore')),
    ])
    # New objects on every call: model pipelines never share mutable fitted state.
    return Pipeline([
        ('codebook', CodebookTransformer(schema)),
        ('preprocessor', ColumnTransformer([('categorical', categorical, columns)], remainder='drop')),
        ('classifier', estimator),
    ])
