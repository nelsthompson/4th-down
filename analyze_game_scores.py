#!/usr/bin/env python3
"""
Analyze final score distributions from many game simulations
"""

import random
from collections import Counter, defaultdict
from gridiron_dice import simulate_game

def analyze_game_scores(num_games: int = 1000):
    """Simulate many games and analyze score distributions"""

    print(f"Simulating {num_games} games...\n")

    # Track results
    bombers_scores = []
    gunners_scores = []
    total_scores = []
    score_diffs = []
    final_scores = []  # (bombers, gunners) tuples

    bombers_wins = 0
    gunners_wins = 0
    ties = 0

    # Simulate games
    for _ in range(num_games):
        game = simulate_game(seed=None)
        b_score = game.score["Bombers"]
        g_score = game.score["Gunners"]

        bombers_scores.append(b_score)
        gunners_scores.append(g_score)
        total_scores.append(b_score + g_score)
        score_diffs.append(abs(b_score - g_score))
        final_scores.append((b_score, g_score))

        if b_score > g_score:
            bombers_wins += 1
        elif g_score > b_score:
            gunners_wins += 1
        else:
            ties += 1

    # Calculate statistics
    avg_bombers = sum(bombers_scores) / num_games
    avg_gunners = sum(gunners_scores) / num_games
    avg_total = sum(total_scores) / num_games
    avg_diff = sum(score_diffs) / num_games

    min_bombers = min(bombers_scores)
    max_bombers = max(bombers_scores)
    min_gunners = min(gunners_scores)
    max_gunners = max(gunners_scores)
    min_total = min(total_scores)
    max_total = max(total_scores)

    # Print results
    print("=" * 70)
    print("GAME SCORE ANALYSIS")
    print("=" * 70)
    print()

    print(f"Games Simulated: {num_games}")
    print()

    print("OUTCOMES:")
    print(f"  Bombers Wins:  {bombers_wins:4d} ({bombers_wins/num_games*100:5.1f}%)")
    print(f"  Gunners Wins:  {gunners_wins:4d} ({gunners_wins/num_games*100:5.1f}%)")
    print(f"  Ties:          {ties:4d} ({ties/num_games*100:5.1f}%)")
    print()

    print("SCORING AVERAGES:")
    print(f"  Avg Bombers Score:     {avg_bombers:5.1f}")
    print(f"  Avg Gunners Score:     {avg_gunners:5.1f}")
    print(f"  Avg Combined Score:    {avg_total:5.1f}")
    print(f"  Avg Score Differential: {avg_diff:5.1f}")
    print()

    print("SCORE RANGES:")
    print(f"  Bombers: {min_bombers:3d} - {max_bombers:3d}")
    print(f"  Gunners: {min_gunners:3d} - {max_gunners:3d}")
    print(f"  Combined: {min_total:3d} - {max_total:3d}")
    print()

    # Score distribution by range
    print("=" * 70)
    print("INDIVIDUAL TEAM SCORE DISTRIBUTION")
    print("=" * 70)
    print()

    all_scores = bombers_scores + gunners_scores

    ranges = [
        (0, 6, "0-6"),
        (7, 13, "7-13"),
        (14, 20, "14-20"),
        (21, 27, "21-27"),
        (28, 34, "28-34"),
        (35, 41, "35-41"),
        (42, 100, "42+")
    ]

    print("Score Range    Count    Percentage")
    print("-----------    -----    ----------")
    for low, high, label in ranges:
        count = sum(1 for s in all_scores if low <= s <= high)
        pct = count / len(all_scores) * 100
        print(f"{label:11s}    {count:5d}    {pct:5.1f}%")
    print()

    # Combined score distribution
    print("=" * 70)
    print("COMBINED SCORE DISTRIBUTION")
    print("=" * 70)
    print()

    combined_ranges = [
        (0, 19, "0-19"),
        (20, 29, "20-29"),
        (30, 39, "30-39"),
        (40, 49, "40-49"),
        (50, 59, "50-59"),
        (60, 69, "60-69"),
        (70, 100, "70+")
    ]

    print("Total Range    Count    Percentage")
    print("-----------    -----    ----------")
    for low, high, label in combined_ranges:
        count = sum(1 for s in total_scores if low <= s <= high)
        pct = count / num_games * 100
        print(f"{label:11s}    {count:5d}    {pct:5.1f}%")
    print()

    # Score differential distribution
    print("=" * 70)
    print("SCORE DIFFERENTIAL DISTRIBUTION")
    print("=" * 70)
    print()

    diff_ranges = [
        (0, 0, "Tie (0)"),
        (1, 3, "1-3 pts"),
        (4, 7, "4-7 pts"),
        (8, 14, "8-14 pts"),
        (15, 21, "15-21 pts"),
        (22, 100, "22+ pts")
    ]

    print("Differential    Count    Percentage")
    print("------------    -----    ----------")
    for low, high, label in diff_ranges:
        count = sum(1 for d in score_diffs if low <= d <= high)
        pct = count / num_games * 100
        print(f"{label:12s}    {count:5d}    {pct:5.1f}%")
    print()

    # Most common final scores
    print("=" * 70)
    print("MOST COMMON FINAL SCORES (Top 20)")
    print("=" * 70)
    print()

    score_counter = Counter(final_scores)
    most_common = score_counter.most_common(20)

    print("Rank  Score          Count   Percentage")
    print("----  -------------  -----   ----------")
    for i, ((b, g), count) in enumerate(most_common, 1):
        pct = count / num_games * 100
        winner = "B" if b > g else ("G" if g > b else "T")
        print(f"{i:3d}.  {b:2d} - {g:2d} ({winner})     {count:5d}   {pct:5.1f}%")
    print()

    # Quartiles for individual scores
    print("=" * 70)
    print("SCORE QUARTILES")
    print("=" * 70)
    print()

    all_scores_sorted = sorted(all_scores)
    n = len(all_scores_sorted)
    q1_idx = n // 4
    q2_idx = n // 2
    q3_idx = 3 * n // 4

    print(f"25th percentile: {all_scores_sorted[q1_idx]} points")
    print(f"50th percentile (median): {all_scores_sorted[q2_idx]} points")
    print(f"75th percentile: {all_scores_sorted[q3_idx]} points")
    print()

    # High scoring and low scoring games
    print("=" * 70)
    print("EXTREME GAMES")
    print("=" * 70)
    print()

    highest_total_idx = total_scores.index(max_total)
    lowest_total_idx = total_scores.index(min_total)
    highest_diff_idx = score_diffs.index(max(score_diffs))

    print(f"Highest Scoring Game: {bombers_scores[highest_total_idx]} - {gunners_scores[highest_total_idx]} (Total: {max_total})")
    print(f"Lowest Scoring Game:  {bombers_scores[lowest_total_idx]} - {gunners_scores[lowest_total_idx]} (Total: {min_total})")
    print(f"Biggest Blowout:      {bombers_scores[highest_diff_idx]} - {gunners_scores[highest_diff_idx]} (Diff: {score_diffs[highest_diff_idx]})")
    print()

    # Shutouts and high scores
    shutouts = sum(1 for (b, g) in final_scores if b == 0 or g == 0)
    high_scorers = sum(1 for s in all_scores if s >= 40)

    print(f"Shutouts: {shutouts} ({shutouts/num_games*100:.1f}%)")
    print(f"Team scoring 40+: {high_scorers} ({high_scorers/len(all_scores)*100:.1f}%)")
    print()

if __name__ == "__main__":
    random.seed()
    analyze_game_scores(1000)
