#!/usr/bin/env python3
"""
Generate drive outcome tables as CSV file
"""

import csv
from gridiron_dice import BALANCED, RUN_FIRST, PASS_FIRST

def generate_drive_csv(output_file="drive_outcomes.csv"):
    """Generate CSV file with drive outcome tables"""

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header row
        writer.writerow([
            'Roll',
            'Balanced Yards', 'Balanced Time',
            'Run-First Yards', 'Run-First Time',
            'Pass-First Yards', 'Pass-First Time'
        ])

        # Data rows
        for i in range(20):
            balanced_yards, balanced_time = BALANCED[i]
            run_yards, run_time = RUN_FIRST[i]
            pass_yards, pass_time = PASS_FIRST[i]

            writer.writerow([
                i,
                balanced_yards, balanced_time,
                run_yards, run_time,
                pass_yards, pass_time
            ])

    print(f"Drive outcome CSV saved to: {output_file}")

if __name__ == "__main__":
    generate_drive_csv()
    print("\nCSV file generated with all drive outcomes for quick reference.")
