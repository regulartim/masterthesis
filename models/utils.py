import json
import sys
from datetime import date
from functools import cache

import numpy as np
import pandas as pd
import plotly.express as px


@cache
def date_delta(earlier_date: str, later_date: str) -> int:
    """
     Calculate number of days between two dates in ISO format.

    Args:
        earlier_date: ISO format date string (YYYY-MM-DD)
        later_date: ISO format date string (YYYY-MM-DD)

    Returns:
        Number of days between dates (positive if later_date is after earlier_date)

    Raises:
       ValueError: If dates are not in ISO format (YYYY-MM-DD)
    """
    try:
        d1 = date.fromisoformat(earlier_date)
        d2 = date.fromisoformat(later_date)
    except ValueError as exc:
        raise ValueError("Dates must be in ISO format (YYYY-MM-DD)") from exc
    return (d2 - d1).days


def correlated_features(df: pd.DataFrame, features: list[str], threshold: float) -> list[tuple]:
    """
    Identify highly correlated feature pairs in a DataFrame.

    Args:
        df: Input DataFrame containing the features
        features: List of feature names to analyze
        threshold: Minimum absolute correlation value to consider features as highly correlated

    Returns:
        Correlated pairs with correlation > threshold
    """
    if not all(f in df.columns for f in features):
        raise ValueError("All features must be present in DataFrame")
    corr_matrix = df[features].corr()
    high_corr_pairs = []
    for idx, f1 in enumerate(features):
        for f2 in features[idx + 1 :]:
            if abs(corr_matrix.loc[f1, f2]) > threshold:
                high_corr_pairs.append((f1, f2, corr_matrix.loc[f1, f2]))
    return high_corr_pairs


def correlation_analysis(df: pd.DataFrame, features: list[str], threshold: float = 0.7) -> None:
    """
    Analyze feature correlations and print highly correlated pairs.

    Args:
        df: Input DataFrame containing the features
        features: List of feature names to analyze
        threshold: Minimum absolute correlation value to consider features as highly correlated (default: 0.7)
    """
    high_corr_pairs = correlated_features(df, features, threshold)
    if high_corr_pairs:
        print("Found highly correlated features:")
        for f1, f2, corr in high_corr_pairs:
            print(f"{f1} & {f2}: {corr:.2f}")


def get_features(iocs: list[dict], reference_day: str) -> pd.DataFrame:
    """
    Extract and calculate features from IOC data.

    Args:
        iocs: List of IOC dictionaries with required fields
        reference_day: Reference date for time-based calculations

    Returns:
       DataFrame containing metadata and calculated features for each IOC
    """
    FEATURES_OFFSET = 8
    result = []
    for ioc in iocs:
        days_seen_count = len(ioc["days_seen"])
        time_diffs = [date_delta(a, b) for a, b in zip(ioc["days_seen"], ioc["days_seen"][1:])]
        active_timespan = sum(time_diffs) + 1
        result.append(
            {
                # METADATA
                "value": ioc.get("name", ioc["value"]),
                "attack_count": ioc["attack_count"],
                "last_seen": ioc["last_seen"],
                "first_seen": ioc["first_seen"],
                "days_seen": ioc["days_seen"],
                # CAT FEATURES
                "asn": str(ioc["asn"]),
                "ip_reputation": ioc["ip_reputation"],
                "honeypots": ioc["honeypots"],
                # FEATURES
                "honeypot_count": len(ioc["honeypots"]),
                "destination_port_count": ioc["destination_port_count"],
                "days_seen_count": days_seen_count,
                "active_timespan": active_timespan,
                "active_days_ratio": days_seen_count / active_timespan,
                "login_attempts": ioc["login_attempts"],
                "login_attempts_per_day": ioc["login_attempts"] / days_seen_count,
                "interaction_count": ioc["interaction_count"],
                "interactions_per_day": ioc["interaction_count"] / days_seen_count,
                "avg_days_between": np.mean(time_diffs) if len(time_diffs) > 0 else 1,
                "std_days_between": np.std(time_diffs) if len(time_diffs) > 0 else 0,
                "days_since_last_seen": date_delta(ioc["last_seen"], reference_day),
                "days_since_first_seen": date_delta(ioc["first_seen"], reference_day),
            }
        )
    df = pd.DataFrame(result)
    correlation_analysis(df, list(result[0].keys())[FEATURES_OFFSET:])
    return df


