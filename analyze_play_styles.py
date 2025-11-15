#!/usr/bin/env python3
"""
Analyze points scored by play style for drives starting at own 30-yard line
"""

from gridiron_dice import simulate_game
from collections import defaultdict

def analyze_play_styles_from_30(n_games=500):
    """Analyze drive outcomes by play style from the 30-yard line"""

    print(f"Simulating {n_games} games to analyze play style effectiveness from 30-yard line...\n")

    # Track drives by style
    # Key: style, Value: list of points scored
    style_drives = {
        "run": [],
        "balanced": [],
        "pass": []
    }

    # Track detailed outcomes
    style_outcomes = {
        "run": {"TD": 0, "FG": 0, "Turnover": 0, "Zero": 0, "total": 0},
        "balanced": {"TD": 0, "FG": 0, "Turnover": 0, "Zero": 0, "total": 0},
        "pass": {"TD": 0, "FG": 0, "Turnover": 0, "Zero": 0, "total": 0}
    }

    for i in range(n_games):
        if (i + 1) % 100 == 0:
            print(f"Completed {i + 1}/{n_games} games...")

        game = simulate_game(seed=None)

        for drive in game.drives:
            # Check if drive starts at own 30
            if drive.team == "Bombers":
                starting_at_30 = (drive.start_x == 30)
            else:  # Gunners
                # Gunners at x=70 is their own 30
                starting_at_30 = (drive.start_x == 70)

            if starting_at_30:
                style = drive.style
                points = drive.points

                style_drives[style].append(points)
                style_outcomes[style]["total"] += 1

                # Categorize outcome
                if "Turnover" in drive.result:
                    style_outcomes[style]["Turnover"] += 1
                elif points == 7:
                    style_outcomes[style]["TD"] += 1
                elif points == 3:
                    style_outcomes[style]["FG"] += 1
                else:
                    style_outcomes[style]["Zero"] += 1

    print(f"\nCompleted all {n_games} games!\n")

    # Calculate and display results
    print("="*80)
    print("PLAY STYLE ANALYSIS: DRIVES STARTING AT OWN 30-YARD LINE")
    print("="*80)
    print()

    # Summary table
    print("SUMMARY")
    print("-" * 80)
    print(f"{'Style':>12} | {'Drives':>8} | {'Avg Pts':>10} | {'TD%':>8} | {'FG%':>8} | {'TO%':>8} | {'0 pts%':>8}")
    print("-" * 80)

    results = {}
    for style in ["run", "balanced", "pass"]:
        drives = style_drives[style]
        outcomes = style_outcomes[style]

        if not drives:
            continue

        total = outcomes["total"]
        avg_points = sum(drives) / len(drives)
        td_pct = 100 * outcomes["TD"] / total
        fg_pct = 100 * outcomes["FG"] / total
        to_pct = 100 * outcomes["Turnover"] / total
        zero_pct = 100 * outcomes["Zero"] / total

        results[style] = {
            "drives": total,
            "avg_points": avg_points,
            "td_pct": td_pct,
            "fg_pct": fg_pct,
            "to_pct": to_pct,
            "zero_pct": zero_pct
        }

        print(f"{style:>12} | {total:>8} | {avg_points:>10.3f} | {td_pct:>7.1f}% | {fg_pct:>7.1f}% | {to_pct:>7.1f}% | {zero_pct:>7.1f}%")

    print()
    print("="*80)
    print()

    # Detailed breakdown
    print("DETAILED BREAKDOWN BY STYLE")
    print("-" * 80)

    for style in ["run", "balanced", "pass"]:
        if style not in results:
            continue

        r = results[style]
        outcomes = style_outcomes[style]

        print(f"\n{style.upper()}")
        print(f"  Total drives: {r['drives']}")
        print(f"  Average points per drive: {r['avg_points']:.3f}")
        print(f"  Touchdowns: {outcomes['TD']} ({r['td_pct']:.1f}%)")
        print(f"  Field Goals: {outcomes['FG']} ({r['fg_pct']:.1f}%)")
        print(f"  Turnovers: {outcomes['Turnover']} ({r['to_pct']:.1f}%)")
        print(f"  No Score: {outcomes['Zero']} ({r['zero_pct']:.1f}%)")

        # Scoring drives percentage
        scoring_drives = outcomes['TD'] + outcomes['FG']
        scoring_pct = 100 * scoring_drives / r['drives']
        print(f"  Scoring drives: {scoring_drives} ({scoring_pct:.1f}%)")

    print()
    print("="*80)
    print()

    # Key insights
    print("KEY INSIGHTS:")
    print()

    # Best for points
    best_style = max(results.keys(), key=lambda s: results[s]['avg_points'])
    worst_style = min(results.keys(), key=lambda s: results[s]['avg_points'])
    print(f"  Highest avg points: {best_style.upper()} ({results[best_style]['avg_points']:.3f} pts/drive)")
    print(f"  Lowest avg points: {worst_style.upper()} ({results[worst_style]['avg_points']:.3f} pts/drive)")
    print()

    # TD comparison
    best_td = max(results.keys(), key=lambda s: results[s]['td_pct'])
    print(f"  Highest TD rate: {best_td.upper()} ({results[best_td]['td_pct']:.1f}%)")
    print()

    # Turnover comparison
    safest = min(results.keys(), key=lambda s: results[s]['to_pct'])
    riskiest = max(results.keys(), key=lambda s: results[s]['to_pct'])
    print(f"  Safest (lowest TO): {safest.upper()} ({results[safest]['to_pct']:.1f}%)")
    print(f"  Riskiest (highest TO): {riskiest.upper()} ({results[riskiest]['to_pct']:.1f}%)")
    print()

    # Risk-adjusted analysis
    print("  RISK-ADJUSTED SCORING (Avg Points - Turnover Penalty):")
    for style in ["run", "balanced", "pass"]:
        r = results[style]
        # Each turnover costs you the drive (0 points instead of potential)
        # We can estimate the "cost" of turnovers
        risk_adjusted = r['avg_points']
        print(f"    {style.capitalize():>8}: {risk_adjusted:.3f} pts/drive (TO rate: {r['to_pct']:.1f}%)")

    print()
    print("="*80)

if __name__ == "__main__":
    analyze_play_styles_from_30(500)
