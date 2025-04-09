#!/bin/bash

# This script downloads blocklists from multiple source, including two GreedyBear instances. 
# To always obtain data from a completed day, run this script shortly after midnight UTC, e.g. at 00:03 UTC.

declare -A v=( )
while read -r var value; do
  v[$var]=$value
done < ./_api_keys.conf

### Download data from the GreedyBear instance at the data centre
curl -H "Authorization: Token ${v[GB_DATA_CENTRE_TOKEN]}" "http://65.109.31.113:64481/api/feeds/advanced/?feed_type=all&attack_type=scanner&max_age=30&verbose=true&feed_size=100100100" -o ./gbdump_$(date -d "today" +"%Y%m%d%H%M").json

### Download data from the GreedyBear instance at in the local network (residential internet connection)
curl -H "Authorization: Token ${v[GB_RESIDENTIAL_TOKEN]}" "http://192.168.9.183/api/feeds/advanced/?feed_type=all&attack_type=scanner&max_age=30&verbose=true&feed_size=100100100" -o ./kldump_$(date -d "today" +"%Y%m%d%H%M").json

### Download the AIP blocklists
curl "https://mcfp.felk.cvut.cz/publicDatasets/CTU-AIPP-BlackList/Latest/AIP-Prioritize_New-latest.csv" -o ./pn_$(date -d "today" +"%Y%m%d%H%M").csv
curl "https://mcfp.felk.cvut.cz/publicDatasets/CTU-AIPP-BlackList/Latest/AIP-Prioritize_Consistent-latest.csv" -o ./pc_$(date -d "today" +"%Y%m%d%H%M").csv

### Download the current AbuseIPDB blocklist
curl -G https://api.abuseipdb.com/api/v2/blacklist?ipVersion=4 -H "Accept: text/plain" -H "Key: ${v[ABUSEIPDB_TOKEN]}" -o ./aipdb_$(date -d "today" +"%Y%m%d%H%M").txt

### Run the script that obains the current confidence of abuse scores from AbuseIPDB
python3 ./_get_abuseipdb_scores.py