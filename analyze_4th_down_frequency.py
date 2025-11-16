#!/usr/bin/env python3
"""
Analyze 4th down attempt frequency by play style
"""

import random
from gridiron_dice import *

def simulate_drive_4th_down_tracking(team: str, x: int, style: str, blocks_left: int = 180) -> dict:
    """
    Simulate a single drive and track 4th down decisions.
    Returns: dict with drive outcome details
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
        "attempted_4th": False,
        "converted_4th": False,
        "fg_attempt": False,
        "fg_made": False,
        "punt": False,
        "td": False,
        "turnover": False,
        "safety": False
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
        result["safety"] = True
        return result

    # Handle TD
    if y == "TD" or is_td_yardage(team, end_x):
        if turnover_occurred:
            result["turnover"] = True
            return result

        result["td"] = True
        return result

    # Check turnover before 4th down
    if turnover_occurred:
        result["turnover"] = True
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
        result["attempted_4th"] = True

        # Attempt 4th down
        attempt_roll = random.randint(1, 20)
        conversion_result = FOURTH_DOWN_CONVERSION[attempt_roll - 1]

        if conversion_result == "TD":
            result["td"] = True
            result["converted_4th"] = True
            return result
        else:
            yards_gained = conversion_result
            new_x = advance(team, end_x, yards_gained)

            if is_td_yardage(team, new_x):
                result["td"] = True
                result["converted_4th"] = True
                return result
            elif yards_gained >= yards_to_go:
                result["converted_4th"] = True
                return result
            else:
                # Failed 4th down
                return result

    # Not going for it - FG or punt
    if within_fg_range(team, end_x):
        result["fg_attempt"] = True

        fg_roll = random.randint(1, 20)
        make_distance = FIELD_GOAL_DISTANCE[fg_roll - 1]
        distance = yards_to_endzone(team, end_x)
        success = make_distance >= distance

        if success:
            result["fg_made"] = True
        return result
    else:
        result["punt"] = True
        return result

def analyze_4th_down_frequency(num_simulations: int = 10000):
    """Analyze 4th down attempt frequency by play style"""

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
            drive_result = simulate_drive_4th_down_tracking(team, start_x, style)
            results[style].append(drive_result)

    print("=" * 70)
    print("4TH DOWN ATTEMPT FREQUENCY ANALYSIS")
    print("=" * 70)
    print()

    for style in ["balanced", "run", "pass"]:
        drives = results[style]

        attempted = sum(1 for d in drives if d["attempted_4th"])
        converted = sum(1 for d in drives if d["converted_4th"])
        fg_attempts = sum(1 for d in drives if d["fg_attempt"])
        fg_made = sum(1 for d in drives if d["fg_made"])
        punts = sum(1 for d in drives if d["punt"])
        tds = sum(1 for d in drives if d["td"])
        turnovers = sum(1 for d in drives if d["turnover"])
        safeties = sum(1 for d in drives if d["safety"])

        conversion_rate = (converted / attempted * 100) if attempted > 0 else 0
        fg_success_rate = (fg_made / fg_attempts * 100) if fg_attempts > 0 else 0

        print(f"{style.upper()} OFFENSE:")
        print(f"  Total Drives:              {num_simulations}")
        print(f"  Touchdowns:                {tds:5d} ({tds/num_simulations*100:5.1f}%)")
        print(f"  Turnovers:                 {turnovers:5d} ({turnovers/num_simulations*100:5.1f}%)")
        print(f"  Safeties:                  {safeties:5d} ({safeties/num_simulations*100:5.1f}%)")
        print()
        print(f"  4th Down Attempts:         {attempted:5d} ({attempted/num_simulations*100:5.1f}%)")
        print(f"  4th Down Conversions:      {converted:5d} ({conversion_rate:5.1f}% success)")
        print()
        print(f"  Field Goal Attempts:       {fg_attempts:5d} ({fg_attempts/num_simulations*100:5.1f}%)")
        print(f"  Field Goals Made:          {fg_made:5d} ({fg_success_rate:5.1f}% success)")
        print()
        print(f"  Punts:                     {punts:5d} ({punts/num_simulations*100:5.1f}%)")
        print()
        print("-" * 70)
        print()

    # Comparison table
    print("=" * 70)
    print("COMPARISON TABLE:")
    print("=" * 70)
    print()
    print("Metric                  BALANCED    RUN-FIRST   PASS-FIRST")
    print("                        --------    ---------   ----------")

    for metric, label in [
        ("attempted_4th", "4th Down Attempts"),
        ("converted_4th", "4th Down Conversions"),
        ("fg_attempt", "FG Attempts"),
        ("fg_made", "FGs Made"),
        ("punt", "Punts"),
        ("td", "Touchdowns"),
        ("turnover", "Turnovers")
    ]:
        bal = sum(1 for d in results["balanced"] if d[metric]) / num_simulations * 100
        run = sum(1 for d in results["run"] if d[metric]) / num_simulations * 100
        pas = sum(1 for d in results["pass"] if d[metric]) / num_simulations * 100
        print(f"{label:22s}  {bal:6.1f}%      {run:6.1f}%      {pas:6.1f}%")

    print()

if __name__ == "__main__":
    random.seed()
    analyze_4th_down_frequency(10000)
