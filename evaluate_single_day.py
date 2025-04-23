import argparse
import json
import re
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
from greedybear_utils import calculate_interaction_delta, read_delta_file, read_dump
from models.base_model import Model
from models.feed import Feed
from models.model_definitions import MODEL_DEFINITIONS
from models.utils import get_features, load_coa_data, load_csv, load_txt, plot


def run():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)

    parser.add_argument(
        "-s",
        "--scoring-data",
        required=True,
        help="Path to the .json file containing the training data.",
    )

    parser.add_argument(
        "-e",
        "--evaluation-data",
        required=True,
        help="Path to the .json file containing the evaluation data.",
    )

    parser.add_argument(
        "--delta",
        help="If evaluation data is a prepared delta file.",
        action="store_true",
    )

    parser.add_argument(
        "-n",
        "--prioritize-new",
        help="Path to the .csv file containing the prioritize-new feed.",
    )

    parser.add_argument(
        "-c",
        "--prioritize-consistent",
        help="Path to the .csv file containing the prioritize-consistent feed.",
    )

    parser.add_argument(
        "-a",
        "--abuseipdb",
        help="Path to the .txt file containing the abuseipdb blocklist.",
    )

    parser.add_argument(
        "--coa",
        help="Path to the .json file containing the 'confidence of abuse' scores.",
    )

    parser.add_argument(
        "-d",
        "--details",
        help="Print more metrics per feed.",
        action="store_true",
    )

    parser.add_argument(
        "-m",
        "--exclude-mass-scanners",
        help="Exclude mass scanners from evaluation.",
        action="store_true",
    )

    parser.add_argument(
        "-f",
        "--feed-size",
        help="Number of records the generated feed should have.",
        type=int,
        default=5000,
    )

    parser.add_argument(
        "--test-sizes-up-to",
        help="Number of records the generated feed should have.",
    )

    parser.add_argument(
        "--dump",
        help="Write feed data into txt file.",
        action="store_true",
    )

    parser.add_argument(
        "-p",
        "--plot",
        help="Plot result into line graphs.",
        action="store_true",
    )

    config = vars(parser.parse_args())

    print("loading scoring data")
    scoring_data = read_dump(config["scoring_data"], exclude_mass_scanners=config["exclude_mass_scanners"])
    scoring_data_date = max(row["last_seen"] for row in scoring_data)
    print(f"scoring data is from {scoring_data_date}")

    print("loading evaluation data")
    if config["delta"]:
        evaluation_data, evaluation_data_date = read_delta_file(config["evaluation_data"])
        interaction_delta = defaultdict(int, evaluation_data)
    else:
        evaluation_data = read_dump(config["evaluation_data"], exclude_mass_scanners=config["exclude_mass_scanners"])
        evaluation_data_date = max(row["last_seen"] for row in evaluation_data)
        assert scoring_data_date < evaluation_data_date
        interaction_delta = calculate_interaction_delta(scoring_data, scoring_data_date, evaluation_data)
    print(f"evaluation data is from {evaluation_data_date}")

    coa_scores = None
    if config["coa"]:
        print("loading confidence of abuse data")
        coa_scores = load_coa_data(config["coa"])

    print("extracting features")
    scoring_df = get_features(scoring_data, scoring_data_date)
    scoring_df["interactions_on_eval_day"] = scoring_df["value"].map(lambda ip: interaction_delta[ip])

    print("calculating scores")
    models = [d.get("class", Model)(d) for d in MODEL_DEFINITIONS]
    for model in models:
        if model.estimator is not None:
            model.execute(scoring_df)

    print("creating feeds")
    three_days_ago = (date.fromisoformat(scoring_data_date) - timedelta(days=3)).isoformat()
    two_weeks_ago = (date.fromisoformat(scoring_data_date) - timedelta(days=14)).isoformat()
    feeds = {
        model.name: Feed(model.name, data=scoring_df, size=config["feed_size"], sort_key=model.sort_key, eval_ips=interaction_delta, coa_scores=coa_scores)
        for model in models
    }

    if "Recent (GreedyBear)" in feeds:
        feeds["Recent (GreedyBear)"].exclude(scoring_df["last_seen"] < three_days_ago)
    if "Persistent (GreedyBear)" in feeds:
        feeds["Persistent (GreedyBear)"].exclude((scoring_df["last_seen"] < two_weeks_ago) | (scoring_df["days_seen"].str.len() < 10))
    if config["prioritize_new"]:
        csv_df = load_csv(config["prioritize_new"])
        csv_df["interactions_on_eval_day"] = csv_df["value"].map(lambda ip: interaction_delta[ip])
        feeds["AIP Prioritize New"] = Feed(
            "AIP Prioritize New", data=csv_df, size=config["feed_size"], sort_key="score", eval_ips=interaction_delta, coa_scores=coa_scores
        )
    if config["prioritize_consistent"]:
        csv_df = load_csv(config["prioritize_consistent"])
        csv_df["interactions_on_eval_day"] = csv_df["value"].map(lambda ip: interaction_delta[ip])
        feeds["AIP Prioritize Consistent"] = Feed(
            "AIP Prioritize Consistent", data=csv_df, size=config["feed_size"], sort_key="score", eval_ips=interaction_delta, coa_scores=coa_scores
        )
    if config["abuseipdb"]:
        adb_df = load_txt(config["abuseipdb"])
        adb_df["interactions_on_eval_day"] = adb_df["value"].map(lambda ip: interaction_delta[ip])
        feeds["AbuseIPDB Blocklist"] = Feed(
            "AbuseIPDB Blocklist", data=adb_df, size=config["feed_size"], sort_key="score", eval_ips=interaction_delta, coa_scores=coa_scores
        )

    print("evaluating")
    if config["test_sizes_up_to"]:
        if re.match(r"^[\d]{1,2}%$", config["test_sizes_up_to"]):
            max_size = len(scoring_data) * int(config["test_sizes_up_to"][:-1]) // 100
            percentage = True
        else:
            max_size = int(config["test_sizes_up_to"])
            percentage = False
        test_results = []
        for feed in feeds.values():
            test_results.extend(feed.evaluate_range(max_size))
        if config["plot"]:
            plot(models, pd.DataFrame(test_results), scoring_data_date, evaluation_data_date, percentage)

    for feed in feeds.values():
        feed.evaluate()
        if config["details"]:
            print(f"\n{feed.name}:")
            print(json.dumps(feed.metrics, sort_keys=True, indent=4))
        else:
            print(feed)

    if config["dump"]:
        print("writing blocklists")
        for feed in feeds.values():
            feed.dump_to_txt()


if __name__ == "__main__":
    run()
