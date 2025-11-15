#!/usr/bin/env python3
"""
Generate a play aid reference table for Gridiron Dice Football
Shows drive outcomes for each play style and die roll
"""

from gridiron_dice import BALANCED, RUN_FIRST, PASS_FIRST

def generate_play_aid(output_file="PLAY_AID.md"):
    """Generate a markdown play aid table"""

    with open(output_file, 'w') as f:
        # Header
        f.write("# Gridiron Dice Football - Play Aid\n\n")
        f.write("## Drive Outcome Tables\n\n")
        f.write("Roll a d20 (0-19) and consult the table for your chosen play style.\n\n")
        f.write("**Format:** Yards / Time Blocks\n\n")

        # Create the main comparison table
        f.write("### Drive Outcome Comparison\n\n")
        f.write("| Roll | Balanced | Run-First | Pass-First |\n")
        f.write("|------|----------|-----------|------------|\n")

        for i in range(20):
            balanced_outcome = BALANCED[i]
            run_outcome = RUN_FIRST[i]
            pass_outcome = PASS_FIRST[i]

            # Format each outcome
            def format_outcome(outcome):
                yards, time = outcome
                if yards == "TD":
                    return "**TD** / 1-20"
                else:
                    return f"{yards} / {time}"

            f.write(f"| {i:2d}   | {format_outcome(balanced_outcome):12s} | {format_outcome(run_outcome):12s} | {format_outcome(pass_outcome):12s} |\n")

        # Individual style tables for detailed reference
        f.write("\n---\n\n")
        f.write("## Detailed Tables by Style\n\n")

        # Balanced
        f.write("### Balanced Offense\n\n")
        f.write("| Roll | Yards | Time Blocks | Notes |\n")
        f.write("|------|-------|-------------|-------|\n")
        for i, (yards, time) in enumerate(BALANCED):
            if yards == "TD":
                f.write(f"| {i:2d}   | TD    | 1-20        | Roll 1d20, cap by yards needed |\n")
            else:
                f.write(f"| {i:2d}   | {yards:3d}   | {time:2d}          |       |\n")

        f.write("\n")

        # Run-First
        f.write("### Run-First Offense\n\n")
        f.write("| Roll | Yards | Time Blocks | Notes |\n")
        f.write("|------|-------|-------------|-------|\n")
        for i, (yards, time) in enumerate(RUN_FIRST):
            if yards == "TD":
                f.write(f"| {i:2d}   | TD    | 1-20        | Roll 1d20, cap by yards needed |\n")
            else:
                f.write(f"| {i:2d}   | {yards:3d}   | {time:2d}          |       |\n")

        f.write("\n")

        # Pass-First
        f.write("### Pass-First Offense\n\n")
        f.write("| Roll | Yards | Time Blocks | Notes |\n")
        f.write("|------|-------|-------------|-------|\n")
        for i, (yards, time) in enumerate(PASS_FIRST):
            if yards == "TD":
                f.write(f"| {i:2d}   | TD    | 1-20        | Roll 1d20, cap by yards needed |\n")
            else:
                f.write(f"| {i:2d}   | {yards:3d}   | {time:2d}          |       |\n")

        f.write("\n---\n\n")

        # Game rules summary
        f.write("## Game Rules Summary\n\n")
        f.write("### Field Position\n")
        f.write("- Field coordinates: 0 (Bombers goal) to 100 (Gunners goal)\n")
        f.write("- Kickoffs start at team's own 30-yard line\n")
        f.write("- Field goal range: Within 35 yards of opponent's goal\n\n")

        f.write("### Time\n")
        f.write("- Each half: 180 time blocks (30 minutes game time)\n")
        f.write("- 1 time block = 10 seconds\n\n")

        f.write("### Drive Outcomes\n")
        f.write("- **Touchdown (TD):** Score 6 points + extra point attempt\n")
        f.write("  - **One-point conversion:** Roll on FG table, good if make distance ≥ 15 yards (~85% success)\n")
        f.write("  - **Two-point conversion:** Roll d10 (0-9), good on 6+ (40% success)\n")
        f.write("  - **Final TD score:** 6, 7, or 8 points total\n")
        f.write("  - **After scoring:** Opponent receives kickoff\n")
        f.write("- **Field Goal Attempts:** Within 50 yards\n")
        f.write("  - **Roll d20 (0-19)** and look up make distance:\n")
        f.write("    - 0: 0 yards | 1: 15 yards | 2: 20 yards | 3: 25 yards\n")
        f.write("    - 4-8: 30 yards | 9-12: 35 yards | 13-16: 40 yards | 17-19: 45 yards\n")
        f.write("  - **If make distance ≥ actual distance:** FG good (3 points)\n")
        f.write("  - **If make distance < actual distance:** FG miss, opponent gets ball 7 yards back (min their 20)\n")
        f.write("- **Punt:** Opponent gets ball 40 yards downfield (touchback at their 20)\n")
        f.write("- **Safety:**\n")
        f.write("  - **When:** Drive result pushes offense to/past their own goal line\n")
        f.write("  - **Check:** Happens BEFORE turnover check\n")
        f.write("  - **Effect:** Opponent scores 2 points, gets ball at their 30-yard line\n")
        f.write("- **Turnover (Roll d20 for each drive):**\n")
        f.write("  - **Run-first:** Turnover on 0 (5% chance)\n")
        f.write("  - **Balanced:** Turnover on 0-1 (10% chance)\n")
        f.write("  - **Pass-first:** Turnover on 0-2 (15% chance)\n")
        f.write("  - **Effect:** No punt/FG, opponent gets ball at current spot\n")
        f.write("  - **If TD:** TD negated, opponent gets ball at their 20\n")
        f.write("- **4th Down Conversions:**\n")
        f.write("  - **Yards to go determination:** Roll for yards to go (style-dependent)\n")
        f.write("    - **Run-first:** d8 (1-8 yards)\n")
        f.write("    - **Balanced:** d10 (1-10 yards)\n")
        f.write("    - **Pass-first:** d20 (1-20 yards)\n")
        f.write("  - **If yards to go ≥ distance to goal:** It's 4th and goal\n")
        f.write("  - **AI Decision:** Team decides whether to go for it based on:\n")
        f.write("    - Field position (more likely near goal)\n")
        f.write("    - Yards to go (more likely on 4th and short)\n")
        f.write("    - Game situation (trailing, late game)\n")
        f.write("  - **If going for it:** Roll d20 (0-19) for conversion attempt\n")
        f.write("    - **Results:** -10 to 30 yards, or automatic TD\n")
        f.write("    - **If 'TD' result or reaches end zone:** Touchdown (7 points), opponent gets ball\n")
        f.write("    - **If yards gained ≥ yards to go:** First down! Same team continues with fresh drive/new style\n")
        f.write("    - **Otherwise:** Turnover on downs (opponent gets ball)\n\n")

        f.write("### TD Time Cap Rule\n")
        f.write("When you roll a TD or gain enough yards to reach the end zone:\n")
        f.write("1. Roll 1d20 for time\n")
        f.write("2. Find the smallest non-TD row with yards ≥ yards needed\n")
        f.write("3. Use the minimum of the d20 roll and that row's time\n\n")

        f.write("### Late Half Rule\n")
        f.write("If time remaining is less than the drive time:\n")
        f.write("- Use the largest non-TD row that leaves ≥1 block\n")
        f.write("- If in FG range, attempt FG and half ends\n")
        f.write("- Otherwise, half ends immediately\n\n")

        f.write("### Play Style Selection (AI)\n")
        f.write("**With ≤60 blocks remaining (~10 min):**\n")
        f.write("- Trailing: 55% Pass, 35% Balanced, 10% Run\n")
        f.write("- Leading: 50% Run, 40% Balanced, 10% Pass\n")
        f.write("- Tied: 40% Pass, 45% Balanced, 15% Run\n\n")
        f.write("**Otherwise:**\n")
        f.write("- 50% Balanced, 30% Pass, 20% Run\n\n")

        f.write("---\n\n")
        f.write("*Generated by Gridiron Dice Football Simulator*\n")

    print(f"Play aid saved to: {output_file}")

if __name__ == "__main__":
    generate_play_aid()
    print("\nPlay aid generated! This reference shows all drive outcomes for quick table lookup.")
