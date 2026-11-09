"""
GoviSense Warning Evaluation & Coverage Scoring Engine
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Provides rigorous mathematical evaluations for:
1. Directional warning precision, recall, and F1-score for Glut & Shortage alerts.
2. Empirical coverage and calibration error for 80% conformal prediction intervals.
3. Price crash / spike correlation against preceding SPI signals.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd


def evaluate_directional_warnings(
    actual_labels: List[str],
    predicted_labels: List[str],
    target_class: str = "Glut",
) -> Dict[str, float]:
    """
    Computes precision, recall, specificity, and F1-score for a directional market warning.

    Args:
        actual_labels: Ground-truth market state ('Glut', 'Balanced', 'Shortage')
        predicted_labels: Model predicted SPI state
        target_class: The warning event to score ('Glut' or 'Shortage')

    Returns:
        Dictionary containing precision, recall, specificity, and f1_score.
    """
    if len(actual_labels) != len(predicted_labels):
        raise ValueError("actual_labels and predicted_labels must have identical length")

    tp = sum(1 for a, p in zip(actual_labels, predicted_labels) if a == target_class and p == target_class)
    fp = sum(1 for a, p in zip(actual_labels, predicted_labels) if a != target_class and p == target_class)
    fn = sum(1 for a, p in zip(actual_labels, predicted_labels) if a == target_class and p != target_class)
    tn = sum(1 for a, p in zip(actual_labels, predicted_labels) if a != target_class and p != target_class)

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    specificity = tn / max(tn + fp, 1)
    f1 = 2 * (precision * recall) / max(precision + recall, 1e-6)

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": round(float(precision), 3),
        "recall": round(float(recall), 3),
        "specificity": round(float(specificity), 3),
        "f1_score": round(float(f1), 3),
    }


def evaluate_interval_coverage(
    y_true: np.ndarray,
    y_low: np.ndarray,
    y_high: np.ndarray,
    target_nominal: float = 0.80,
) -> Dict[str, Any]:
    """
    Evaluates empirical coverage of prediction intervals against the nominal target (e.g. 80%).

    Args:
        y_true: Ground-truth continuous observations
        y_low: Lower bound of prediction interval
        y_high: Upper bound of prediction interval
        target_nominal: Nominal confidence level (default: 0.80)

    Returns:
        Dictionary containing empirical coverage %, nominal %, average interval width,
        and boolean pass flag (empirical >= target_nominal - 0.05).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_low = np.asarray(y_low, dtype=float)
    y_high = np.asarray(y_high, dtype=float)

    if len(y_true) == 0:
        return {
            "empirical_coverage_pct": 0.0,
            "nominal_target_pct": target_nominal * 100.0,
            "coverage_error": -target_nominal,
            "mean_interval_width": 0.0,
            "calibrated": False,
        }

    in_bounds = (y_true >= y_low) & (y_true <= y_high)
    empirical_coverage = float(np.mean(in_bounds))
    widths = y_high - y_low
    mean_width = float(np.mean(widths))

    calibrated = empirical_coverage >= (target_nominal - 0.05)

    return {
        "empirical_coverage_pct": round(empirical_coverage * 100.0, 1),
        "nominal_target_pct": round(target_nominal * 100.0, 1),
        "coverage_error": round(empirical_coverage - target_nominal, 3),
        "mean_interval_width": round(mean_width, 2),
        "sample_count": len(y_true),
        "calibrated": calibrated,
    }


def derive_ground_truth_from_prices(
    price_series: np.ndarray,
    threshold_pct: float = 0.15,
) -> List[str]:
    """
    Derives economic ground-truth market states directly from observed price movement:
    - Price drop > threshold_pct in following month -> 'Glut'
    - Price increase > threshold_pct in following month -> 'Shortage'
    - Price change within +/- threshold_pct -> 'Balanced'
    """
    prices = np.asarray(price_series, dtype=float)
    if len(prices) < 2:
        return ["Balanced"] * len(prices)

    pct_change = np.diff(prices) / np.maximum(prices[:-1], 1.0)
    labels = []
    for change in pct_change:
        if change < -threshold_pct:
            labels.append("Glut")
        elif change > threshold_pct:
            labels.append("Shortage")
        else:
            labels.append("Balanced")
    # For the last observation without a future step, assume Balanced
    labels.append("Balanced")
    return labels


