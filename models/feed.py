from collections import defaultdict
from statistics import mean

import numpy as np
import pandas as pd

DEBUG_FEATURES =["value", "last_seen", "days_seen", "active_days_ratio", "days_seen_count", "avg_days_between", "std_days_between", "days_since_last_seen", "interactions_per_day", "interactions_on_eval_day", "rfc_score",]
METRICS = ["Interaction recall","IP recall","IP F1 score", "Average COA score"]

class Feed:
    def __init__(self, name: str, data: pd.DataFrame, size: int, sort_key: str, eval_ips:dict=None, coa_scores:dict=None):
        self.name = name
        if sort_key == "randomize":
            self.data = data.sample(frac=1)
        else:
            self.data = data.sort_values(by=sort_key, ascending=False)
        self.size = min(size, len(data))
        self.metrics = {}
        self.known_ip_count = len(self.data)
        self.fn_ips_count = 0
        self.fn_ias_count = 0
        if eval_ips is not None:
            in_feed = set(self.data["value"])
            not_in_feed = {ip: v for ip, v in eval_ips.items() if ip not in in_feed}
            self.fn_ips_count += len(not_in_feed)
            self.fn_ias_count += sum(not_in_feed.values())
        self.coa_scores = defaultdict(int, coa_scores) if coa_scores else None


    def __repr__(self):
        res = f"{self.name.ljust(32)}| size: {self.size:>5} | recall: {self.metrics["ip_recall"]:.4f} / {self.metrics["interaction_recall"]:.4f} | F1: {self.metrics["ip_f1_score"]:.4f}"
        if "ip_recall_auc" in self.metrics:
            res += f" | ipAUC: {self.metrics["ip_recall_auc"]:.4f}"

        if "interaction_recall_auc" in self.metrics:
            res += f" | iaAUC: {self.metrics["interaction_recall_auc"]:.4f}"

        if self.coa_scores:
            res += f" | coaAUC: {self.metrics["avg_coa_auc"]:.4f}"
        return res

    def exclude(self, predicate):
        excluded = self.data.loc[predicate]
        self.known_ip_count +=len(excluded)
        self.fn_ips_count += excluded.loc[excluded["interactions_on_eval_day"] > 0].shape[0]
        self.fn_ias_count+=sum(excluded["interactions_on_eval_day"])
        self.data = self.data.loc[~predicate]

    def set_size(self, size:int):
        self.size = min(size, len(self.data))

    def show_false_positives(self):
        print(self.data.iloc[:self.size].loc[self.data["interactions_on_eval_day"] == 0].head(50)[DEBUG_FEATURES])

    def show_false_negatives(self):
        print(self.data.iloc[self.size:].loc[self.data["interactions_on_eval_day"] >  0].head(50)[DEBUG_FEATURES])

    def evaluate(self):
        self.metrics["ip_tp"]  = self.data.iloc[:self.size].loc[self.data["interactions_on_eval_day"] >  0].shape[0]
        self.metrics["ip_fp"]  = self.data.iloc[:self.size].loc[self.data["interactions_on_eval_day"] == 0].shape[0]
        self.metrics["ip_fn"]  = self.data.iloc[self.size:].loc[self.data["interactions_on_eval_day"] >  0].shape[0]
        self.metrics["ip_fn"] += self.fn_ips_count
        self.metrics["ip_precision"] = self.metrics["ip_tp"] / (
            self.metrics["ip_tp"] + self.metrics["ip_fp"]
        )
        self.metrics["ip_recall"] = self.metrics["ip_tp"] / (
            self.metrics["ip_tp"] + self.metrics["ip_fn"]
        )
        self.metrics["ip_f1_score"] = 2*self.metrics["ip_tp"] / (
            2*self.metrics["ip_tp"]+ self.metrics["ip_fp"] + self.metrics["ip_fn"]
        )
        self.metrics["interaction_tp"]  = sum(self.data.iloc[:self.size]["interactions_on_eval_day"])
        self.metrics["interaction_fn"]  = sum(self.data.iloc[self.size:]["interactions_on_eval_day"])
        self.metrics["interaction_fn"] += self.fn_ias_count
        self.metrics["interaction_recall"] = self.metrics["interaction_tp"] / (
            self.metrics["interaction_tp"] + self.metrics["interaction_fn"]
        )
        if self.coa_scores:
            self.metrics["average_coa_score"] = mean(self.coa_scores[ip] for ip in self.data.iloc[:self.size]["value"])

    def evaluate_range(self, stop: int, samples:int=100) -> list:
        results = []
        
        for i in range(0,stop,stop//samples):
            self.set_size(i+ stop//samples)
            self.evaluate()
            metadata = {"feed": f"{self.name}", "absolute feed size": self.size, "relative feed size": self.size/self.known_ip_count}
            for metric in METRICS:
                metric_key = metric.replace(" ", "_").lower()
                if metric_key not in self.metrics:
                    continue
                data = {"value": self.metrics[metric_key], "metric": metric}
                results.append(metadata | data)
        ip_recalls =[r["value"] for r in results if r["metric"]=="IP recall"]
        ia_recalls =[r["value"] for r in results if r["metric"]=="Interaction recall"]
        avg_coa_scores =[r["value"] for r in results if r["metric"]=="Average COA score"]
        self.metrics["ip_recall_auc"] = np.trapz([0] + ip_recalls) / samples
        self.metrics["interaction_recall_auc"] = np.trapz([0] + ia_recalls) / samples
        self.metrics["avg_coa_auc"] = np.trapz([0] + avg_coa_scores) / samples
        return results

    def dump_to_txt(self):
        file_name = f"{self.name.replace(" ", "_").lower()}_{self.size}.txt"
        ips = self.data.iloc[:self.size]["value"].to_list()
        with open(f"./lists/{file_name}", "w") as f:
            f.write("\n".join(ips))
