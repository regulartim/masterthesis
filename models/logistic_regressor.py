from models.base_model import Classifier
from models.consts import IP_REPUTATIONS, ML_FEATURES, MULTI_VAL_FEATURES
from models.utils import multi_label_encode, one_hot_encode
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class LogisticRegressor(Classifier):
    def __init__(self, definition):
        super().__init__(definition)
        self.features = ML_FEATURES + MULTI_VAL_FEATURES + ["ip_reputation"]

    def hyper_param_search(self, X, y):
        """
        Hyper parameter search for LogisticRegressor
        Best parameters: {'tol': 0.01, 'solver': 'saga', 'penalty': 'l1', 'max_iter': 5000, 'class_weight': 'balanced', 'C': 0.001}
        Best parameters: {'tol': 0.0001, 'solver': 'newton-cg', 'penalty': 'l2', 'max_iter': 1000, 'class_weight': None, 'C': 0.1}
        """
        print(f"\nHyper parameter search for LogisticRegressor")
        param_dist = {
            "penalty": ["l1", "l2", "elasticnet", "none"],
            "C": [0.001, 0.01, 0.1, 1, 10, 100],
            "solver": ["lbfgs", "newton-cg", "liblinear", "sag", "saga"],
            "max_iter": [100, 1000, 2500, 5000],
            "class_weight": ["balanced", None],
            "tol": [1e-4, 1e-3, 1e-2],
        }

        model = LogisticRegression()
        self.random_search(model, param_dist, X, y)

    def train(self, df, search=False):
        X = df[self.features]
        y = df["interactions_on_eval_day"] > 0

        X = one_hot_encode(X, "ip_reputation", IP_REPUTATIONS)

        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        if search:
            self.hyper_param_search(X_train, y_train)
            return

        params = {
            "tol": 0.0001,
            "solver": "newton-cg",
            "penalty": "l2",
            "max_iter": 1000,
            "class_weight": None,
            "C": 0.1,
        }
        lg_model = LogisticRegression(
            random_state=42,
            **params,
        )
        lg_model.fit(X_train, y_train)
        self.report(lg_model, X_test, y_test, X.columns)
        self.save(lg_model, scaler)

    def execute(self, df):
        lg_model, scaler = self.load(scaler=True)
        X = df[self.features]
        X = one_hot_encode(X, "ip_reputation", IP_REPUTATIONS)
        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)
        # print(scaler.feature_names_in_)
        # print(X.columns)
        df["lg_score"] = lg_model.predict_proba(scaler.transform(X))[:, 1]
        return df
