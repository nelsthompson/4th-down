#!/usr/bin/env python3
"""
Analyze average points per drive by drive type from the 30 yard line
"""

import random
from gridiron_dice import *

def simulate_single_drive(team: str, x: int, style: str, blocks_left: int = 180) -> tuple:
    """
    Simulate a single drive and return comprehensive stats.
    Returns: (points, is_td, is_fg_good, opponent_start_x)
    """
    opponent = "Gunners" if team == "Bombers" else "Bombers"
    score = {team: 0, opponent: 0}

    # Roll for drive outcome
    drive_roll = random.randint(1, 20)
    y, t = TABLES[style][drive_roll - 1]

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
        # Opponent gets ball at their 30
        opponent_x = kickoff_position(opponent)
        return 0, 0, 0, opponent_x  # No points for offense

    # Handle TD
    if y == "TD" or is_td_yardage(team, end_x):
        if turnover_occurred:
            # TD negated, opponent gets ball at their 20
            opponent_x = 20 if opponent == "Bombers" else 80
            return 0, 0, 0, opponent_x

        # Score TD + extra point
        extra_pts, conv_type = attempt_extra_point(team, score, blocks_left, 1)
        total_pts = 6 + extra_pts
        # After TD, opponent gets kickoff at their 30
        opponent_x = kickoff_position(opponent)
        return total_pts, 1, 0, opponent_x

    # Check turnover before 4th down
    if turnover_occurred:
        # Opponent gets ball at current position
        return 0, 0, 0, end_x

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
        attempt_roll = random.randint(1, 20)
        result = FOURTH_DOWN_CONVERSION[attempt_roll - 1]

        if result == "TD":
            extra_pts, conv_type = attempt_extra_point(team, score, blocks_left, 1)
            total_pts = 6 + extra_pts
            opponent_x = kickoff_position(opponent)
            return total_pts, 1, 0, opponent_x
        else:
            yards_gained = result
            new_x = advance(team, end_x, yards_gained)

            if is_td_yardage(team, new_x):
                extra_pts, conv_type = attempt_extra_point(team, score, blocks_left, 1)
                total_pts = 6 + extra_pts
                opponent_x = kickoff_position(opponent)
                return total_pts, 1, 0, opponent_x
            elif yards_gained >= yards_to_go:
                # First down - for analysis, treat as end of drive with no score
                # Opponent doesn't get ball, so return None for opponent_x
                return 0, 0, 0, None
            else:
                # Turnover on downs, opponent gets ball at new position
                return 0, 0, 0, new_x

    # Not going for it - FG or punt
    if within_fg_range(team, end_x):
        fg_roll = random.randint(1, 20)
        make_distance = FIELD_GOAL_DISTANCE[fg_roll - 1]
        distance = yards_to_endzone(team, end_x)
        success = make_distance >= distance

        if success:
            # FG good, opponent gets kickoff at their 30
            opponent_x = kickoff_position(opponent)
            return 3, 0, 1, opponent_x
        else:
            # FG miss, opponent gets ball 7 yards back (min their 20)
            miss_spot = missed_fg_spot(team, end_x)
            return 0, 0, 0, miss_spot
    else:
        # Punt - opponent gets ball 40 yards downfield (touchback at 20)
        punt_x = punt_spot(team, end_x)
        return 0, 0, 0, punt_x

