from models.base_model import Classifier, Regressor
from models.consts import IP_REPUTATIONS, ML_FEATURES, MULTI_VAL_FEATURES
from models.utils import multi_label_encode, one_hot_encode
from scipy.stats import randint
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split

COMMON_SEARCH_PARAMS = {
    "n_estimators": randint(50, 500),
    "max_depth": [None] + list(range(10, 50)),
    "min_samples_split": randint(2, 20),
    "min_samples_leaf": randint(1, 10),
    "max_features": ["sqrt", "log2", None],
}


class RFClassifier(Classifier):
    def __init__(self, definition):
        super().__init__(definition)
        self.features = ML_FEATURES + MULTI_VAL_FEATURES + ["ip_reputation"]

    def hyper_param_search(self, X, y):
        """
        Hyper parameter search for RandomForestClassifier
        Best parameters (with SMOTE): {'class_weight': {False: 1, True: 8}, 'criterion': 'entropy', 'max_depth': 31, 'max_features': 'sqrt', 'min_samples_leaf': 1, 'min_samples_split': 2, 'n_estimators': 452}
        Best parameters (w/o SMOTE): {'class_weight': {False: 1, True: 4}, 'criterion': 'entropy', 'max_depth': 10, 'max_features': 'log2', 'min_samples_leaf': 6, 'min_samples_split': 3, 'n_estimators': 241}
        Best parameters (Halving): {'class_weight': {False: 1, True: 12}, 'criterion': 'log_loss', 'max_depth': 33, 'max_features': 'log2', 'min_samples_leaf': 8, 'min_samples_split': 19, 'n_estimators': 300}
        Best parameters: {'class_weight': {False: 1, True: 8}, 'criterion': 'log_loss', 'max_depth': 18, 'max_features': 'log2', 'min_samples_leaf': 9, 'min_samples_split': 8, 'n_estimators': 389}

        """
        print(f"\nHyper parameter search for RandomForestClassifier")
        param_dist = COMMON_SEARCH_PARAMS | {
            "criterion": ["gini", "entropy", "log_loss"],
            "class_weight": [{False: 1, True: w} for w in [1, 2, 4, 8, 12, 16]],
        }
        self.random_search(RandomForestClassifier(), param_dist, X, y)

    def train(self, df, search=False):
        X = df[self.features]
        y = df["interactions_on_eval_day"] > 0

        X = one_hot_encode(X, "ip_reputation", IP_REPUTATIONS)

        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)

        if search:
            self.hyper_param_search(X, y)
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        params = {
            "class_weight": {False: 1, True: 8},
            "criterion": "log_loss",
            "max_depth": 18,
            "max_features": "log2",
            "min_samples_leaf": 9,
            "min_samples_split": 8,
            "n_estimators": 389,
        }

        model = RandomForestClassifier(
            random_state=42,
            n_jobs=-1,
            **params,
        )
        model.fit(X_train, y_train)
        self.report(model, X_test, y_test, X.columns)
        self.save(model)

    def execute(self, df):
        model, _ = self.load()
        X = df[self.features]
        X = one_hot_encode(X, "ip_reputation", IP_REPUTATIONS)  # , remove=False)
        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)
        df[self.sort_key] = model.predict_proba(X)[:, 1]
        return df


class RFRegressor(Regressor):
    def __init__(self, definition):
        super().__init__(definition)
        self.features = ML_FEATURES + MULTI_VAL_FEATURES + ["ip_reputation"]

    def hyper_param_search(self, X, y):
        """
        Hyper parameter search for RandomForestRegressor
        Best parameters: {'criterion': 'friedman_mse', 'max_depth': 10, 'max_features': 'sqrt', 'min_samples_leaf': 1, 'min_samples_split': 13, 'n_estimators': 363}
        Best parameters: {'criterion': 'squared_error', 'max_depth': 11, 'max_features': 'sqrt', 'min_samples_leaf': 3, 'min_samples_split': 8, 'n_estimators': 70}
        Best parameters (Halving): {'criterion': 'poisson', 'max_depth': 19, 'max_features': 'log2', 'min_samples_leaf': 7, 'min_samples_split': 3, 'n_estimators': 479}
        Best parameters: {'criterion': 'squared_error', 'max_depth': 33, 'max_features': 'sqrt', 'min_samples_leaf': 5, 'min_samples_split': 15, 'n_estimators': 122}
        """
        print(f"\nHyper parameter search for RandomForestRegressor")
        param_dist = COMMON_SEARCH_PARAMS | {
            "criterion": ["squared_error", "friedman_mse", "poisson"],
        }
        self.random_search(RandomForestRegressor(), param_dist, X, y)

    def train(self, df, search=False):
        X = df[self.features]
        y = df["interactions_on_eval_day"]

        X = one_hot_encode(X, "ip_reputation", IP_REPUTATIONS)

        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)

        if search:
            self.hyper_param_search(X, y)
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        params = {
            "criterion": "squared_error",
            "max_depth": 33,
            "max_features": "sqrt",
            "min_samples_leaf": 5,
            "min_samples_split": 15,
            "n_estimators": 122,
        }
        model = RandomForestRegressor(
            random_state=42,
            n_jobs=-1,
            **params,
        )
        model.fit(X_train, y_train)
        self.report(model, X_test, y_test, X.columns)
        self.save(model)

    def execute(self, df):
        model, _ = self.load()
        X = df[self.features]
        X = one_hot_encode(X, "ip_reputation", IP_REPUTATIONS)  # , remove=False)
        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)
        df[self.sort_key] = model.predict(X)
        return df
