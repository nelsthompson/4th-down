#!/usr/bin/env python3
"""
Analyze distribution of game outcomes from batch simulations
"""

from gridiron_dice import simulate_game
import statistics

def analyze_batch(n: int = 200):
    """Run n simulations and analyze the distributions"""
    total_points = []
    point_differentials = []
    drive_counts = []

    print(f"Simulating {n} games...\n")

    for i in range(n):
        game = simulate_game(seed=None)
        b = game.score["Bombers"]
        g = game.score["Gunners"]

        total_pts = b + g
        diff = abs(b - g)
        num_drives = len(game.drives)

        total_points.append(total_pts)
        point_differentials.append(diff)
        drive_counts.append(num_drives)

    # Sort for quartile calculation
    total_points.sort()
    point_differentials.sort()
    drive_counts.sort()

    # Calculate quartiles
    def get_quartiles(data):
        q1 = statistics.quantiles(data, n=4)[0]  # 25th percentile
        q2 = statistics.median(data)              # 50th percentile (median)
        q3 = statistics.quantiles(data, n=4)[2]  # 75th percentile
        return q1, q2, q3

    tp_q1, tp_q2, tp_q3 = get_quartiles(total_points)
    pd_q1, pd_q2, pd_q3 = get_quartiles(point_differentials)
    dc_q1, dc_q2, dc_q3 = get_quartiles(drive_counts)

    # Print results
    print("="*60)
    print("GAME OUTCOMES ANALYSIS ({} games)".format(n))
    print("="*60)

    print("\n📊 TOTAL POINTS PER GAME")
    print("-" * 60)
    print(f"  Minimum:        {min(total_points)}")
    print(f"  25th percentile (Q1): {tp_q1:.1f}")
    print(f"  50th percentile (Median): {tp_q2:.1f}")
    print(f"  75th percentile (Q3): {tp_q3:.1f}")
    print(f"  Maximum:        {max(total_points)}")
    print(f"  Mean:           {statistics.mean(total_points):.1f}")
    print(f"  Std Dev:        {statistics.stdev(total_points):.1f}")

    print("\n📊 POINT DIFFERENTIAL (Winner - Loser)")
    print("-" * 60)
    print(f"  Minimum:        {min(point_differentials)}")
    print(f"  25th percentile (Q1): {pd_q1:.1f}")
    print(f"  50th percentile (Median): {pd_q2:.1f}")
    print(f"  75th percentile (Q3): {pd_q3:.1f}")
    print(f"  Maximum:        {max(point_differentials)}")
    print(f"  Mean:           {statistics.mean(point_differentials):.1f}")
    print(f"  Std Dev:        {statistics.stdev(point_differentials):.1f}")

    print("\n📊 DRIVES PER GAME")
    print("-" * 60)
    print(f"  Minimum:        {min(drive_counts)}")
    print(f"  25th percentile (Q1): {dc_q1:.1f}")
    print(f"  50th percentile (Median): {dc_q2:.1f}")
    print(f"  75th percentile (Q3): {dc_q3:.1f}")
    print(f"  Maximum:        {max(drive_counts)}")
    print(f"  Mean:           {statistics.mean(drive_counts):.1f}")
    print(f"  Std Dev:        {statistics.stdev(drive_counts):.1f}")

    # Distribution breakdown
    print("\n📊 TOTAL POINTS DISTRIBUTION")
    print("-" * 60)
    print(f"  < 40 points:    {sum(1 for x in total_points if x < 40):3d} games ({100*sum(1 for x in total_points if x < 40)/n:.1f}%)")
    print(f"  40-49 points:   {sum(1 for x in total_points if 40 <= x < 50):3d} games ({100*sum(1 for x in total_points if 40 <= x < 50)/n:.1f}%)")
    print(f"  50-59 points:   {sum(1 for x in total_points if 50 <= x < 60):3d} games ({100*sum(1 for x in total_points if 50 <= x < 60)/n:.1f}%)")
    print(f"  60-69 points:   {sum(1 for x in total_points if 60 <= x < 70):3d} games ({100*sum(1 for x in total_points if 60 <= x < 70)/n:.1f}%)")
    print(f"  70+ points:     {sum(1 for x in total_points if x >= 70):3d} games ({100*sum(1 for x in total_points if x >= 70)/n:.1f}%)")

    print("\n📊 POINT DIFFERENTIAL DISTRIBUTION")
    print("-" * 60)
    print(f"  Ties (0):       {sum(1 for x in point_differentials if x == 0):3d} games ({100*sum(1 for x in point_differentials if x == 0)/n:.1f}%)")
    print(f"  1-7 points:     {sum(1 for x in point_differentials if 1 <= x <= 7):3d} games ({100*sum(1 for x in point_differentials if 1 <= x <= 7)/n:.1f}%)")
    print(f"  8-14 points:    {sum(1 for x in point_differentials if 8 <= x <= 14):3d} games ({100*sum(1 for x in point_differentials if 8 <= x <= 14)/n:.1f}%)")
    print(f"  15-21 points:   {sum(1 for x in point_differentials if 15 <= x <= 21):3d} games ({100*sum(1 for x in point_differentials if 15 <= x <= 21)/n:.1f}%)")
    print(f"  22+ points:     {sum(1 for x in point_differentials if x >= 22):3d} games ({100*sum(1 for x in point_differentials if x >= 22)/n:.1f}%)")

    print("\n📊 DRIVES PER GAME DISTRIBUTION")
    print("-" * 60)
    print(f"  < 20 drives:    {sum(1 for x in drive_counts if x < 20):3d} games ({100*sum(1 for x in drive_counts if x < 20)/n:.1f}%)")
    print(f"  20-24 drives:   {sum(1 for x in drive_counts if 20 <= x < 25):3d} games ({100*sum(1 for x in drive_counts if 20 <= x < 25)/n:.1f}%)")
    print(f"  25-29 drives:   {sum(1 for x in drive_counts if 25 <= x < 30):3d} games ({100*sum(1 for x in drive_counts if 25 <= x < 30)/n:.1f}%)")
    print(f"  30-34 drives:   {sum(1 for x in drive_counts if 30 <= x < 35):3d} games ({100*sum(1 for x in drive_counts if 30 <= x < 35)/n:.1f}%)")
    print(f"  35+ drives:     {sum(1 for x in drive_counts if x >= 35):3d} games ({100*sum(1 for x in drive_counts if x >= 35)/n:.1f}%)")

    print("\n" + "="*60)

if __name__ == "__main__":
    analyze_batch(200)
