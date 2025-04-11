from models.aip_linear import AIPLinear
from models.cat_boost import CBClassifier, CBRanker, CBRegressor
from models.logistic_regressor import LogisticRegressor
from models.random_forest import RFClassifier, RFRegressor
from models.threat_level import ThreatLevel

MODEL_DEFINITIONS = [
    {
        "name": "Recent (GreedyBear)",
        "colour": "yellow",
        "sort_key": "last_seen",
    },
    {
        "name": "Persistent (GreedyBear)",
        "colour": "goldenrod",
        "sort_key": "attack_count",
    },
    {
        "name": "Prioritize Consistent (AIPish)",
        "colour": "purple",
        "sort_key": "pc_score",
    },
    {
        "name": "Prioritize New (AIPish)",
        "class": AIPLinear,
        "colour": "fuchsia",
        "sort_key": "pn_score",
    },
    {
        "name": "Threat Level",
        "class": ThreatLevel,
        "colour": "red",
        "sort_key": "tl_score",
    },
    {
        "name": "Logistic Regression",
        "class": LogisticRegressor,
        "trainable": True,
        "colour": "pink",
        "sort_key": "lg_score",
        "focus": "interactions",
    },
    {
        "name": "Random Forest Classifier",
        "class": RFClassifier,
        "trainable": True,
        "colour": "darkgreen",
        "sort_key": "rfc_score",
        "focus": "ips",
    },
    {
        "name": "Random Forest Regressor",
        "class": RFRegressor,
        "trainable": True,
        "colour": "lightgreen",
        "sort_key": "rfr_score",
        "focus": "interactions",
    },
    {
        "name": "CatBoost Classifier",
        "class": CBClassifier,
        "trainable": True,
        "colour": "royalblue",
        "sort_key": "cbc_score",
        "focus": "ips",
    },
    {
        "name": "CatBoost Regressor",
        "class": CBRegressor,
        "trainable": True,
        "colour": "darkturquoise ",
        "sort_key": "cbrg_score",
        "focus": "interactions",
    },
    {
        "name": "CatBoost Ranker",
        "class": CBRanker,
        "trainable": True,
        "colour": "lightblue",
        "sort_key": "cbr_score",
        "focus": "interactions",
    },
    {
        "name": "Upper Bound",
        "colour": "black",
        "sort_key": "interactions_on_eval_day",
    },
    {
        "name": "Lower Bound (Random)",
        "colour": "grey",
        "sort_key": "randomize",
    },
]
