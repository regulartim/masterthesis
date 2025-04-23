from itertools import product

import numpy as np
from clustering.similarity import compute_similarity_matrix, jaccard_similarity, ratcliff_obershelp_similarity
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.metrics.cluster import rand_score

ALGORITHMS = [
    {
        "name": "Agglomerative Clustering (average linkage)",
        "class": AgglomerativeClustering,
        "param_searchspace": {
            "similarity_fn": [jaccard_similarity, ratcliff_obershelp_similarity],
            "distance_threshold": np.linspace(0, 1, 100, endpoint=False),
            "linkage": ["average"],
            "n_clusters": [None],
        },
        "optimum_params": {
            "similarity_fn": jaccard_similarity,
            "distance_threshold": 0.56,
            "linkage": "average",
            "n_clusters": None,
        },
    },
    {
        "name": "Agglomerative Clustering (complete linkage)",
        "class": AgglomerativeClustering,
        "param_searchspace": {
            "similarity_fn": [jaccard_similarity, ratcliff_obershelp_similarity],
            "distance_threshold": np.linspace(0, 1, 100, endpoint=False),
            "linkage": ["complete"],
            "n_clusters": [None],
        },
        "optimum_params": {
            "similarity_fn": jaccard_similarity,
            "distance_threshold": 0.57,
            "linkage": "complete",
            "n_clusters": None,
        },
    },
    {
        "name": "Agglomerative Clustering (single linkage)",
        "class": AgglomerativeClustering,
        "param_searchspace": {
            "similarity_fn": [jaccard_similarity, ratcliff_obershelp_similarity],
            "distance_threshold": np.linspace(0, 1, 100, endpoint=False),
            "linkage": ["single"],
            "n_clusters": [None],
        },
        "optimum_params": {
            "similarity_fn": jaccard_similarity,
            "distance_threshold": 0.52,
            "linkage": "single",
            "n_clusters": None,
        },
    },
    {
        "name": "DBSCAN Clustering",
        "class": DBSCAN,
        "param_searchspace": {
            "similarity_fn": [jaccard_similarity, ratcliff_obershelp_similarity],
            "eps": np.linspace(0.01, 1, 100),
            "min_samples": [1],
        },
        "optimum_params": {
            "similarity_fn": jaccard_similarity,
            "eps": 0.5,
            "min_samples": 1,
        },
    },
]


def perform_clustering(sequences: list[list[str]], algorithm, params: dict) -> list[int]:
    """
    Perform clustering on a list of sequences using the specified algorithm and parameters.

    Args:
        sequences: List of tokenized sequences to cluster, where each sequence
                    is represented as a list of strings
        algorithm: The clustering algorithm class from scikit-learn
                    that will be instantiated with the provided parameters
        params: Dictionary of parameters for the clustering algorithm, must include:
                - 'similarity_fn': Function to compute similarity between sequences
                - Additional parameters specific to the algorithm

    Returns:
        list[int]: Cluster labels for each input sequence. The length of the returned list
                  matches the length of the input sequences.
    """
    similarity_matrix = compute_similarity_matrix(sequences, params["similarity_fn"])
    distance_matrix = 1 - similarity_matrix
    params = {k: v for k, v in params.items() if k != "similarity_fn"}
    return list(algorithm(metric="precomputed", **params).fit_predict(distance_matrix))


def hyperparam_search(tokenized_seqs: list[list[str]], true_labels: list[int]) -> tuple[float, list[dict]]:
    """
    Perform hyperparameter search across multiple clustering algorithms to find optimal parameters.

    This function conducts an exhaustive grid search over the parameter spaces defined in the
    global ALGORITHMS configuration. It evaluates each parameter combination against ground
    truth labels using the Rand score metric, which measures the similarity between two clusterings.
    The function returns the highest achieved score and all parameter combinations that reached
    that score.

    Parameters:
        tokenized_seqs: List of tokenized sequences to cluster, where each sequence
                        is represented as a list of strings
        true_labels: Ground truth cluster assignments for each sequence in tokenized_seqs.
                     Used to evaluate the quality of clustering results.

    Returns:
        tuple: A 2-element tuple containing:
            - float: The highest Rand score achieved across all parameter combinations
            - list[dict]: List of parameter dictionaries that achieved the highest score.
    """
    winners = (0, [])
    for algorithm in ALGORITHMS:
        param_combinations = [dict(zip(algorithm["param_searchspace"].keys(), v)) for v in product(*algorithm["param_searchspace"].values())]
        for candidate in param_combinations:
            cluster_labels = perform_clustering(tokenized_seqs, algorithm["class"], candidate)
            score = rand_score(true_labels, cluster_labels)
            candidate["algorithm"] = algorithm["name"]
            if score == winners[0]:
                winners[1].append(candidate)
            if score > winners[0]:
                winners = (score, [candidate])
    return winners
