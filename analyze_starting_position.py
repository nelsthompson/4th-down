#!/usr/bin/env python3
"""
Analyze average points scored per drive by starting field position
"""

from gridiron_dice import simulate_game
from collections import defaultdict

def analyze_starting_positions(n_games=200):
    """Analyze points scored by starting field position"""

    print(f"Simulating {n_games} games to analyze starting position impact...\n")

    # Track drives by starting position bucket
    # Key: (team, position_bucket), Value: list of points scored
    bombers_drives = defaultdict(list)
    gunners_drives = defaultdict(list)

    for i in range(n_games):
        if (i + 1) % 50 == 0:
            print(f"Completed {i + 1}/{n_games} games...")

        game = simulate_game(seed=None)

        for drive in game.drives:
            if drive.team == "Bombers":
                # For Bombers, starting position is their yard line (0-100)
                # Bucket by 10s
                bucket = (drive.start_x // 10) * 10
                bombers_drives[bucket].append(drive.points)
            else:  # Gunners
                # For Gunners, they move from 100 toward 0
                # Convert to their perspective (distance from their own goal)
                # If Gunners start at x=70, they're at their own 30
                gunners_own_yardline = 100 - drive.start_x
                bucket = (gunners_own_yardline // 10) * 10
                gunners_drives[bucket].append(drive.points)

    print(f"\nCompleted all {n_games} games!\n")

    # Calculate averages
    print("="*70)
    print("AVERAGE POINTS SCORED PER DRIVE BY STARTING FIELD POSITION")
    print("="*70)
    print("\nStarting field position represents yards from own goal line")
    print("(e.g., '20' = starting at own 20-29 yard line)\n")

    # Combined analysis (both teams together)
    combined_drives = defaultdict(list)
    for bucket in set(list(bombers_drives.keys()) + list(gunners_drives.keys())):
        combined_drives[bucket] = bombers_drives[bucket] + gunners_drives[bucket]

    print("COMBINED (Both Teams)")
    print("-" * 70)
    print(f"{'Position':>10} | {'Drives':>8} | {'Avg Points':>12} | {'TD%':>8} | {'FG%':>8} | {'0 pts%':>8}")
    print("-" * 70)

    for bucket in sorted(combined_drives.keys()):
        drives = combined_drives[bucket]
        avg_points = sum(drives) / len(drives) if drives else 0
        td_pct = 100 * sum(1 for p in drives if p == 7) / len(drives) if drives else 0
        fg_pct = 100 * sum(1 for p in drives if p == 3) / len(drives) if drives else 0
        zero_pct = 100 * sum(1 for p in drives if p == 0) / len(drives) if drives else 0

        print(f"{bucket:>4}-{bucket+9:<4} | {len(drives):>8} | {avg_points:>12.3f} | {td_pct:>7.1f}% | {fg_pct:>7.1f}% | {zero_pct:>7.1f}%")

    # Individual team breakdowns
    print("\n" + "="*70)
    print("BOMBERS")
    print("-" * 70)
    print(f"{'Position':>10} | {'Drives':>8} | {'Avg Points':>12} | {'TD%':>8} | {'FG%':>8} | {'0 pts%':>8}")
    print("-" * 70)

    for bucket in sorted(bombers_drives.keys()):
        drives = bombers_drives[bucket]
        avg_points = sum(drives) / len(drives) if drives else 0
        td_pct = 100 * sum(1 for p in drives if p == 7) / len(drives) if drives else 0
        fg_pct = 100 * sum(1 for p in drives if p == 3) / len(drives) if drives else 0
        zero_pct = 100 * sum(1 for p in drives if p == 0) / len(drives) if drives else 0

        print(f"{bucket:>4}-{bucket+9:<4} | {len(drives):>8} | {avg_points:>12.3f} | {td_pct:>7.1f}% | {fg_pct:>7.1f}% | {zero_pct:>7.1f}%")

    print("\n" + "="*70)
    print("GUNNERS")
    print("-" * 70)
    print(f"{'Position':>10} | {'Drives':>8} | {'Avg Points':>12} | {'TD%':>8} | {'FG%':>8} | {'0 pts%':>8}")
    print("-" * 70)

    for bucket in sorted(gunners_drives.keys()):
        drives = gunners_drives[bucket]
        avg_points = sum(drives) / len(drives) if drives else 0
        td_pct = 100 * sum(1 for p in drives if p == 7) / len(drives) if drives else 0
        fg_pct = 100 * sum(1 for p in drives if p == 3) / len(drives) if drives else 0
        zero_pct = 100 * sum(1 for p in drives if p == 0) / len(drives) if drives else 0

        print(f"{bucket:>4}-{bucket+9:<4} | {len(drives):>8} | {avg_points:>12.3f} | {td_pct:>7.1f}% | {fg_pct:>7.1f}% | {zero_pct:>7.1f}%")

    print("\n" + "="*70)
    print("\nKey Insights:")

    # Find best and worst starting positions
    best_bucket = max(combined_drives.keys(), key=lambda b: sum(combined_drives[b])/len(combined_drives[b]))
    worst_bucket = min(combined_drives.keys(), key=lambda b: sum(combined_drives[b])/len(combined_drives[b]))

    best_avg = sum(combined_drives[best_bucket])/len(combined_drives[best_bucket])
    worst_avg = sum(combined_drives[worst_bucket])/len(combined_drives[worst_bucket])

    print(f"- Best starting position: {best_bucket}-{best_bucket+9} ({best_avg:.3f} points/drive)")
    print(f"- Worst starting position: {worst_bucket}-{worst_bucket+9} ({worst_avg:.3f} points/drive)")
    print(f"- Field position impact: {best_avg - worst_avg:.3f} point difference")

    print("\n" + "="*70)

if __name__ == "__main__":
    analyze_starting_positions(200)
