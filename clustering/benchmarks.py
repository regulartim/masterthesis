import random
import string
from statistics import mean, stdev
from time import perf_counter

from clustering.algorithms import ALGORITHMS
from clustering.similarity import compute_similarity_matrix


def generate_benchmark_sequences(
    n_sequences: int = 10_000, min_tokens: int = 5, max_tokens: int = 50, token_length_range: tuple = (3, 10), vocabulary_size: int = 500
) -> list[list[str]]:
    """
    Generate a collection of tokenized sequences for benchmarking.

    Args:
        n_sequences: Number of sequences to generate
        min_tokens: Minimum number of tokens per sequence
        max_tokens: Maximum number of tokens per sequence
        token_length_range: (min_length, max_length) for generated tokens
        vocabulary_size: Size of the synthetic vocabulary to draw from

    Returns:
        List of tokenized sequences, where each sequence is a list of string tokens
    """
    # Generate a synthetic vocabulary
    vocabulary = []
    for _ in range(vocabulary_size):
        token_length = random.randint(*token_length_range)
        token = "".join(random.choice(string.ascii_lowercase) for _ in range(token_length))
        vocabulary.append(token)

    # Generate sequences using the vocabulary
    sequences = []
    for _ in range(n_sequences):
        seq_length = random.randint(min_tokens, max_tokens)
        sequence = []
        for _ in range(seq_length):
            token = random.choice(vocabulary)
            sequence.append(token)
        sequences.append(sequence)
    return sequences


def benchmark_clustering_functions(similarity_fn, n_trials: int = 5) -> list[dict]:
    """
    Benchmark clustering algorithms by measuring their runtime performance.

    Args:
        similarity_fn: Similarity function to use for all clustering algorithms
        n_trials: Number of times to repeat each benchmark

    Returns:
        List of benchmark results for each clustering function
    """
    results = []
    sequences = generate_benchmark_sequences()
    print("pre-calculating distance matrix")
    similarity_matrix = compute_similarity_matrix(sequences, similarity_fn)
    distance_matrix = 1 - similarity_matrix

    for algorithm in ALGORITHMS:
        print(f"testing {algorithm['name']}")
        params = {k: v for k, v in algorithm["optimum_params"].items() if k != "similarity_fn"}
        trial_times = []
        for _ in range(n_trials):
            start_time = perf_counter()
            algorithm["class"](metric="precomputed", **params).fit_predict(distance_matrix)
            elapsed = perf_counter() - start_time
            trial_times.append(elapsed)

        # Calculate statistics
        results.append(
            {
                "algorithm": algorithm["name"],
                "mean time": mean(trial_times),
                "standard deviation": stdev(trial_times) if n_trials > 1 else 0,
                "sequences per second": len(sequences) / mean(trial_times),
            }
        )

    return results


def benchmark_similarity_functions(similarity_fns: list, n_sequences: int = 1000, seq_length_range: tuple = (10, 100), n_trials: int = 3) -> list[dict]:
    """
    Benchmark similarity functions by measuring their runtime performance.

    Args:
        similarity_fns: List of similarity functions to test
        n_sequences: Number of sequences to generate for testing
        seq_length_range: (min_length, max_length) for random sequences
        n_trials: Number of times to repeat the benchmark

    Returns:
        List of benchmark results for each clustering function
    """
    # Generate random test sequences
    sequences = []
    for _ in range(n_sequences):
        length = random.randint(*seq_length_range)
        sequence = [random.choice(string.ascii_lowercase) for _ in range(length)]
        sequences.append(sequence)

    total_comparisons = (n_sequences * (n_sequences - 1)) // 2
    results = []
    for fn in similarity_fns:
        trial_times = []
        for _ in range(n_trials):
            start_time = perf_counter()
            for i in range(n_sequences):
                for j in range(i + 1, n_sequences):
                    fn(sequences[i], sequences[j])
            elapsed = perf_counter() - start_time
            trial_times.append(elapsed)

        # Calculate statistics
        results.append(
            {
                "function": fn.__name__,
                "mean time": mean(trial_times),
                "standard deviation": stdev(trial_times) if n_trials > 1 else 0,
                "comparisons per second": total_comparisons / mean(trial_times),
            }
        )

    return results


def print_benchmark_results(results: list[dict]):
    """
    Pretty print the benchmark results.
    """
    print("\nbenchmark results:")
    for r in results:
        for k, v in r.items():
            print(f"{k}: {v}")
        print()
