from models.base_model import Model
from models.utils import min_max_normalize

COMMON_WEIGHTS = {
    "honeypot_count": 0.05,
    "destination_port_count": 0.05,
}

PC_WEIGHTS = COMMON_WEIGHTS | {
    "days_seen_count": 0.15,
    "active_days_ratio": 0.15,
    "login_attempts": 0.05,
    "login_attempts_per_day": 0.15,
    "interaction_count": 0.05,
    "interactions_per_day": 0.15,
    "avg_days_between": 0.1,
    "std_days_between": 0.1,
}

PN_WEIGHTS = COMMON_WEIGHTS | {
    "days_seen_count": 0.05,
    "active_days_ratio": 0.05,
    "login_attempts": 0.3,
    "login_attempts_per_day": 0.05,
    "interaction_count": 0.3,
    "interactions_per_day": 0.05,
    "avg_days_between": 0.05,
    "std_days_between": 0.05,
}

LOWER_IS_BETTER = {"avg_days_between", "std_days_between"}

assert sum(PC_WEIGHTS.values()) == 1
assert sum(PN_WEIGHTS.values()) == 1


def aip_linear_scoring(row: dict, weights: dict, aging_factor: float) -> float:
    score = sum(row[col] * weight for col, weight in weights.items())
    return aging_factor * score


class AIPLinear(Model):
    def prioritize_consistent(self, row: dict) -> float:
        """
        The Prioritize Consistent algorithm is designed to give higher scores to IP addresses
        that consistently attack the network over a long period.
        """
        aging_factor = 1 - row["days_since_last_seen"] / (row["days_since_last_seen"] + row["active_timespan"])
        return aip_linear_scoring(row, PC_WEIGHTS, aging_factor)

    def prioritize_new(self, row: dict) -> float:
        """
        The Prioritize New algorithm is designed to give higher scores to IP addresses
        that are new and aggressively attacking the network over a short period.
        """
        aging_factor = 2 / (2 + row["days_since_last_seen"])
        return aip_linear_scoring(row, PN_WEIGHTS, aging_factor)

    def execute(self, df):
        normalised_df = min_max_normalize(df, PC_WEIGHTS.keys(), LOWER_IS_BETTER)
        normalised_df["days_since_last_seen"] = df["days_since_last_seen"]
        normalised_df["active_timespan"] = df["active_timespan"]
        df["pc_score"] = normalised_df.apply(self.prioritize_consistent, axis=1)
        df["pn_score"] = normalised_df.apply(self.prioritize_new, axis=1)
        return df
