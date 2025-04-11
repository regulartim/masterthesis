import abc
import os
import time

import joblib
import numpy as np
import pandas as pd
from models.consts import IP_REPUTATIONS, MAX_K, MULTI_VAL_FEATURES, SAMPLE_COUNT, SEARCH_CV, SEARCH_N_ITER, SEARCH_VERBOSITY
from models.utils import multi_label_encode, one_hot_encode
from sklearn.experimental import enable_halving_search_cv
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, r2_score
from sklearn.model_selection import HalvingRandomSearchCV, RandomizedSearchCV


class Model(object):
    def __init__(self, definition):
        self.name = definition["name"]
        self.colour = definition["colour"]
        self.sort_key = definition["sort_key"]
        self.estimator = definition.get("class")
        self.trainable = definition.get("trainable", False)
        self.focus = definition.get("focus", "general")
        self.features = []


class MLModel(Model):
    __metaclass__ = abc.ABCMeta

    def file_name(self) -> str:
        return self.name.replace(" ", "_").lower()

    def save(self, model, scaler=None):
        try:
            os.mkdir("./.joblib")
        except FileExistsError:
            pass
        if scaler is not None:
            joblib.dump(scaler, f"./.joblib/{self.file_name()}_scaler.joblib")
        joblib.dump(model, f"./.joblib/{self.file_name()}.joblib")

    def load(self, scaler=False):
        model = joblib.load(f"./.joblib/{self.file_name()}.joblib")
        if not scaler:
            return model, None
        return model, joblib.load(f"./.joblib/{self.file_name()}_scaler.joblib")

    def recall_auc(self, estimator, X, y):
        """Calculate the area under the recall curve for top-k predictions.

        Takes a fitted model (classifier or regressor) and calculates how well it ranks
        positive instances by computing recall at different depths k. The final score is
        the area under this recall curve, sampled at SAMPLE_COUNT evenly spaced points up to
        a quater of the dataset.

        Args:
            estimator: A fitted classifier or regressor. For classifiers, uses
                predict_proba; for regressors, uses predict.
            X: The input features to generate predictions for.
            y: Prediction targets with target values in column 'interactions_on_eval_day'.

        Returns:
            A score between 0 and 1, where 1 means perfect ranking (all positive
            instances are ranked before negative ones).
        """
        y = y.reset_index(drop=True)
        y_pred = pd.Series(estimator.predict_proba(X)[:, 1]) if isinstance(self, Classifier) else pd.Series(estimator.predict(X))
        df = pd.concat([y, y_pred], axis=1).sort_values(by=0, ascending=False)
        positives = df["interactions_on_eval_day"].sum()
        max_k = len(X)  # // 4
        step_size = max(max_k // SAMPLE_COUNT, 1)
        k_values = range(step_size, max_k + step_size, step_size)
        recalls = [df.head(k)["interactions_on_eval_day"].sum() / positives for k in k_values]
        area = np.trapz([0] + recalls) / SAMPLE_COUNT
        return area

    def random_search(self, estimator, param_dist, X, y, **kwargs):
        random_search = HalvingRandomSearchCV(
            estimator,
            param_distributions=param_dist,
            # n_iter=SEARCH_N_ITER,
            scoring=self.recall_auc,
            cv=SEARCH_CV,
            random_state=42,
            n_jobs=-1,
            verbose=SEARCH_VERBOSITY,
            min_resources=100,
        )

        random_search.fit(X, y, **kwargs)
        print("Best parameters:", random_search.best_params_)

    @abc.abstractmethod
    def score(self, estimator, X, y):
        return


class Classifier(MLModel):
    def report(self, model, X_test: np.ndarray, y_test: np.ndarray, cols):
        print(f"\n\n######## Training Report for {self.name} ########")
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)

        print(f"\nRecall AUC: {self.recall_auc(model, X_test,y_test):.4f}")

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        if hasattr(model, "feature_importances_"):
            feature_importance = pd.DataFrame({"feature": cols, "importance": model.feature_importances_})
            print("\nFeature Importance:")
            print(feature_importance.sort_values("importance", ascending=False))

        test_results = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
        for i, class_name in enumerate(model.classes_):
            test_results[f"Probability_class_{class_name}"] = y_pred_proba[:, i]

        print("\nSample of Predictions:")
        print(test_results.head())

    def execute(self, df):
        model, _ = self.load()
        X = df[self.features]
        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)
        df[self.sort_key] = model.predict_proba(X)[:, 1]
        return df


class Regressor(MLModel):
    def report(self, model, X_test, y_test, cols):
        print(f"\n\n######## Training Report for {self.name} ########")
        y_pred = model.predict(X_test)

        print(f"\nRecall AUC: {self.recall_auc(model, X_test,y_test):.4f}")

        if hasattr(model, "feature_importances_"):
            feature_importance = pd.DataFrame({"feature": cols, "importance": model.feature_importances_})
            print("\nFeature Importance:")
            print(feature_importance.sort_values("importance", ascending=False))

        test_results = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
        print("\nSample of Predictions:")
        print(test_results.head())

    def execute(self, df):
        model, _ = self.load()
        X = df[self.features]
        for feature in MULTI_VAL_FEATURES:
            X = multi_label_encode(X, feature)
        df[self.sort_key] = model.predict(X)
        return df