def load_coa_data(file_path: str) -> dict:
    """
    Load and process Confidence of Abuse (CoA) data from a JSON file.

    This function reads a JSON file containing abuse confidence scores and
    extracts each score into a flattened dictionary format.

    Args:
        file_path (str): Path to the JSON file containing CoA data

    Returns:
        dict: A dictionary mapping IPs to their
              corresponding abuse confidence scores
    """
    with open(file_path) as f:
        j = json.load(f)
    coa_data = {}
    for elem in j:
        for k, v in elem.items():
            coa_data[k] = v["abuseConfidenceScore"]
    return coa_data


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Loads a CSV file and renames the 'ip' column to 'value'.

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame with 'ip' column renamed to 'value'
    """
    df = pd.read_csv(file_path)
    df.rename(columns={"ip": "value"}, inplace=True)
    return df


def load_txt(file_path: str) -> pd.DataFrame:
    """
    Loads a CSV file and renames the 'ip' column to 'value'.

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame with 'ip' column renamed to 'value'
    """
    entries = []
    with open(file_path) as f:
        for idx, line in enumerate(f.readlines()):
            entries.append({"value": line.strip(), "score": -idx})
    return pd.DataFrame(entries)


def min_max_normalize(df: pd.DataFrame, target_cols: list[str], lower_is_better: set[str]) -> pd.DataFrame:
    """
    Normalizes specified columns in a pandas DataFrame using min-max scaling, with special handling for metrics where lower values are better.

    The function applies min-max normalization to transform values to a 0-1 scale. For columns listed in LOWER_IS_BETTER,
    the normalization is inverted so that lower original values result in higher normalized scores (closer to 1).

    Args:
        df (pandas.DataFrame): Input DataFrame containing the columns to be normalized
        target_cols (list): List of column names to normalize. Each column must exist in df
        lower_is_better (set): Columns where lower values are better

    Returns:
        A new pandas DataFrame containing only the normalized columns. Original DataFrame remains unchanged
    """
    result = pd.DataFrame(index=df.index)
    for col in target_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        if min_val == max_val:
            result[col] = 1.0
            continue
        if col in lower_is_better:
            result[col] = (max_val - df[col]) / (max_val - min_val)
        else:
            result[col] = (df[col] - min_val) / (max_val - min_val)
    return result


def multi_label_encode(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Convert a column containing lists of values into multiple binary columns.

    For each unique value found across all lists in the specified column, creates a new
    column prefixed with 'has_' containing 1 if the value is present in the list and 0
    if it is not. The original column is dropped.

    Args:
        df: A pandas DataFrame containing the column to encode
        column_name: Name of the column containing lists of values to encode

    Returns:
        DataFrame with the original column replaced by binary columns for each unique value
    """
    result_df = df.copy()
    unique_values = set()
    for value_list in df[column_name]:
        unique_values.update(value_list)
    for value in sorted(unique_values):
        result_df[f"has_{value}"] = df[column_name].apply(lambda x: 1 if value in x else 0)
    return result_df.drop(column_name, axis=1)


def one_hot_encode(df: pd.DataFrame, column_name: str, unique_values: list, remove=True) -> pd.DataFrame:
    """
    Convert a column containing categorical values into multiple binary columns.

    For each unique value found the specified column, creates a new
    column prefixed with 'is_' containing 1 if the value is present and 0
    if it is not. The original column is dropped.

    Args:
        df: A pandas DataFrame containing the column to encode
        column_name: Name of the column containing values to encode
        unique_values: List of all possible values. If provided, ensures
                      consistent encoding even when some values are missing.

    Returns:
        DataFrame with the original column replaced by binary columns for each unique value
    """
    result_df = df.copy()
    for value in unique_values:
        column_label = f"is_{value}"
        result_df[column_label] = (df[column_name] == value).astype(int)
    return result_df.drop(column_name, axis=1) if remove else result_df


