"""
Interaction difference calculation

GreedyBear only saves a cumulated interaction count. 
That's why it is ofen not possible to determine
how often a specific IoC interacted with any honeypot on a single day. 
This script takes an earlier and a more recent GreedyBear dataset 
and computes the difference in interaction counts between the two.

Usage:
    python ioc_interaction_diff.py file_a file_b output_file

    Where:
        file_a: JSON file containing the earlier dataset
        file_b: JSON file containing the more recent dataset
        output_file: Destination file for the differential results

Input file format:
    Each input file should contain a JSON object with an "iocs" key that maps to a list of IoC objects. 
    (Which is the default for GreedyBear API responses.)
    Each IoC object must have the following keys:
        - "value": The IoC identifier (typically an IP address)
        - "scanner": Boolean indicating if the IoC was a scanner
        - "interaction_count": Total number of interactions recorded
        - "last_seen": Timestamp of the last observed activity

Output file format:
    A JSON object containing:
        - "iocs": A dictionary mapping IoC values to their incremental interaction counts in the newer dataset
        - "date": The most recent timestamp from the newer dataset

Notes:
    - IoCs with empty values are excluded as they may result from a known (and fixed) bug in GreedyBear
    - Only scanner-type IoCs are included in the analysis (payload requests are filtered out)
    - The module verifies that file_a's data predates file_b's data
"""
import json
import sys


def load_data(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)["iocs"]
        # filter out IoCs that were payload requests
        data = [ioc for ioc in data if ioc["scanner"]]
    return data


*_, file_a, file_b, out_file_name = sys.argv

a, b = load_data(file_a), load_data(file_b)
date_a = max(row["last_seen"] for row in a)
date_b = max(row["last_seen"] for row in b)
assert date_a < date_b

# build a mapping from IoC to its cumulated interaction count including day A
ips_in_a = {ioc["value"]: ioc["interaction_count"] for ioc in a}
result = {}
for ioc in b:
    # ignore IoCs that were not seen on day B
    if ioc["last_seen"] < date_b:
        continue
    # ignore IoCs that do not have an IP address
    # this happend sometimes due to a bug in GreedyBear
    if ioc["value"] == "":
        continue
    # filter out IoCs that were payload requests
    if not ioc["scanner"]:
        continue
    # save the number of interactions on day B that an IoC was responsible for
    result[ioc["value"]] = ioc["interaction_count"] - ips_in_a.get(ioc["value"], 0)

# write result
with open(out_file_name, "w") as file:
    json.dump({"iocs": result, "date": date_b}, file)
