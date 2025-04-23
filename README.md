# Generating Threat Intelligence Live Feeds Based on Honeypot Data

This repository contains the implementation code for my master's thesis on enhancing threat intelligence feeds through advanced generation mechanisms in [GreedyBear](https://github.com/intelowlproject/GreedyBear).

## Project Overview

The research focuses on improving the quality of threat intelligence feeds derived from honeypot data by:

1. Implementing IP blocklist generation mechanisms that prioritise malicious IP addresses
2. Developing command sequence clustering techniques to identify similar attack patterns across multiple sources
3. Creating a evaluation method to assess blocklist quality

The project extended GreedyBear with machine learning models and advanced clustering algorithms to transform raw honeypot data into more valuable threat intelligence for the security community.

## Repository Structure

- **clustering/** - Implementation of command sequence clustering algorithms and similarity measures
- **data_in/** - Scripts for data gathering
- **data_out/** - Evaluation results
- **models/** - Implementation of scoring models for blocklist generation

### Key Files

- **evaluate_clustering.py** - Clustering quality analysis
- **evaluate_single_day.py** - Single-day analysis of blocklists
- **evaluate_time_span.py** - Analysis of blocklists over multiple days
- **greedybear_utils.py** - Utility functions for interfacing with GreedyBear
- **train_models.py** - Training pipeline for machine learning models with hyperparameter optimization

## Implemented Models

The repository implements several scoring models for blocklist generation including:
- Logistic Regression Classifier
- Random Forest Classifier and Regressor
- CatBoost Classifier, Regressor, and Ranker

For command sequence clustering, both DBSCAN and Agglomerative Hierarchical Clustering are implemented with Jaccard and Ratcliff/Obershelp similarity measures.

## Evaluation

The evaluation methodology assesses blocklist quality through:

1. **Prevention-based metrics**: Measures how effectively generated blocklists would have prevented future honeypot interactions
2. **Third-party validation**: Compares generated blocklists against AbuseIPDB's confidence of abuse scores

## Results

Key findings of this research include:

- Classifier models excel at maximizing IP-based recall
- Regressor/ranker models achieve superior interaction-based recall
- DBSCAN clustering with Jaccard similarity provides a good alance of accuracy and computational efficiency for identifying attack patterns

The implemented techniques significantly outperform existing GreedyBear feed generation mechanisms and are already [in operation](https://greedybear.honeynet.org/).