def bootstrap_metric_ci(
    y_true: List[str],
    y_pred: List[str],
    target_class: str = "Glut",
    n_bootstraps: int = 500,
    confidence_level: float = 0.95,
    random_seed: int = 42,
) -> Dict[str, Tuple[float, float]]:
    """
    Computes bootstrap confidence intervals for precision, recall, and F1.
    """
    np.random.seed(random_seed)
    n = len(y_true)
    if n == 0:
        return {"precision_ci": (0.0, 0.0), "recall_ci": (0.0, 0.0), "f1_ci": (0.0, 0.0)}

    precisions, recalls, f1s = [], [], []
    for _ in range(n_bootstraps):
        indices = np.random.choice(n, size=n, replace=True)
        bt_true = [y_true[i] for i in indices]
        bt_pred = [y_pred[i] for i in indices]
        res = evaluate_directional_warnings(bt_true, bt_pred, target_class=target_class)
        precisions.append(res["precision"])
        recalls.append(res["recall"])
        f1s.append(res["f1_score"])

    alpha = (1.0 - confidence_level) / 2.0
    return {
        "precision_ci": (
            round(float(np.percentile(precisions, 100 * alpha)), 3),
            round(float(np.percentile(precisions, 100 * (1 - alpha))), 3),
        ),
        "recall_ci": (
            round(float(np.percentile(recalls, 100 * alpha)), 3),
            round(float(np.percentile(recalls, 100 * (1 - alpha))), 3),
        ),
        "f1_ci": (
            round(float(np.percentile(f1s, 100 * alpha)), 3),
            round(float(np.percentile(f1s, 100 * (1 - alpha))), 3),
        ),
    }


def evaluate_price_crash_correlation(
    prices: np.ndarray,
    spi_scores: np.ndarray,
    crash_threshold_pct: float = 0.10,
) -> Dict[str, float]:
    """
    Evaluates correlation between SPI scores and subsequent monthly price changes.
    Verifies the economic thesis: high positive SPI (glut) precedes farmgate price collapse.
    """
    if len(prices) < 2 or len(spi_scores) < 2:
        return {
            "correlation_spi_vs_subsequent_price_change": 0.0,
            "glut_crash_hit_rate": 0.0,
        }

    n = min(len(prices) - 1, len(spi_scores) - 1)
    prec_spi = spi_scores[:n]
    price_pct_changes = (prices[1 : n + 1] - prices[:n]) / np.maximum(prices[:n], 1e-6)

    # Pearson correlation
    if np.std(prec_spi) > 1e-6 and np.std(price_pct_changes) > 1e-6:
        corr = float(np.corrcoef(prec_spi, price_pct_changes)[0, 1])
    else:
        corr = 0.0

    # Glut crash hit rate: when SPI >= 0.15, did prices drop by at least crash_threshold_pct?
    glut_mask = prec_spi >= 0.15
    if np.sum(glut_mask) > 0:
        crashes = price_pct_changes[glut_mask] <= -crash_threshold_pct
        hit_rate = float(np.mean(crashes))
    else:
        hit_rate = 0.0

    return {
        "correlation_spi_vs_subsequent_price_change": round(corr, 3),
        "glut_crash_hit_rate": round(hit_rate, 3),
    }


def evaluate_spi_against_price_ground_truth(
    prices: np.ndarray,
    predicted_spi_labels: List[str],
    target_class: str = "Glut",
) -> Dict[str, Any]:
    """
    Rebuilds ground truth from CBSL wholesale price movements and evaluates model
    against Random Baseline and Always-Balanced Baseline.
    Detects degenerate distributions and marks them 'not evaluable'.
    """
    actual_labels = derive_ground_truth_from_prices(prices)
    if len(actual_labels) != len(predicted_spi_labels):
        min_len = min(len(actual_labels), len(predicted_spi_labels))
        actual_labels = actual_labels[:min_len]
        predicted_spi_labels = predicted_spi_labels[:min_len]

    sample_size = len(actual_labels)
    unique_actual = set(actual_labels)
    unique_pred = set(predicted_spi_labels)

    # Degenerate case detection: e.g. all months identical class or no target class present
    if len(unique_actual) <= 1 or target_class not in unique_actual or len(unique_pred) <= 1:
        return {
            "status": "not evaluable",
            "reason": f"Degenerate label distribution (Actual classes: {unique_actual}, Pred classes: {unique_pred})",
            "sample_size": sample_size,
            "target_class": target_class,
        }

    # Model evaluation
    model_metrics = evaluate_directional_warnings(actual_labels, predicted_spi_labels, target_class=target_class)
    cis = bootstrap_metric_ci(actual_labels, predicted_spi_labels, target_class=target_class)

    # Always-Balanced Baseline
    balanced_preds = ["Balanced"] * sample_size
    balanced_metrics = evaluate_directional_warnings(actual_labels, balanced_preds, target_class=target_class)

    # Random Baseline (proportional random guess)
    class_probs = [actual_labels.count(c) / sample_size for c in ["Glut", "Balanced", "Shortage"]]
    np.random.seed(42)
    random_preds = np.random.choice(["Glut", "Balanced", "Shortage"], size=sample_size, p=class_probs).tolist()
    random_metrics = evaluate_directional_warnings(actual_labels, random_preds, target_class=target_class)

    return {
        "status": "evaluable",
        "sample_size": sample_size,
        "target_class": target_class,
        "model": {**model_metrics, **cis},
        "always_balanced_baseline": balanced_metrics,
        "random_baseline": random_metrics,
        "beats_always_balanced": model_metrics["f1_score"] > balanced_metrics["f1_score"],
        "beats_random": model_metrics["f1_score"] > random_metrics["f1_score"],
    }

