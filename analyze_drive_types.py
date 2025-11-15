#!/usr/bin/env python3
"""
Analyze average points per drive by drive type from the 30 yard line
"""

import random
from gridiron_dice import *

def simulate_single_drive(team: str, x: int, style: str, blocks_left: int = 180) -> int:
    """
    Simulate a single drive and return points scored.
    Returns: points scored on this drive
    """
    opponent = "Gunners" if team == "Bombers" else "Bombers"
    score = {team: 0, opponent: 0}

    # Roll for drive outcome
    drive_roll = random.randint(0, 19)
    y, t = TABLES[style][drive_roll]

    # Roll for turnover
    turnover_occurred = check_turnover(style)

    # Simplified drive resolution
    time_spent = t if isinstance(t, int) else 0
    yards = y if isinstance(y, int) else 0

    # Handle time overflow
    if time_spent > blocks_left:
        time_spent = blocks_left

    # Calculate end position
    end_x = advance(team, x, yards)

    # Check for safety
    if is_safety(team, end_x):
        return 0  # No points for offense (opponent gets 2)

    # Handle TD
    if y == "TD" or is_td_yardage(team, end_x):
        if turnover_occurred:
            return 0  # TD negated

        # Score TD + extra point
        extra_pts, conv_type = attempt_extra_point(team, score, blocks_left, 1)
        return 6 + extra_pts

    # Check turnover before 4th down
    if turnover_occurred:
        return 0

    # 4th down decision
    distance_to_goal = yards_to_endzone(team, end_x)

    # Determine yards to go based on style
    if style == "run":
        ytg_roll = random.randint(1, 8)
    elif style == "balanced":
        ytg_roll = random.randint(1, 10)
    else:  # pass
        ytg_roll = random.randint(1, 20)

    yards_to_go = min(ytg_roll, distance_to_goal)
    is_4th_and_goal = (ytg_roll >= distance_to_goal)

    # Decide whether to go for it (simplified probability)
    go_for_it_prob = 0.0
    if is_4th_and_goal:
        if distance_to_goal <= 3:
            go_for_it_prob = 0.60
        elif distance_to_goal <= 5:
            go_for_it_prob = 0.40
        else:
            go_for_it_prob = 0.20
    else:
        if yards_to_go <= 3:
            go_for_it_prob = 0.30
        elif yards_to_go <= 5:
            go_for_it_prob = 0.15
        else:
            go_for_it_prob = 0.05

    if distance_to_goal <= 20:
        go_for_it_prob += 0.15
    elif distance_to_goal <= 40:
        go_for_it_prob += 0.05

    go_for_it = random.random() < go_for_it_prob

    if go_for_it:
        # Attempt 4th down
        attempt_roll = random.randint(0, 19)
        result = FOURTH_DOWN_CONVERSION[attempt_roll]

        if result == "TD":
            extra_pts, conv_type = attempt_extra_point(team, score, blocks_left, 1)
            return 6 + extra_pts
        else:
            yards_gained = result
            new_x = advance(team, end_x, yards_gained)

            if is_td_yardage(team, new_x):
                extra_pts, conv_type = attempt_extra_point(team, score, blocks_left, 1)
                return 6 + extra_pts
            elif yards_gained >= yards_to_go:
                # First down - would continue, but for analysis we'll stop here
                return 0
            else:
                return 0  # Failed, turnover on downs

    # Not going for it - FG or punt
    if within_fg_range(team, end_x):
        fg_roll = random.randint(0, 19)
        make_distance = FIELD_GOAL_DISTANCE[fg_roll]
        distance = yards_to_endzone(team, end_x)
        success = make_distance >= distance

        if success:
            return 3
        else:
            return 0
    else:
        # Punt
        return 0

def analyze_drive_types(num_simulations: int = 10000):
    """Analyze average points per drive type from the 30 yard line"""

    results = {
        "balanced": [],
        "run": [],
        "pass": []
    }

    team = "Bombers"
    start_x = 30

    print(f"Simulating {num_simulations} drives of each type from the {start_x} yard line...\n")

    for style in ["balanced", "run", "pass"]:
        for _ in range(num_simulations):
            points = simulate_single_drive(team, start_x, style)
            results[style].append(points)

    print("=" * 60)
    print("DRIVE TYPE ANALYSIS - Starting at 30 Yard Line")
    print("=" * 60)
    print()

    for style in ["balanced", "run", "pass"]:
        pts = results[style]
        avg = sum(pts) / len(pts)

        # Count outcomes
        zeros = pts.count(0)
        threes = pts.count(3)
        sixes = pts.count(6)
        sevens = pts.count(7)
        eights = pts.count(8)

        print(f"{style.upper()} OFFENSE:")
        print(f"  Average Points per Drive: {avg:.3f}")
        print(f"  Outcomes (from {num_simulations} drives):")
        print(f"    0 points (punt/turnover/miss): {zeros} ({100*zeros/num_simulations:.1f}%)")
        print(f"    3 points (FG):                 {threes} ({100*threes/num_simulations:.1f}%)")
        print(f"    6 points (TD, missed XP):      {sixes} ({100*sixes/num_simulations:.1f}%)")
        print(f"    7 points (TD+1pt):             {sevens} ({100*sevens/num_simulations:.1f}%)")
        print(f"    8 points (TD+2pt):             {eights} ({100*eights/num_simulations:.1f}%)")
        print()

    # Comparison
    print("=" * 60)
    print("COMPARISON:")
    print("=" * 60)
    balanced_avg = sum(results["balanced"]) / len(results["balanced"])
    run_avg = sum(results["run"]) / len(results["run"])
    pass_avg = sum(results["pass"]) / len(results["pass"])

    styles_sorted = sorted([
        ("Balanced", balanced_avg),
        ("Run", run_avg),
        ("Pass", pass_avg)
    ], key=lambda x: x[1], reverse=True)

    for i, (style, avg) in enumerate(styles_sorted, 1):
        print(f"{i}. {style}: {avg:.3f} points per drive")
    print()

if __name__ == "__main__":
    random.seed()
    analyze_drive_types(10000)
