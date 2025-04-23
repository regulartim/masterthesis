import datetime
import os
import re
import subprocess

import pandas as pd

K_MAX = 10_000
DATA_FOLDER = "./data_in/"


def get_files() -> list:
    """
    Retrieve a sorted list of files from the DATA_FOLDER directory.

    This function scans the directory specified by the global DATA_FOLDER
    constant and returns only the regular files (not directories) found within it.

    Returns:
        A sorted list of filenames (as strings) that exist in the DATA_FOLDER directory.
    """
    return sorted([f for f in os.listdir(DATA_FOLDER) if os.path.isfile(os.path.join(DATA_FOLDER, f))])


def get_date_from_filename(filename: str) -> datetime.date:
    """
    Extract and parse a date from a filename containing an 8-digit date string.

    The function looks for an 8-digit sequence in the filename (format YYYYMMDD)
    and converts it to a date object.

    Args:
        filename (str): The filename containing an 8-digit date string (YYYYMMDD).

    Returns:
        The parsed date from the filename.
    """
    match = re.findall(r"(\d{8})", filename)[0]
    return datetime.datetime.strptime(match, "%Y%m%d").date()


def process_evaluation_result(res: subprocess.CompletedProcess, score_date: datetime.date, ev_type: str, excl_mass: bool) -> list[dict]:
    """
    Process and normalize model evaluation results from subprocess output.

    This function parses the stdout from an evaluation subprocess, extracts performance
    metrics for different models, and creates two sets of records:
    1. Original metrics as reported in the output
    2. Normalized metrics where each value is divided by the corresponding "Upper Bound" model value

    Args:
        res: The completed subprocess result containing stdout output
        score_date: The date associated with the evaluation scores
        ev_type: The evaluation type identifier (e.g., 'gb', 'kl')
        excl_mass: Flag indicating whether mass was excluded in the evaluation

    Returns:
        list[dict]: A list of dictionaries containing both the original and normalized
                   evaluation metrics for each model. Each dictionary contains model name,
                   evaluation metadata, and performance metrics.
    """
    r = []
    for line in res.stdout.split("\n"):
        if "recall" not in line:
            continue
        model = line.split("|")[0].strip()
        ip_recall, ia_recall, f1, ip_auc, ia_auc, coa_auc = list(map(float, re.findall(r"(\d{1,2}\.\d+)", line)))
        r.append(
            {
                "model": model,
                "date": score_date,
                "loc": ev_type,
                "norm": False,
                "excl_mass": excl_mass,
                "size": K_MAX,
                "ip_recall": ip_recall,
                "ia_recall": ia_recall,
                "f1": f1,
                "ip_auc": ip_auc,
                "ia_auc": ia_auc,
                "coa_auc": coa_auc,
            }
        )
    s = []
    upper = next(d for d in r if d["model"] == "Upper Bound")
    for d in r:
        s.append(
            d
            | {
                "norm": True,
                "ip_recall": d["ip_recall"] / upper["ip_recall"],
                "ia_recall": d["ia_recall"] / upper["ia_recall"],
                "f1": d["f1"] / upper["f1"],
                "ip_auc": d["ip_auc"] / upper["ip_auc"],
                "ia_auc": d["ia_auc"] / upper["ia_auc"],
            }
        )
    return r + s


def run():
    out_data = []

    ### BUILD EVALUATION DATA
    kl_files = [f for f in get_files() if f.startswith("kldump")]
    for file_a, file_b in zip(kl_files, kl_files[1:]):
        out_file_name = DATA_FOLDER + "delta_" + file_b
        if os.path.exists(out_file_name):
            continue
        result = subprocess.run(["python3", "create_delta_file.py", DATA_FOLDER + file_a, DATA_FOLDER + file_b, out_file_name], capture_output=True, text=True)
        print(result)

    ### GET RELEVANT FILES
    main_files = [f for f in get_files() if f.startswith("gbdump")]
    kl_files = [f for f in get_files() if f.startswith("delta_kldump")]
    adb_blocklist_files = [f for f in get_files() if f.startswith("aipdb_")]
    adb_score_files = [f for f in get_files() if f.startswith("aipdscores_")]

    for train, score, eval_i, eval_kl, adbb, adbs in zip(main_files, main_files[1:], main_files[2:], kl_files, adb_blocklist_files, adb_score_files):
        assert (
            get_date_from_filename(train) + datetime.timedelta(days=2)
            == get_date_from_filename(score) + datetime.timedelta(days=1)
            == get_date_from_filename(eval_i)
            == get_date_from_filename(eval_kl)
            == get_date_from_filename(adbb)
            == get_date_from_filename(adbs)
        )

        # TRAIN
        print(f"Train models with data {train} and {score}.")
        result = subprocess.run(["python3", "train_models.py", "-d", DATA_FOLDER + train, "-t", DATA_FOLDER + score], capture_output=True, text=True)
        assert result.returncode == 0

        # TEST
        print(f"Test scoring performance based on {score}.")

        result = subprocess.run(
            [
                "python3",
                "evaluate_single_day.py",
                "-s",
                DATA_FOLDER + score,
                "-e",
                DATA_FOLDER + eval_i,
                "-a",
                DATA_FOLDER + adbb,
                "--test-sizes-up-to",
                str(K_MAX),
                "--coa",
                DATA_FOLDER + adbs,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        out_data.extend(process_evaluation_result(result, get_date_from_filename(score), "gb", False))
        result = subprocess.run(
            [
                "python3",
                "evaluate_single_day.py",
                "-s",
                DATA_FOLDER + score,
                "-e",
                DATA_FOLDER + eval_kl,
                "-a",
                DATA_FOLDER + adbb,
                "--delta",
                "--test-sizes-up-to",
                str(K_MAX),
                "--coa",
                DATA_FOLDER + adbs,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        out_data.extend(process_evaluation_result(result, get_date_from_filename(score), "kl", False))
        result = subprocess.run(
            [
                "python3",
                "evaluate_single_day.py",
                "-s",
                DATA_FOLDER + score,
                "-e",
                DATA_FOLDER + eval_i,
                "-a",
                DATA_FOLDER + adbb,
                "--test-sizes-up-to",
                str(K_MAX),
                "--coa",
                DATA_FOLDER + adbs,
                "-m",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        out_data.extend(process_evaluation_result(result, get_date_from_filename(score), "gb", True))
        result = subprocess.run(
            [
                "python3",
                "evaluate_single_day.py",
                "-s",
                DATA_FOLDER + score,
                "-e",
                DATA_FOLDER + eval_kl,
                "-a",
                DATA_FOLDER + adbb,
                "--delta",
                "--test-sizes-up-to",
                str(K_MAX),
                "--coa",
                DATA_FOLDER + adbs,
                "-m",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        out_data.extend(process_evaluation_result(result, get_date_from_filename(score), "kl", True))

    pd.DataFrame(out_data).to_csv("./data_out/eval_results.csv", index=False)


if __name__ == "main":
    run()
