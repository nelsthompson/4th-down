#!/usr/bin/env python3
"""
Generate a detailed drive chart with all rolls and decisions shown
"""

import random
from gridiron_dice import *

def simulate_detailed_game(output_file="DRIVE_CHART.md"):
    """Simulate a game with detailed roll logging"""

    random.seed()  # Random seed for variety

    with open(output_file, 'w') as f:
        f.write("# Detailed Game Drive Chart\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        score = {"Bombers": 0, "Gunners": 0}

        # Simulate both halves
        all_drives = []

        # Half 1
        f.write("## Half 1\n\n")
        team = "Bombers"
        x = 30
        blocks = BLOCKS_PER_HALF
        drive_num = 1

        for half in [1, 2]:
            if half == 2:
                f.write("\n---\n\n## Half 2\n\n")
                team = "Gunners"
                x = 70
                blocks = BLOCKS_PER_HALF

            while blocks > 0:
                opponent = "Gunners" if team == "Bombers" else "Bombers"
                lead = score[team] - score[opponent]

                # Choose style
                style = choose_style(team, lead, blocks)

                f.write(f"### Drive {drive_num}: {team}\n\n")
                f.write(f"**Starting Position:** {x} yard line | **Time Remaining:** {blocks} blocks\n")
                f.write(f"**Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n")
                f.write(f"**Play Style Selected:** {style.upper()}\n\n")

                # Roll for drive outcome
                drive_roll = random.randint(0, 19)
                y, t = TABLES[style][drive_roll]
                f.write(f"**Drive Roll:** {drive_roll} → Result: {y} yards, {t} time blocks\n")

                # Roll for turnover
                turnover_roll = random.randint(0, 19)
                turnover_occurred = turnover_roll in TURNOVER_THRESHOLDS[style]
                f.write(f"**Turnover Check:** {turnover_roll} → {'TURNOVER' if turnover_occurred else 'No turnover'}\n")

                # Simplified drive resolution for detailed output
                time_spent = t if isinstance(t, int) else 0
                yards = y if isinstance(y, int) else 0

                # Handle time overflow
                if time_spent > blocks:
                    time_spent = blocks

                # Calculate end position
                end_x = advance(team, x, yards)

                # Check for safety
                if is_safety(team, end_x):
                    f.write(f"\n**SAFETY!** Opponent scores 2 points\n")
                    score[opponent] += 2
                    f.write(f"**Drive Result:** Safety | **Points:** 0 (opponent +2)\n")
                    f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                    blocks -= time_spent
                    team = opponent
                    x = kickoff_position(opponent)
                    drive_num += 1
                    continue

                # Handle TD
                if y == "TD" or is_td_yardage(team, end_x):
                    if turnover_occurred:
                        f.write(f"\n**TD negated by turnover!**\n")
                        opponent_20 = 20 if opponent == "Bombers" else 80
                        f.write(f"**Drive Result:** Turnover (would be TD) | **Points:** 0\n")
                        f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                        blocks -= time_spent
                        team = opponent
                        x = opponent_20
                        drive_num += 1
                        continue

                    # Score TD + extra point
                    f.write(f"\n**TOUCHDOWN!** 6 points\n")

                    # Decide 1pt or 2pt
                    go_for_two = False
                    if blocks <= 60:
                        if lead <= -8:
                            go_for_two = random.random() < 0.70
                        elif lead == -7:
                            go_for_two = random.random() < 0.80
                        elif lead == -6:
                            go_for_two = random.random() < 0.20

                    if go_for_two:
                        f.write(f"**Extra Point Decision:** Go for 2-point conversion\n")
                        conv_roll = random.randint(0, 9)
                        success = conv_roll >= 6
                        f.write(f"**2pt Attempt Roll (d10):** {conv_roll} → {'GOOD' if success else 'FAILED'}\n")
                        extra_pts = 2 if success else 0
                        conv_type = "2pt"
                    else:
                        f.write(f"**Extra Point Decision:** Go for 1-point conversion\n")
                        fg_roll = random.randint(0, 19)
                        make_distance = FIELD_GOAL_DISTANCE[fg_roll]
                        success = make_distance >= 15
                        f.write(f"**1pt Attempt Roll (d20):** {fg_roll} → Make distance: {make_distance} yards → {'GOOD' if success else 'FAILED'}\n")
                        extra_pts = 1 if success else 0
                        conv_type = "1pt"

                    total_pts = 6 + extra_pts
                    score[team] += total_pts
                    f.write(f"**Drive Result:** TD+{conv_type} | **Points:** {total_pts}\n")
                    f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")

                    blocks -= time_spent
                    team = opponent
                    x = kickoff_position(opponent)
                    drive_num += 1
                    continue

                # Check turnover before 4th down
                if turnover_occurred:
                    f.write(f"\n**Drive Result:** Turnover | **Points:** 0\n")
                    f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                    blocks -= time_spent
                    team = opponent
                    x = end_x
                    drive_num += 1
                    continue

                # 4th down decision
                distance_to_goal = yards_to_endzone(team, end_x)

                # Determine yards to go
                if style == "run":
                    ytg_roll = random.randint(1, 8)
                elif style == "balanced":
                    ytg_roll = random.randint(1, 10)
                else:  # pass
                    ytg_roll = random.randint(1, 20)

                yards_to_go = min(ytg_roll, distance_to_goal)
                is_4th_and_goal = (ytg_roll >= distance_to_goal)

                f.write(f"\n**4th Down Distance Roll:** {ytg_roll} yards")
                if is_4th_and_goal:
                    f.write(f" → 4th and goal from {distance_to_goal}\n")
                else:
                    f.write(f" → 4th and {yards_to_go}\n")

                # Decide whether to go for it
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

                if blocks <= 60:
                    if lead < 0:
                        go_for_it_prob += 0.10

                go_for_it = random.random() < go_for_it_prob

                f.write(f"**Go For It Decision:** {go_for_it_prob*100:.0f}% chance → {'GO FOR IT' if go_for_it else 'KICK/PUNT'}\n")

                if go_for_it:
                    # Attempt 4th down
                    attempt_roll = random.randint(0, 19)
                    result = FOURTH_DOWN_CONVERSION[attempt_roll]
                    f.write(f"**4th Down Attempt Roll (d20):** {attempt_roll} → {result} yards")

                    if result == "TD":
                        f.write(f" → TOUCHDOWN!\n")
                        # Score TD + extra point
                        f.write(f"\n**TOUCHDOWN!** 6 points\n")

                        # Extra point (simplified)
                        conv_roll = random.randint(0, 19)
                        make_distance = FIELD_GOAL_DISTANCE[conv_roll]
                        success = make_distance >= 15
                        f.write(f"**1pt Attempt Roll:** {conv_roll} → Make distance: {make_distance} → {'GOOD' if success else 'FAILED'}\n")
                        extra_pts = 1 if success else 0
                        total_pts = 6 + extra_pts
                        score[team] += total_pts

                        f.write(f"**Drive Result:** 4th down TD+1pt | **Points:** {total_pts}\n")
                        f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")

                        blocks -= time_spent
                        team = opponent
                        x = kickoff_position(opponent)
                        drive_num += 1
                        continue
                    else:
                        yards_gained = result
                        new_x = advance(team, end_x, yards_gained)

                        if is_td_yardage(team, new_x):
                            f.write(f" → Reaches end zone! TOUCHDOWN!\n")
                            # Score TD (similar to above, simplified)
                            score[team] += 7
                            f.write(f"**Drive Result:** 4th down TD | **Points:** 7\n")
                            f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                            blocks -= time_spent
                            team = opponent
                            x = kickoff_position(opponent)
                            drive_num += 1
                            continue
                        elif yards_gained >= yards_to_go:
                            f.write(f" → FIRST DOWN!\n")
                            f.write(f"**Drive Result:** 4th down conversion | **Points:** 0\n")
                            f.write(f"**Ball moves to {new_x} yard line, same team continues**\n")
                            f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                            blocks -= time_spent
                            x = new_x
                            drive_num += 1
                            continue
                        else:
                            f.write(f" → FAILED (need {yards_to_go}, got {yards_gained})\n")
                            f.write(f"**Drive Result:** Turnover on downs | **Points:** 0\n")
                            f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                            blocks -= time_spent
                            team = opponent
                            x = new_x
                            drive_num += 1
                            continue

                # Not going for it - FG or punt
                if within_fg_range(team, end_x):
                    fg_roll = random.randint(0, 19)
                    make_distance = FIELD_GOAL_DISTANCE[fg_roll]
                    distance = yards_to_endzone(team, end_x)
                    success = make_distance >= distance

                    f.write(f"**Field Goal Attempt from {distance} yards**\n")
                    f.write(f"**FG Roll (d20):** {fg_roll} → Make distance: {make_distance} yards → {'GOOD' if success else 'MISS'}\n")

                    if success:
                        score[team] += 3
                        f.write(f"**Drive Result:** FG Good | **Points:** 3\n")
                        f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                        blocks -= time_spent
                        team = opponent
                        x = kickoff_position(opponent)
                    else:
                        miss_spot = missed_fg_spot(team, end_x)
                        f.write(f"**Drive Result:** FG Miss | **Points:** 0\n")
                        f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                        blocks -= time_spent
                        team = opponent
                        x = miss_spot
                else:
                    spot = punt_spot(team, end_x)
                    f.write(f"**PUNT (40 yards)**\n")
                    f.write(f"**Drive Result:** Punt | **Points:** 0\n")
                    f.write(f"**Final Score:** Bombers {score['Bombers']} - Gunners {score['Gunners']}\n\n")
                    blocks -= time_spent
                    team = opponent
                    x = spot

                drive_num += 1

        f.write("\n---\n\n")
        f.write(f"## Final Score\n\n")
        f.write(f"**Bombers {score['Bombers']} - Gunners {score['Gunners']}**\n\n")
        if score['Bombers'] > score['Gunners']:
            f.write("**Winner: Bombers**\n")
        elif score['Gunners'] > score['Bombers']:
            f.write("**Winner: Gunners**\n")
        else:
            f.write("**TIE GAME**\n")

    print(f"Detailed drive chart saved to: {output_file}")

if __name__ == "__main__":
    from datetime import datetime
    simulate_detailed_game()
