#!/usr/bin/env python3
"""
Generate a human-readable drive chart document from a simulated game
"""

from gridiron_dice import simulate_game
from datetime import datetime

def format_drive_chart(game, output_file="DRIVE_CHART.md"):
    """Generate a markdown drive chart from a game result"""

    with open(output_file, 'w') as f:
        # Header
        f.write("# Game Drive Chart\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Final Score
        b_score = game.score['Bombers']
        g_score = game.score['Gunners']
        winner = "Bombers" if b_score > g_score else ("Gunners" if g_score > b_score else "TIE")

        f.write("## Final Score\n\n")
        f.write(f"**{game.score['Bombers']} - {game.score['Gunners']}**\n\n")
        if winner == "TIE":
            f.write("*Game ended in a tie*\n\n")
        else:
            f.write(f"*Winner: {winner}*\n\n")

        f.write("---\n\n")

        # Drive by drive breakdown
        f.write("## Drive Summary\n\n")

        # Group drives by half
        h1_drives = [d for d in game.drives if d.half == 1]
        h2_drives = [d for d in game.drives if d.half == 2]

        for half_num, drives in [(1, h1_drives), (2, h2_drives)]:
            f.write(f"### Half {half_num}\n\n")

            for i, drive in enumerate(drives, 1):
                # Drive header
                f.write(f"#### Drive {i}: {drive.team}\n\n")

                # Drive details
                f.write(f"- **Play Style:** {drive.style.title()}\n")
                f.write(f"- **Starting Position:** {drive.start_x} yard line\n")
                f.write(f"- **Ending Position:** {drive.end_x} yard line\n")
                f.write(f"- **Yards Gained:** {drive.yards}\n")
                f.write(f"- **Time Consumed:** {drive.time_blocks} blocks ({drive.time_blocks * 10} seconds)\n")
                f.write(f"- **Result:** {drive.result}\n")
                f.write(f"- **Points Scored:** {drive.points}\n")

                # Running score
                running_b = sum(d.points for d in game.drives[:game.drives.index(drive)+1] if d.team == "Bombers")
                running_g = sum(d.points for d in game.drives[:game.drives.index(drive)+1] if d.team == "Gunners")
                f.write(f"- **Score After Drive:** Bombers {running_b} - Gunners {running_g}\n")

                f.write("\n")

            f.write("---\n\n")

        # Game Statistics
        f.write("## Game Statistics\n\n")

        bombers_drives = [d for d in game.drives if d.team == "Bombers"]
        gunners_drives = [d for d in game.drives if d.team == "Gunners"]

        f.write("| Stat | Bombers | Gunners |\n")
        f.write("|------|---------|--------|\n")
        f.write(f"| Total Drives | {len(bombers_drives)} | {len(gunners_drives)} |\n")
        f.write(f"| Total Points | {game.score['Bombers']} | {game.score['Gunners']} |\n")

        # Count scoring drives
        b_tds = sum(1 for d in bombers_drives if 'TD' in d.result)
        g_tds = sum(1 for d in gunners_drives if 'TD' in d.result)
        f.write(f"| Touchdowns | {b_tds} | {g_tds} |\n")

        b_fgs = sum(1 for d in bombers_drives if 'FG Good' in d.result)
        g_fgs = sum(1 for d in gunners_drives if 'FG Good' in d.result)
        f.write(f"| Field Goals Made | {b_fgs} | {g_fgs} |\n")

        b_fg_miss = sum(1 for d in bombers_drives if 'FG Miss' in d.result)
        g_fg_miss = sum(1 for d in gunners_drives if 'FG Miss' in d.result)
        f.write(f"| Field Goals Missed | {b_fg_miss} | {g_fg_miss} |\n")

        b_punts = sum(1 for d in bombers_drives if d.result == 'Punt')
        g_punts = sum(1 for d in gunners_drives if d.result == 'Punt')
        f.write(f"| Punts | {b_punts} | {g_punts} |\n")

        # Calculate total yards
        b_yards = sum(d.yards for d in bombers_drives if isinstance(d.yards, int))
        g_yards = sum(d.yards for d in gunners_drives if isinstance(d.yards, int))
        f.write(f"| Total Yards | {b_yards} | {g_yards} |\n")

        # Average yards per drive
        b_avg = b_yards / len(bombers_drives) if bombers_drives else 0
        g_avg = g_yards / len(gunners_drives) if gunners_drives else 0
        f.write(f"| Avg Yards/Drive | {b_avg:.1f} | {g_avg:.1f} |\n")

        # Total time of possession
        b_time = sum(d.time_blocks for d in bombers_drives)
        g_time = sum(d.time_blocks for d in gunners_drives)
        f.write(f"| Time of Possession (blocks) | {b_time} | {g_time} |\n")
        f.write(f"| Time of Possession (min:sec) | {b_time//6}:{(b_time%6)*10:02d} | {g_time//6}:{(g_time%6)*10:02d} |\n")

        f.write("\n")

        # Play style breakdown
        f.write("## Play Style Usage\n\n")

        for team_name, team_drives in [("Bombers", bombers_drives), ("Gunners", gunners_drives)]:
            f.write(f"### {team_name}\n\n")
            balanced = sum(1 for d in team_drives if d.style == "balanced")
            run = sum(1 for d in team_drives if d.style == "run")
            pass_style = sum(1 for d in team_drives if d.style == "pass")
            total = len(team_drives)

            if total > 0:
                f.write(f"- **Balanced:** {balanced} drives ({100*balanced/total:.1f}%)\n")
                f.write(f"- **Run:** {run} drives ({100*run/total:.1f}%)\n")
                f.write(f"- **Pass:** {pass_style} drives ({100*pass_style/total:.1f}%)\n")
            f.write("\n")

        f.write("---\n\n")
        f.write("*Generated by Gridiron Dice Football Simulator*\n")

    print(f"Drive chart saved to: {output_file}")

if __name__ == "__main__":
    print("Simulating game...")
    game = simulate_game()
    print(f"Final Score: Bombers {game.score['Bombers']} - Gunners {game.score['Gunners']}")
    print()
    format_drive_chart(game)