def plot_old(models: list, df: pd.DataFrame, ref_date: str, eval_date: str, percentage=False):
    """
     Create and save an interactive line plot comparing feed performances.

    Args:
        df: DataFrame with columns 'feed', 'metric', 'value', and either
            'relative feed size' or 'absolute feed size'
        ref_date: Reference date used for predictions (YYYY-MM-DD)
        eval_date: Date predictions were evaluated against (YYYY-MM-DD)
        percentage: If True, use relative feed sizes for x-axis

    Saves:
        HTML file with interactive plot named 'size_recall_n_{ref_date}_{eval_date}.html'
        Appends command line parameters as HTML comment

    Shows:
        Interactive plot in notebook/browser
    """
    title = (
        "Prediction quality of different models over a range of feed sizes.\n"
        + f"Data from {ref_date} was used to predict honeypot activity on {eval_date} and then evaluated against it."
    )
    fig = px.line(
        df,
        title=title,
        x="relative feed size" if percentage else "absolute feed size",
        y="value",
        color="feed",
        line_dash="metric",
        color_discrete_map={m.name: m.colour for m in models},
        render_mode="svg",
    )
    out_path = f"size_recall_n_{ref_date}_{eval_date}.html"
    fig.write_html(out_path)

    with open(out_path, "a") as f:
        f.write(f"\n<!-- Parameters: {' '.join(sys.argv)} -->\n")

    print(f"Plot written to {out_path}")
    fig.show()


def plot(models: list, df: pd.DataFrame, ref_date: str, eval_date: str, percentage=False):
    """
    Create and save interactive line plots comparing feed performances, with a separate plot for each metric.

    Args:
        df: DataFrame with columns 'feed', 'metric', 'value', and either
            'relative feed size' or 'absolute feed size'
        ref_date: Reference date used for predictions (YYYY-MM-DD)
        eval_date: Date predictions were evaluated against (YYYY-MM-DD)
        percentage: If True, use relative feed sizes for x-axis

    Saves:
        HTML files with interactive plots named 'size_recall_n_{metric}_{ref_date}_{eval_date}.html'
        Appends command line parameters as HTML comment

    Shows:
        Interactive plots in notebook/browser
    """
    for metric in df["metric"].unique():
        metric_df = df[df["metric"] == metric]

        title = (
            f"{metric} across different models over a range of feed sizes.\n"
            + f"Data from {ref_date} was used to predict honeypot activity on {eval_date} and then evaluated against it."
        )

        fig = px.line(
            metric_df,
            # title=title,
            x="relative feed size" if percentage else "absolute feed size",
            y="value",
            labels={
                "absolute feed size": "Absolute blocklist size k",
                "feed": "Model",
                "value": {
                    "Interaction recall": "Interaction-based recall@k",
                    "IP recall": "IP-based recall@k",
                    "IP F1 score": "IP-based F1 score",
                    "Average COA score": "Average COA score",
                }[metric],
            },
            color="feed",
            color_discrete_map={m.name: m.colour for m in models}
            | {
                "AIP Prioritize New": "fuchsia",
                "AIP Prioritize Consistent": "purple",
                "AbuseIPDB Blocklist": "red",
            },
            render_mode="svg",
        )
        fig.update_layout(xaxis_tickformat="digits")

        out_path = f"size_recall_{ref_date}_{eval_date}_{metric}.html"
        fig.write_html(out_path)

        with open(out_path, "a") as f:
            f.write(f"\n<!-- Parameters: {' '.join(sys.argv)} -->\n")

        print(f"Plot for {metric} written to {out_path}")
        fig.show()
