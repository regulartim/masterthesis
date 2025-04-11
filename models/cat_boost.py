import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, CatBoostRanker, CatBoostRegressor
from models.base_model import Classifier, Regressor
from models.consts import CATEGORICAL_FEATURES, ML_FEATURES, MULTI_VAL_FEATURES
from models.utils import multi_label_encode
from scipy.stats import randint, uniform
from sklearn.model_selection import train_test_split

COMMON_SEARCH_PARAMS = {
    "iterations": randint(100, 2000),
    "learning_rate": uniform(0.01, 0.3),
    "depth": randint(4, 10),
    "l2_leaf_reg": uniform(1, 10),
    "border_count": randint(1, 255),
    "boosting_type": ["Plain", "Ordered"],
    "rsm": uniform(0, 1),
    "min_child_samples": randint(1, 20),
}


class CBClassifier(Classifier):
    def __init__(self, definition):
        super().__init__(definition)
        self.features = ML_FEATURES + MULTI_VAL_FEATURES + CATEGORICAL_FEATURES

    def hyper_param_search(self, X, y):
        """
        Best parameters: {'bagging_temperature': 0.05819359550844361, 'boosting_type': 'Ordered', 'border_count': 1, 'class_weights': {False: 1, True: 2}, 'depth': 9, 'iterations': 217, 'l2_leaf_reg': 8.145959227000624, 'learning_rate': 0.20805921301531938, 'min_child_samples': 1, 'rsm': 0.9548652806631941}
        """
        print(f"\nHyper parameter search for CatBoostClassifier")
        param_dist = COMMON_SEARCH_PARAMS | {
            "bagging_temperature": uniform(0, 1),
            "class_weights": [{False: 1, True: w} for w in [1, 2, 4, 8, 12, 16]],
        }

        model = CatBoostClassifier(cat_features=CATEGORICAL_FEATURES, random_seed=42, silent=True)
        self.random_search(model, param_dist, X, y)

    def train(self, df, search=False):
        X = df[self.features]
        y = df["interactions_on_eval_day"] > 0

        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)

        if search:
            self.hyper_param_search(X, y)
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        params = {
            "bagging_temperature": 0.05819359550844361,
            "boosting_type": "Ordered",
            "border_count": 1,
            "class_weights": {False: 1, True: 2},
            "depth": 9,
            "iterations": 217,
            "l2_leaf_reg": 8.145959227000624,
            "learning_rate": 0.20805921301531938,
            "min_child_samples": 1,
            "rsm": 0.9548652806631941,
        }
        model = CatBoostClassifier(
            random_seed=42,
            verbose=False,
            # **params,
        )
        model.fit(X_train, y_train, cat_features=CATEGORICAL_FEATURES)
        self.report(model, X_test, y_test, X.columns)
        self.save(model)


class CBRegressor(Regressor):
    def __init__(self, definition):
        super().__init__(definition)
        self.features = ML_FEATURES + MULTI_VAL_FEATURES + CATEGORICAL_FEATURES

    def hyper_param_search(self, X, y):
        """
        Best parameters: {'boosting_type': 'Plain', 'border_count': 109, 'depth': 9, 'iterations': 840, 'l2_leaf_reg': 10.336918237598745, 'learning_rate': 0.012260308940222422, 'loss_function': 'RMSE', 'min_child_samples': 6, 'rsm': 0.36535681967405764}
        """
        print(f"\nHyper parameter search for CatBoostRegressor")
        param_dist = COMMON_SEARCH_PARAMS | {
            "loss_function": ["RMSE", "MAE", "Quantile", "MAPE"],  # Regression-specific loss functions
        }

        model = CatBoostRegressor(cat_features=CATEGORICAL_FEATURES, random_seed=42, silent=True)
        self.random_search(model, param_dist, X, y)

    def train(self, df, search=False):
        X = df[self.features]
        y = df["interactions_on_eval_day"]

        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)

        if search:
            self.hyper_param_search(X, y)
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        params = {
            "boosting_type": "Plain",
            "border_count": 109,
            "depth": 9,
            "iterations": 840,
            "l2_leaf_reg": 10.336918237598745,
            "learning_rate": 0.012260308940222422,
            "loss_function": "RMSE",
            "min_child_samples": 6,
            "rsm": 0.36535681967405764,
        }

        model = CatBoostRegressor(
            random_seed=42,
            verbose=False,
            **params,
        )
        model.fit(X_train, y_train, cat_features=CATEGORICAL_FEATURES)
        self.report(model, X_test, y_test, X.columns)
        self.save(model)


class CBRanker(Regressor):
    def __init__(self, definition):
        super().__init__(definition)
        self.features = ML_FEATURES + MULTI_VAL_FEATURES + CATEGORICAL_FEATURES

    def hyper_param_search(self, X, y, query_id):
        """
        Best parameters: {'boosting_type': 'Plain', 'border_count': 207, 'depth': 5, 'iterations': 653, 'l2_leaf_reg': 5.393365018657701, 'leaf_estimation_method': 'Newton', 'learning_rate': 0.019428755706020276, 'loss_function': 'QuerySoftMax', 'min_child_samples': 17, 'rsm': 0.3143559810763267}
        Best parameters: {'boosting_type': 'Plain', 'border_count': 207, 'depth': 5, 'iterations': 1677, 'l2_leaf_reg': 5.393365018657701, 'leaf_estimation_method': 'Newton', 'learning_rate': 0.019428755706020276, 'loss_function': 'RMSE', 'min_child_samples': 17, 'rsm': 0.3143559810763267}
        """
        print(f"\nHyper parameter search for CatBoostRanker")
        param_dist = COMMON_SEARCH_PARAMS | {
            "leaf_estimation_method": ["Newton", "Gradient"],
            "loss_function": ["RMSE", "QueryRMSE"],
        }

        model = CatBoostRanker(cat_features=CATEGORICAL_FEATURES, random_seed=42, silent=True)
        self.random_search(model, param_dist, X, y, group_id=query_id)

    def train(self, df, search=False):
        X = df[self.features]
        # y = np.ceil(np.log10(df["interactions_on_eval_day"] + 1))
        y = df["interactions_on_eval_day"]

        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)

        query_id = pd.DataFrame([1] * X.shape[0])

        # for i in range(101):
        #    print(i, np.ceil(np.log10(i + 1)))
        # exit()
        # import plotly.express as px

        # df = px.data.tips()
        # fig = px.histogram(df, x=y)
        # fig.show()
        # exit()

        if search:
            self.hyper_param_search(X, y, query_id)
            return

        X_train, X_test, y_train, y_test, query_test, _ = train_test_split(X, y, query_id, test_size=0.2, random_state=42)

        params = {
            "boosting_type": "Plain",
            "border_count": 207,
            "depth": 5,
            "iterations": 1677,
            "l2_leaf_reg": 5.393365018657701,
            "leaf_estimation_method": "Newton",
            "learning_rate": 0.019428755706020276,
            "loss_function": "QuerySoftMax",
            "min_child_samples": 17,
            "rsm": 0.3143559810763267,
        }

        model = CatBoostRanker(
            random_seed=42,
            verbose=False,
            # loss_function="RMSE",
            **params,
        )

        model.fit(X_train, y_train, cat_features=CATEGORICAL_FEATURES, group_id=query_test)
        self.report(model, X_test, y_test, X.columns)
        self.save(model)
