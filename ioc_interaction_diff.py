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

from greedybear_utils import calculate_interaction_delta, read_dump

*_, file_a, file_b, out_file_name = sys.argv

a, b = read_dump(file_a), read_dump(file_b)
date_a = max(row["last_seen"] for row in a)
date_b = max(row["last_seen"] for row in b)
assert date_a < date_b

result = calculate_interaction_delta(a, date_a, b)

# write result
print(f"writing {len(result)} records to {out_file_name}")
with open(out_file_name, "w") as file:
    json.dump({"iocs": result, "date": date_b}, file)
