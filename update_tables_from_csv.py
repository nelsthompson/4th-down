#!/usr/bin/env python3
"""
Update drive outcome tables in gridiron_dice.py from CSV file
"""

import csv

def read_csv_tables(csv_file):
    """Read drive outcome tables from CSV file"""
    balanced = []
    run_first = []
    pass_first = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse each style's values
            bal_yards = row['Balanced Yards']
            bal_time = row['Balanced Time']
            run_yards = row['Run-First Yards']
            run_time = row['Run-First Time']
            pass_yards = row['Pass-First Yards']
            pass_time = row['Pass-First Time']

            # Convert to tuples, keeping "TD" and "1-20" as strings
            balanced.append((bal_yards if bal_yards == 'TD' else int(bal_yards),
                           bal_time if bal_time == '1-20' else int(bal_time)))
            run_first.append((run_yards if run_yards == 'TD' else int(run_yards),
                            run_time if run_time == '1-20' else int(run_time)))
            pass_first.append((pass_yards if pass_yards == 'TD' else int(pass_yards),
                             pass_time if pass_time == '1-20' else int(pass_time)))

    return balanced, run_first, pass_first

def format_table(name, table):
    """Format a table as Python code"""
    lines = [f"{name} = ["]

    # Group entries into rows of 8 for readability
    entries = []
    for yards, time in table:
        yards_str = f'"{yards}"' if yards == "TD" else str(yards)
        time_str = f'"{time}"' if time == "1-20" else str(time)
        entries.append(f"({yards_str},{time_str})")

    # Format in rows
    for i in range(0, len(entries), 8):
        chunk = entries[i:i+8]
        lines.append("    " + ",".join(chunk) + ",")

    lines.append("]")
    return "\n".join(lines)

def update_gridiron_dice(csv_file, python_file):
    """Update the drive outcome tables in gridiron_dice.py"""

    # Read the CSV data
    balanced, run_first, pass_first = read_csv_tables(csv_file)

    # Read the current file
    with open(python_file, 'r') as f:
        content = f.read()

    # Generate the new table definitions
    new_tables = f"""BALANCED = [
    (0,4),(3,5),(5,6),(6,6),(7,7),(9,8),(12,9),(15,10),
    (18,11),(25,14),(32,17),(38,19),(45,22),(55,26),
    (68,31),(85,38),
    ("TD","1-20"),("TD","1-20"),("TD","1-20"),("TD","1-20"),
]

RUN_FIRST = [
    (0,9),(1,9),(2,9),(3,9),(4,9),(6,9),(8,10),(10,11),
    (12,12),(15,15),(18,18),(22,20),(26,23),(30,27),
    (34,32),(38,39),
    (42,21),(48,23),(55,26),("TD","1-20"),
]

PASS_FIRST = [
    (0,2),(5,3),(7,4),(9,4),(12,5),(15,6),(18,7),(22,8),
    (28,9),(35,12),(42,15),(50,17),(60,20),(70,24),
    (80,29),(95,36),
    ("TD","1-20"),("TD","1-20"),("TD","1-20"),("TD","1-20"),
]"""

    # Build new tables from CSV
    balanced_entries = []
    for yards, time in balanced:
        yards_str = f'"{yards}"' if yards == "TD" else str(yards)
        time_str = f'"{time}"' if time == "1-20" else str(time)
        balanced_entries.append(f"({yards_str},{time_str})")

    run_entries = []
    for yards, time in run_first:
        yards_str = f'"{yards}"' if yards == "TD" else str(yards)
        time_str = f'"{time}"' if time == "1-20" else str(time)
        run_entries.append(f"({yards_str},{time_str})")

    pass_entries = []
    for yards, time in pass_first:
        yards_str = f'"{yards}"' if yards == "TD" else str(yards)
        time_str = f'"{time}"' if time == "1-20" else str(time)
        pass_entries.append(f"({yards_str},{time_str})")

    # Format the tables with proper line breaks
    balanced_table = "BALANCED = [\n    " + ",".join(balanced_entries[:8]) + ",\n"
    balanced_table += "    " + ",".join(balanced_entries[8:16]) + ",\n"
    balanced_table += "    " + ",".join(balanced_entries[16:]) + ",\n]"

    run_table = "RUN_FIRST = [\n    " + ",".join(run_entries[:8]) + ",\n"
    run_table += "    " + ",".join(run_entries[8:16]) + ",\n"
    run_table += "    " + ",".join(run_entries[16:]) + ",\n]"

    pass_table = "PASS_FIRST = [\n    " + ",".join(pass_entries[:8]) + ",\n"
    pass_table += "    " + ",".join(pass_entries[8:16]) + ",\n"
    pass_table += "    " + ",".join(pass_entries[16:]) + ",\n]"

    new_tables = f"{balanced_table}\n\n{run_table}\n\n{pass_table}"

    # Find and replace the old tables
    import re

    # Pattern to match all three tables
    pattern = r'BALANCED = \[.*?\]\n\nRUN_FIRST = \[.*?\]\n\nPASS_FIRST = \[.*?\]'

    new_content = re.sub(pattern, new_tables, content, flags=re.DOTALL)

    # Write back
    with open(python_file, 'w') as f:
        f.write(new_content)

    print(f"Updated {python_file} with tables from {csv_file}")
    print(f"  Balanced: {len(balanced)} entries")
    print(f"  Run-First: {len(run_first)} entries")
    print(f"  Pass-First: {len(pass_first)} entries")

if __name__ == "__main__":
    update_gridiron_dice("drive_outcomes_draft.csv", "gridiron_dice.py")
    print("\nDrive outcome tables updated successfully!")
