import argparse

from clustering.algorithms import hyperparam_search
from clustering.benchmarks import benchmark_clustering_functions, benchmark_similarity_functions, print_benchmark_results
from clustering.ground_truth import GROUND_TRUTH
from clustering.similarity import jaccard_similarity, ratcliff_obershelp_similarity


def tokenize(sequence: list[str]) -> list[str]:
    """
    Tokenize a sequence of strings into a flat list of tokens.

    This function processes each string in the input sequence by:
    1. Replacing semicolons (;) with spaces
    2. Splitting the resulting string by whitespace
    3. Concatenating all tokens into a single flat list

    Args:
        sequence (list[str]): A list of strings to tokenize

    Returns:
        list[str]: A flat list containing all tokens extracted from the input sequence
    """
    result = []
    for line in sequence:
        result.extend(line.replace(";", " ").split())
    return result


def evaluate_clustering_quality():
    """
    Evaluate clustering quality by finding optimal clustering parameters using ground truth data.

    This function performs the following steps:
    1. Loads ground truth data with predefined cluster labels from GROUND_TRUTH
    2. Extracts true labels and corresponding sequences
    3. Tokenizes each sequence using the tokenize() function
    4. Performs hyperparameter search across multiple clustering algorithms
       and similarity functions to find the optimal combination
    5. Prints the highest achieved Rand index and all parameter combinations
       that achieved this score

    The function uses the Rand index as a metric, which measures the similarity
    between the clustering produced by different parameter combinations and the
    ground truth clustering. A higher Rand index indicates better clustering quality.
    """
    print("reading ground truth")
    true_labels = [e[0] for e in GROUND_TRUTH]
    sequences = [e[1] for e in GROUND_TRUTH]
    print("tokenizing")
    tokenized_seqs = [tokenize([s]) for s in sequences]
    print("serching for the optimum combination of algorithm, parameters and similarity function")
    winners = hyperparam_search(tokenized_seqs, true_labels)
    print(f"highest rand index of {winners[0]} was achived by these combinations:")
    for combination in winners[1]:
        combination_str = "; ".join(f"{k}: {str(v.__name__)}" if k == "similarity_fn" else f"{k}: {str(v)}" for k, v in combination.items())
        print(combination_str)


def benchmark_similarity_efficiency():
    """
    Benchmark the computational efficiency of different similarity functions.

    This function measures the performance of multiple similarity functions (specifically,
    jaccard_similarity and ratcliff_obershelp_similarity) by running them on randomly
    generated sequence data and measuring execution times.
    """
    similarity_fns = [jaccard_similarity, ratcliff_obershelp_similarity]
    results = benchmark_similarity_functions(similarity_fns, n_sequences=1000, seq_length_range=(10, 100), n_trials=3)
    print_benchmark_results(results)


def benchmark_clustering_efficiency():
    """
    Benchmark the computational efficiency of different clustering algorithms.

    This function measures the performance of clustering algorithms defined in the
    ALGORITHMS configuration by applying them to randomly generated sequence data and
    measuring execution times. All algorithms are benchmarked using jaccard_similarity
    as the similarity measure.

    The benchmark parameters (such as number of sequences, sequence lengths, and number
    of trials) are defined within the benchmark_clustering_functions implementation.
    """
    results = benchmark_clustering_functions(similarity_fn=jaccard_similarity)
    print_benchmark_results(results)


def run():
    """
    Entry point for the clustering evaluation command-line interface.

    This function parses command-line arguments and executes the requested
    evaluation operations.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)

    parser.add_argument(
        "--quality",
        help="Perform hyperparameter search to find optimum combination of measure, algorithm and parameters.",
        action="store_true",
    )

    parser.add_argument(
        "--similarity-benchmark",
        help="Perform benchmark to assess the efficiency of different similarity functions.",
        action="store_true",
    )

    parser.add_argument(
        "--algorithm-benchmark",
        help="Perform benchmark to assess the efficiency of different clustering algorithms.",
        action="store_true",
    )

    config = vars(parser.parse_args())

    if not any(config.values()):
        parser.print_help()
        print("\nNo arguments provided. Please specify at least one action to perform.")

    if config["quality"]:
        print("evaluating clustering quality")
        evaluate_clustering_quality()
        print()
    if config["similarity_benchmark"]:
        print("evaluating efficiency of similarity functions")
        benchmark_similarity_efficiency()
        print()
    if config["algorithm_benchmark"]:
        print("evaluating efficiency of clustering algorithms")
        benchmark_clustering_efficiency()


if __name__ == "__main__":
    run()
