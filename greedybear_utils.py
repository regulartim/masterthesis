import json
from collections import defaultdict


def read_dump(file_path: str, only_scanners: bool = True, exclude_mass_scanners: bool = False) -> list[dict]:
    """
    Read and filter IOC data from a GreedyBear API dump.

    This function loads IOC data from a specified JSON file and applies filtering
    based on scanner status and reputation.

    Args:
        file_path (str): Path to the JSON file containing IOC data.
        only_scanners (bool, optional): If True, only include IOCs marked as scanners.
            Defaults to True.
        exclude_mass_scanners (bool, optional): If True, exclude IOCs with
            "mass scanner" reputation. Defaults to False.

    Returns:
        list[dict]: Filtered list of IOC dictionaries.
    """
    print("reading", file_path)
    with open(file_path, "r") as file:
        data = json.load(file)["iocs"]
    if only_scanners:
        data = [ioc for ioc in data if ioc["scanner"]]
    if exclude_mass_scanners:
        data = [ioc for ioc in data if ioc["ip_reputation"] != "mass scanner"]
    data = [ioc for ioc in data if ioc["value"]]
    print(f"got {len(data)} records")
    return data


def read_delta_file(file_path: str) -> tuple[dict, str]:
    """
    Read a previously created delta file.

    This function loads data from a specified JSON file
    that was previously created by the create_delta_file.py script.

    Args:
        file_path (str): Path to the JSON file containing the data.

    Returns:
        tuple[dict, str]: Mapping from IP addresses to their number of interactions
                          and the date of the day the data was recorded.
    """
    print("reading", file_path)
    with open(file_path, "r") as file:
        content = json.load(file)
    data, date = content["iocs"], content["date"]
    print(f"got {len(data)} records")
    return data, date


def calculate_interaction_delta(baseline: list[dict], baseline_date: str, recent: list[dict]) -> defaultdict[str, int]:
    """
    Calculate the change in interaction counts for IOCs seen after a specified date.

    This function compares two GreedyBear dumps from the Feeds API and returns
    the difference in interaction counts for IOCs that have been seen more recently
    than the baseline date.

    Args:
        baseline (list[dict]): Reference set of IOC data. Each dictionary should contain
                              at least 'value' and 'interaction_count' keys.
        baseline_date (str): Date string used to filter recent IOCs. Only IOCs with
                            'last_seen' dates greater than this will be included.
        recent (list[dict]): Current set of IOC data to compare against the baseline.
                            Each dictionary should contain at least 'value',
                            'interaction_count', and 'last_seen' keys.

    Returns:
        defaultdict[str, int]: A dictionary mapping IOC values to their change in
                              interaction count. Only includes IOCs from the recent data
                              that were seen after the baseline_date. Returns 0 for
                              any IOC value not in the result.
    """
    baseline_interactions_by_ip = defaultdict(int, {ioc["value"]: ioc["interaction_count"] for ioc in baseline})
    result = {ioc["value"]: ioc["interaction_count"] - baseline_interactions_by_ip[ioc["value"]] for ioc in recent if ioc["last_seen"] > baseline_date}
    return defaultdict(int, result)
