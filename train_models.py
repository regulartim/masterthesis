import argparse

import pandas as pd
from greedybear_utils import calculate_interaction_delta, read_dump
from models.base_model import Model
from models.model_definitions import MODEL_DEFINITIONS
from models.utils import get_features


def run():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)

    parser.add_argument(
        "-d",
        "--training-data",
        required=True,
        help="Path to the .json file containing the training data.",
    )

    parser.add_argument(
        "-t",
        "--training-target",
        required=True,
        help="Path to the .json file containing the training targets.",
    )

    parser.add_argument(
        "--hyper-param-search",
        help="Triggers a random hyper parameter search for all trainable models with given data.",
        action="store_true",
    )

    config = vars(parser.parse_args())

    print("loading training data")
    training_data = read_dump(config["training_data"])
    training_data_date = max(row["last_seen"] for row in training_data)
    print(f"training data is from {training_data_date}")

    print("loading training target")
    training_target = read_dump(config["training_target"])
    training_target_date = max(row["last_seen"] for row in training_target)
    print(f"training target is from {training_target_date}")

    assert training_data_date < training_target_date

    interaction_delta = calculate_interaction_delta(training_data, training_data_date, training_target)
    training_df = get_features(training_data, training_data_date)
    training_df["interactions_on_eval_day"] = training_df["value"].map(lambda ip: interaction_delta[ip])

    models = [d.get("class", Model)(d) for d in MODEL_DEFINITIONS]
    for model in models:
        if model.trainable:
            model.train(training_df, config["hyper_param_search"])


if __name__ == "__main__":
    run()
