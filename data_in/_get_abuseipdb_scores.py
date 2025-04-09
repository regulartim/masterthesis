"""
A script for checking IP addresses against the AbuseIPDB API to retrieve reputation scores and threat information
and writing out this information to a json file.
"""
import asyncio
import json
import os
from datetime import datetime

import aiohttp

API_URL = "https://api.abuseipdb.com/api/v2/check"
API_KEY_FILE = "./_api_keys.conf"


def read_api_key() -> str:
    """
    Read the AbuseIPDB API key from the configuration file.

    This function parses the API key configuration file and extracts the
    AbuseIPDB token value from a line that starts with 'ABUSEIPDB_TOKEN'.

    Returns:
        str or None: The API key if found, None otherwise.

    Note:
        The configuration file is expected to be at the path defined by
        the API_KEY_FILE constant, with the format 'ABUSEIPDB_TOKEN <api_key>'.
    """
    with open(API_KEY_FILE, "r") as f:
        for line in f:
            if line.startswith("ABUSEIPDB_TOKEN"):
                return line.strip().split()[-1]
    return None


async def check_single_ip(session: aiohttp.ClientSession, ip: str, api_key: str) -> dict:
    """
    Check a single IP address against the AbuseIPDB API.

    This function makes an asynchronous HTTP request to the AbuseIPDB API to
    retrieve abuse confidence score and other data about the specified IP address.

    Args:
        session (aiohttp.ClientSession): An active aiohttp session for making the request.
        ip (str): The IP address to check.
        api_key (str): The AbuseIPDB API key for authentication.

    Returns:
        dict or None: A dictionary with the IP address as the key and the API response
                     data as the value if successful, None if the request fails.
    """
    headers = {"Accept": "application/json", "Key": api_key}
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    try:
        async with session.get(API_URL, headers=headers, params=params) as response:
            response.raise_for_status()
            res = await response.json()
            return {ip: res["data"]}
    except Exception as e:
        print(f"Error checking IP {ip}: {e}")
        return None


async def check_ip_addresses_async(ip_addresses: list, api_key: str, limit: int) -> list[dict]:
    """
    Asynchronously check multiple IP addresses against the AbuseIPDB API.
    
    This function creates concurrent tasks to check multiple IP addresses, while
    limiting the number of simultaneous connections to avoid overwhelming the API
    or triggering rate limits.
    
    Args:
        ip_addresses (list): A list of IP addresses as strings to check.
        api_key (str): The AbuseIPDB API key for authentication.
        limit (int): Maximum number of IP addresses to check. If limit > 0,
                     only the first 'limit' addresses will be processed.
                     If limit = 0, all IP addresses are processed.
    
    Returns:
        list: A list of dictionaries containing the results for each successfully
              checked IP address. Failed requests are excluded from the results.
              Each dictionary has the format {ip: response_data}.
    """
    if limit > 0:
        ip_addresses = ip_addresses[:limit]

    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(20)

    async def check_with_semaphore(ip: str) -> dict:
        async with semaphore:
            return await check_single_ip(session, ip, api_key)

    # Create async tasks for each IP
    async with aiohttp.ClientSession() as session:
        tasks = [check_with_semaphore(ip) for ip in ip_addresses]
        results = await asyncio.gather(*tasks)

    # Filter out None values (failed requests) and create DataFrame
    valid_results = [r for r in results if r is not None]
    return valid_results


def check_ip_addresses(ip_addresses: list, api_key: str, limit: int = 0) -> list[dict]:
    """
    Check multiple IP addresses against the AbuseIPDB API.
    
    This function serves as a synchronous wrapper around the asynchronous
    implementation, making it easier to use in non-async code contexts.
    
    Args:
        ip_addresses (list): A list of IP addresses as strings to check.
        api_key (str): The AbuseIPDB API key for authentication.
        limit (int, optional): Maximum number of IP addresses to check. 
                               If limit > 0, only the first 'limit' addresses will be processed.
                               If limit = 0 (default), all IP addresses are processed.
    
    Returns:
        list: A list of dictionaries containing the results for each successfully
              checked IP address. Failed requests are excluded from the results.
              Each dictionary has the format {ip: response_data}.
    """
    return asyncio.run(check_ip_addresses_async(ip_addresses, api_key, limit))


if __name__ == "__main__":
    greedybear_feeds = [f for f in os.listdir() if f.startswith("gbdump_") and f.endswith(".json")]
    newest = sorted(greedybear_feeds)[-1]

    with open(newest, "r") as f:
        data = json.load(f)

    api_key = read_api_key()

    ips = [ioc["value"] for ioc in data["iocs"]]
    ratings = check_ip_addresses(ips, , 50000)

    out_file = f"aipdscores_{datetime.now().strftime('%Y%m%d%H%M')}.json"
    with open(out_file, "w") as f:
        json.dump(ratings, f, indent=4)
