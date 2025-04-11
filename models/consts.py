SEARCH_N_ITER = 100
SEARCH_CV = 5
SEARCH_VERBOSITY = 1

ML_FEATURES = [
    "honeypot_count",
    "destination_port_count",
    "days_seen_count",
    # "active_timespan",
    # "active_days_ratio",
    "login_attempts",
    "login_attempts_per_day",
    "interaction_count",
    "interactions_per_day",
    "avg_days_between",
    "std_days_between",
    "days_since_last_seen",
    "days_since_first_seen",
]

CATEGORICAL_FEATURES = [
    "asn",
    "ip_reputation",
]

MULTI_VAL_FEATURES = [
    "honeypots",
]

IP_REPUTATIONS = [
    "known attacker",
    "mass scanner",
    "bot, crawler",
    "tor exit node",
    "form spammer",
    "anonymizer",
    "bitcoin node",
]

MAX_K = 10_000
SAMPLE_COUNT = 100
