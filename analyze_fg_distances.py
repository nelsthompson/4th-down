#!/usr/bin/env python3
"""
Analyze field goal attempt distances by play style
"""

import random
from gridiron_dice import *

def simulate_drive_fg_tracking(team: str, x: int, style: str, blocks_left: int = 180) -> dict:
    """
    Simulate a single drive and track field goal attempt distance.
    Returns: dict with FG details
    """
    opponent = "Gunners" if team == "Bombers" else "Bombers"
    score = {team: 0, opponent: 0}

    # Roll for drive outcome
    drive_roll = random.randint(1, 20)
    y, t = TABLES[style][drive_roll - 1]

    # Roll for turnover
    turnover_occurred = check_turnover(style)

    # Track outcomes
    result = {
        "fg_attempted": False,
        "fg_distance": None,
        "fg_made": False
    }

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
        return result

    # Handle TD
    if y == "TD" or is_td_yardage(team, end_x):
        return result

    # Check turnover before 4th down
    if turnover_occurred:
        return result

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
        # Going for it, no FG attempt
        return result

    # Not going for it - FG or punt
    if within_fg_range(team, end_x):
        distance = yards_to_endzone(team, end_x)
        result["fg_attempted"] = True
        result["fg_distance"] = distance

        fg_roll = random.randint(1, 20)
        make_distance = FIELD_GOAL_DISTANCE[fg_roll - 1]
        success = make_distance >= distance

        if success:
            result["fg_made"] = True

    return result

def analyze_fg_distances(num_simulations: int = 10000):
    """Analyze field goal attempt distances by play style"""

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
            drive_result = simulate_drive_fg_tracking(team, start_x, style)
            results[style].append(drive_result)

    print("=" * 70)
    print("FIELD GOAL DISTANCE ANALYSIS")
    print("=" * 70)
    print()

    for style in ["balanced", "run", "pass"]:
        drives = results[style]

        fg_attempts = [d for d in drives if d["fg_attempted"]]
        total_attempts = len(fg_attempts)

        if total_attempts == 0:
            print(f"{style.upper()} OFFENSE: No field goal attempts")
            continue

        distances = [d["fg_distance"] for d in fg_attempts]
        avg_distance = sum(distances) / len(distances)

        # Categorize by distance
        under_30 = sum(1 for d in distances if d < 30)
        range_30_40 = sum(1 for d in distances if 30 <= d <= 40)
        range_41_50 = sum(1 for d in distances if 41 <= d <= 50)

        # Success rates by distance
        made_under_30 = sum(1 for d in fg_attempts if d["fg_distance"] < 30 and d["fg_made"])
        made_30_40 = sum(1 for d in fg_attempts if 30 <= d["fg_distance"] <= 40 and d["fg_made"])
        made_41_50 = sum(1 for d in fg_attempts if 41 <= d["fg_distance"] <= 50 and d["fg_made"])

        total_made = sum(1 for d in fg_attempts if d["fg_made"])

        print(f"{style.upper()} OFFENSE:")
        print(f"  Total Drives:              {num_simulations}")
        print(f"  FG Attempts:               {total_attempts} ({total_attempts/num_simulations*100:.1f}%)")
        print(f"  FGs Made:                  {total_made} ({total_made/total_attempts*100:.1f}% success)")
        print(f"  Average FG Distance:       {avg_distance:.1f} yards")
        print()
        print(f"  Distance Breakdown:")
        print(f"    Under 30 yards:          {under_30:4d} ({under_30/total_attempts*100:5.1f}%)")
        if under_30 > 0:
            print(f"      Success rate:          {made_under_30}/{under_30} ({made_under_30/under_30*100:.1f}%)")
        print(f"    30-40 yards:             {range_30_40:4d} ({range_30_40/total_attempts*100:5.1f}%)")
        if range_30_40 > 0:
            print(f"      Success rate:          {made_30_40}/{range_30_40} ({made_30_40/range_30_40*100:.1f}%)")
        print(f"    41-50 yards:             {range_41_50:4d} ({range_41_50/total_attempts*100:5.1f}%)")
        if range_41_50 > 0:
            print(f"      Success rate:          {made_41_50}/{range_41_50} ({made_41_50/range_41_50*100:.1f}%)")
        print()
        print(f"  Attempts over 40 yards:    {range_41_50} ({range_41_50/total_attempts*100:.1f}%)")
        print(f"  Attempts over 40 yards     {range_41_50} ({range_41_50/num_simulations*100:.1f}% of all drives)")
        print()
        print("-" * 70)
        print()

    # Comparison table
    print("=" * 70)
    print("COMPARISON TABLE:")
    print("=" * 70)
    print()
    print("Metric                       BALANCED    RUN-FIRST   PASS-FIRST")
    print("                             --------    ---------   ----------")

    for style_name in ["balanced", "run", "pass"]:
        style_drives = results[style_name]
        fg_attempts = [d for d in style_drives if d["fg_attempted"]]

        globals()[f"{style_name}_total_attempts"] = len(fg_attempts)
        if len(fg_attempts) > 0:
            globals()[f"{style_name}_avg_dist"] = sum(d["fg_distance"] for d in fg_attempts) / len(fg_attempts)
            globals()[f"{style_name}_over_40"] = sum(1 for d in fg_attempts if d["fg_distance"] > 40)
            globals()[f"{style_name}_over_40_pct"] = globals()[f"{style_name}_over_40"] / len(fg_attempts) * 100
        else:
            globals()[f"{style_name}_avg_dist"] = 0
            globals()[f"{style_name}_over_40"] = 0
            globals()[f"{style_name}_over_40_pct"] = 0

    print(f"FG Attempts (% of drives)    {balanced_total_attempts/num_simulations*100:6.1f}%      {run_total_attempts/num_simulations*100:6.1f}%      {pass_total_attempts/num_simulations*100:6.1f}%")
    print(f"Avg FG Distance (yards)      {balanced_avg_dist:6.1f}      {run_avg_dist:6.1f}      {pass_avg_dist:6.1f}")
    print(f"Over 40 yards (count)        {balanced_over_40:6d}      {run_over_40:6d}      {pass_over_40:6d}")
    print(f"Over 40 yards (% of FGs)     {balanced_over_40_pct:6.1f}%      {run_over_40_pct:6.1f}%      {pass_over_40_pct:6.1f}%")
    print()

if __name__ == "__main__":
    random.seed()
    analyze_fg_distances(10000)
