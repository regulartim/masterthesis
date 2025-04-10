from difflib import SequenceMatcher

import numpy as np

SIM_MATRIX_CACHE = {}


def jaccard_similarity(seq1: list[str], seq2: list[str]) -> float:
    """
    Calculate the Jaccard similarity coefficient between two sequences.

    The Jaccard similarity is defined as the size of the intersection divided by the size
    of the union of the two sets. It measures the similarity between finite sample sets
    and is defined as the cardinality of the intersection divided by the cardinality of the union.

    Args:
        seq1 (list[str]): First sequence of strings to compare
        seq2 (list[str]): Second sequence of strings to compare

    Returns:
        float: A value between 0 and 1, where:
            - 0 indicates no overlap between the sets (completely dissimilar)
            - 1 indicates identical sets (completely similar)
            - Values between 0 and 1 indicate partial similarity
    """
    set1 = set(seq1)
    set2 = set(seq2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0


def ratcliff_obershelp_similarity(seq1: list[str], seq2: list[str]) -> float:
    """
    Calculate the Ratcliff/Obershelp similarity between two sequences.

    The Ratcliff/Obershelp algorithm finds the largest contiguous matching subsequence,
    then recursively finds the largest matching subsequences to the left and right of this match.
    The similarity is calculated as 2 times the number of matching elements divided by
    the total number of elements in both sequences.

    Parameters:
        seq1 (list[str]): First sequence of strings to compare
        seq2 (list[str]): Second sequence of strings to compare

    Returns:
        float: A value between 0 and 1, where:
            - 0 indicates no similarity
            - 1 indicates identical sequences
            - Values between 0 and 1 indicate partial similarity
    """
    return SequenceMatcher(None, seq1, seq2).ratio()


def compute_similarity_matrix(sequences: list[list[str]], similarity_fn) -> np.ndarray:
    """
    Compute a similarity matrix for a list of sequences using the specified similarity function.

    This function calculates the pairwise similarity between all sequences in the input list
    and returns a square matrix where each cell [i,j] contains the similarity score between
    sequences[i] and sequences[j]. Results are cached to improve performance on repeated calls
    with the same similarity function.

    Parameters:
        sequences (list[list[str]]): List of sequences to compare, where each sequence is a list of strings
        similarity_fn (callable): Function that accepts two sequences (list[str]) and returns a float
                                  representing their similarity (in range 0-1)

    Returns:
        np.ndarray: A square matrix of shape (n, n) where n is the number of sequences.
                   - Diagonal elements [i,i] are set to 1.0 (self-similarity)
                   - Off-diagonal elements [i,j] contain the similarity between sequences[i] and sequences[j]
    """
    if similarity_fn in SIM_MATRIX_CACHE:
        return SIM_MATRIX_CACHE[similarity_fn.__name__]
    n = len(sequences)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            similarity = similarity_fn(sequences[i], sequences[j])
            matrix[i, j] = similarity
            matrix[j, i] = similarity
        matrix[i, i] = 1.0  # Self-similarity
    SIM_MATRIX_CACHE[similarity_fn.__name__] = matrix
    return matrix