def analyze_drive_types(num_simulations: int = 10000):
    """Analyze average points per drive type from the 30 yard line"""

    results = {
        "balanced": {"points": [], "tds": [], "fgs": [], "opponent_starts": []},
        "run": {"points": [], "tds": [], "fgs": [], "opponent_starts": []},
        "pass": {"points": [], "tds": [], "fgs": [], "opponent_starts": []}
    }

    team = "Bombers"
    start_x = 30

    print(f"Simulating {num_simulations} drives of each type from the {start_x} yard line...\n")

    for style in ["balanced", "run", "pass"]:
        for _ in range(num_simulations):
            points, is_td, is_fg, opponent_x = simulate_single_drive(team, start_x, style)
            results[style]["points"].append(points)
            results[style]["tds"].append(is_td)
            results[style]["fgs"].append(is_fg)
            if opponent_x is not None:  # Only count when opponent actually gets ball
                results[style]["opponent_starts"].append(opponent_x)

    print("=" * 70)
    print("COMPREHENSIVE DRIVE TYPE ANALYSIS - Starting at 30 Yard Line")
    print("=" * 70)
    print()

    for style in ["balanced", "run", "pass"]:
        data = results[style]

        # Calculate averages
        avg_points = sum(data["points"]) / len(data["points"])
        avg_tds = sum(data["tds"]) / len(data["tds"])
        avg_fgs = sum(data["fgs"]) / len(data["fgs"])

        # Opponent starting position (only when they get the ball)
        if data["opponent_starts"]:
            avg_opponent_start = sum(data["opponent_starts"]) / len(data["opponent_starts"])
        else:
            avg_opponent_start = 0

        print(f"{style.upper()} OFFENSE:")
        print(f"  Average Points per Drive:        {avg_points:.3f}")
        print(f"  Average TDs per Drive:            {avg_tds:.3f} ({avg_tds*100:.1f}%)")
        print(f"  Average Successful FGs per Drive: {avg_fgs:.3f} ({avg_fgs*100:.1f}%)")
        print(f"  Avg Opponent Start Position:      {avg_opponent_start:.1f} yard line")
        print()

        # Detailed breakdown
        zeros = data["points"].count(0)
        threes = data["points"].count(3)
        sixes = data["points"].count(6)
        sevens = data["points"].count(7)
        eights = data["points"].count(8)

        print(f"  Points Distribution:")
        print(f"    0 points: {zeros:5d} ({100*zeros/num_simulations:5.1f}%)")
        print(f"    3 points: {threes:5d} ({100*threes/num_simulations:5.1f}%)")
        print(f"    6 points: {sixes:5d} ({100*sixes/num_simulations:5.1f}%)")
        print(f"    7 points: {sevens:5d} ({100*sevens/num_simulations:5.1f}%)")
        print(f"    8 points: {eights:5d} ({100*eights/num_simulations:5.1f}%)")
        print()

    # Comparison summary
    print("=" * 70)
    print("COMPARISON SUMMARY:")
    print("=" * 70)
    print()

    print("                        BALANCED    RUN-FIRST   PASS-FIRST")
    print("                        --------    ---------   ----------")

    bal_avg_pts = sum(results["balanced"]["points"]) / len(results["balanced"]["points"])
    run_avg_pts = sum(results["run"]["points"]) / len(results["run"]["points"])
    pass_avg_pts = sum(results["pass"]["points"]) / len(results["pass"]["points"])
    print(f"Points per Drive:       {bal_avg_pts:8.3f}    {run_avg_pts:9.3f}   {pass_avg_pts:10.3f}")

    bal_avg_tds = sum(results["balanced"]["tds"]) / len(results["balanced"]["tds"])
    run_avg_tds = sum(results["run"]["tds"]) / len(results["run"]["tds"])
    pass_avg_tds = sum(results["pass"]["tds"]) / len(results["pass"]["tds"])
    print(f"TDs per Drive:          {bal_avg_tds:8.3f}    {run_avg_tds:9.3f}   {pass_avg_tds:10.3f}")

    bal_avg_fgs = sum(results["balanced"]["fgs"]) / len(results["balanced"]["fgs"])
    run_avg_fgs = sum(results["run"]["fgs"]) / len(results["run"]["fgs"])
    pass_avg_fgs = sum(results["pass"]["fgs"]) / len(results["pass"]["fgs"])
    print(f"FGs per Drive:          {bal_avg_fgs:8.3f}    {run_avg_fgs:9.3f}   {pass_avg_fgs:10.3f}")

    bal_avg_opp = sum(results["balanced"]["opponent_starts"]) / len(results["balanced"]["opponent_starts"]) if results["balanced"]["opponent_starts"] else 0
    run_avg_opp = sum(results["run"]["opponent_starts"]) / len(results["run"]["opponent_starts"]) if results["run"]["opponent_starts"] else 0
    pass_avg_opp = sum(results["pass"]["opponent_starts"]) / len(results["pass"]["opponent_starts"]) if results["pass"]["opponent_starts"] else 0
    print(f"Opponent Start Pos:     {bal_avg_opp:8.1f}    {run_avg_opp:9.1f}   {pass_avg_opp:10.1f}")
    print()

    # Field position analysis
    print("OPPONENT STARTING FIELD POSITION ANALYSIS:")
    print("(Lower is better for offense - pins opponent deeper)")
    print()

    for style in ["balanced", "run", "pass"]:
        opp_starts = results[style]["opponent_starts"]
        if opp_starts:
            avg = sum(opp_starts) / len(opp_starts)
            # Count how many times opponent starts at different zones
            own_20 = sum(1 for x in opp_starts if (x <= 20 or x >= 80))
            own_30 = sum(1 for x in opp_starts if ((21 <= x <= 30) or (70 <= x <= 79)))
            midfield = sum(1 for x in opp_starts if (31 <= x <= 69))

            print(f"{style.upper()}:")
            print(f"  Average: {avg:.1f} yard line")
            print(f"  Opponent at own 20 or worse: {100*own_20/len(opp_starts):.1f}%")
            print(f"  Opponent at own 30:          {100*own_30/len(opp_starts):.1f}%")
            print(f"  Opponent at midfield or better: {100*midfield/len(opp_starts):.1f}%")
            print()

if __name__ == "__main__":
    random.seed()
    analyze_drive_types(10000)
