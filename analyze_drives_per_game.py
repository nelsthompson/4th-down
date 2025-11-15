#!/usr/bin/env python3
"""
Analyze the distribution of drives per game
"""

import random
from gridiron_dice import simulate_game
import statistics

def analyze_drives_per_game(num_games: int = 1000):
    """Simulate games and analyze the number of drives"""

    print(f"Simulating {num_games} games to analyze drives per game...\n")

    drive_counts = []

    for i in range(num_games):
        if (i + 1) % 100 == 0:
            print(f"  Simulated {i + 1} games...")

        game = simulate_game()
        drive_counts.append(len(game.drives))

    # Sort for quartile calculation
    drive_counts.sort()

    # Calculate statistics
    minimum = min(drive_counts)
    maximum = max(drive_counts)
    mean = statistics.mean(drive_counts)
    median = statistics.median(drive_counts)

    # Calculate quartiles
    q1 = statistics.quantiles(drive_counts, n=4)[0]  # 25th percentile
    q2 = statistics.quantiles(drive_counts, n=4)[1]  # 50th percentile (median)
    q3 = statistics.quantiles(drive_counts, n=4)[2]  # 75th percentile

    # Calculate IQR
    iqr = q3 - q1

    print()
    print("=" * 60)
    print("DRIVES PER GAME ANALYSIS")
    print("=" * 60)
    print()
    print(f"Sample size: {num_games} games")
    print()
    print("QUARTILE DISTRIBUTION:")
    print(f"  Minimum:        {minimum} drives")
    print(f"  Q1 (25th %ile): {q1:.1f} drives")
    print(f"  Q2 (Median):    {q2:.1f} drives")
    print(f"  Q3 (75th %ile): {q3:.1f} drives")
    print(f"  Maximum:        {maximum} drives")
    print()
    print(f"  Mean:           {mean:.2f} drives")
    print(f"  IQR (Q3-Q1):    {iqr:.1f} drives")
    print()

    # Frequency distribution
    print("FREQUENCY DISTRIBUTION:")
    from collections import Counter
    freq = Counter(drive_counts)

    for drives in sorted(freq.keys()):
        count = freq[drives]
        pct = 100 * count / num_games
        bar = '#' * int(pct)
        print(f"  {drives:2d} drives: {count:4d} ({pct:5.1f}%) {bar}")

    print()

    # Additional stats
    print("PERCENTILE BREAKDOWN:")
    percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99]
    for p in percentiles:
        idx = int(len(drive_counts) * p / 100)
        value = drive_counts[idx]
        print(f"  {p:2d}th percentile: {value} drives")

    print()

if __name__ == "__main__":
    random.seed()
    analyze_drives_per_game(1000)
