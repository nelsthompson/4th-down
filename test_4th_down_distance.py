#!/usr/bin/env python3
"""
Test the 4th down distance rule
"""

import random
from gridiron_dice import should_go_for_it

random.seed(42)

# Test cases
score = {"Bombers": 0, "Gunners": 0}
team = "Bombers"
x = 50
blocks_left = 100
half = 1

print("Testing 4th down distance calculation:")
print("=" * 70)
print()

# Test 1: Gain < 10 yards
print("Test 1: Drive gains 3 yards (should be 4th and 7)")
style = "balanced"
yards_gained = 3
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x, score, blocks_left, half, style, yards_gained)
expected = 10 - yards_gained
print(f"  Yards gained: {yards_gained}")
print(f"  Expected yards to go: {expected}")
print(f"  Actual yards to go: {yards_to_go}")
print(f"  Result: {'PASS' if yards_to_go == expected else 'FAIL'}")
print()

# Test 2: Gain exactly 10 yards
print("Test 2: Drive gains 10 yards (should roll normally)")
yards_gained = 10
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x, score, blocks_left, half, style, yards_gained)
print(f"  Yards gained: {yards_gained}")
print(f"  Yards to go: {yards_to_go} (rolled from d10)")
print(f"  Result: {'PASS' if 1 <= yards_to_go <= 10 else 'FAIL'}")
print()

# Test 3: Gain > 10 yards
print("Test 3: Drive gains 25 yards (should roll normally)")
yards_gained = 25
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x, score, blocks_left, half, style, yards_gained)
print(f"  Yards gained: {yards_gained}")
print(f"  Yards to go: {yards_to_go} (rolled from d10)")
print(f"  Result: {'PASS' if 1 <= yards_to_go <= 10 else 'FAIL'}")
print()

# Test 4: Negative yardage
print("Test 4: Drive loses 10 yards (should be 4th and 20)")
yards_gained = -10
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x, score, blocks_left, half, style, yards_gained)
expected = 10 - yards_gained
print(f"  Yards gained: {yards_gained}")
print(f"  Expected yards to go: {expected}")
print(f"  Actual yards to go: {yards_to_go}")
print(f"  Result: {'PASS' if yards_to_go == expected else 'FAIL'}")
print()

# Test 5: Short gain near goal line (4th and 5, NOT goal)
print("Test 5: Drive gains 5 yards, 8 yards from goal (should be 4th and 5)")
yards_gained = 5
x_near_goal = 92  # 8 yards from goal
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x_near_goal, score, blocks_left, half, style, yards_gained)
expected = 10 - yards_gained  # Should be 5 (need 5 more for first down)
print(f"  Yards gained: {yards_gained}")
print(f"  Distance to goal: 8 yards")
print(f"  Yards to go: {yards_to_go}")
print(f"  Is 4th and goal: {is_4th_and_goal}")
print(f"  Result: {'PASS' if not is_4th_and_goal and yards_to_go == 5 else 'FAIL'}")
print()

# Test 5b: Short gain VERY near goal line (4th and goal)
print("Test 5b: Drive gains 5 yards, 3 yards from goal (should be 4th and goal)")
yards_gained = 5
x_very_near_goal = 97  # 3 yards from goal
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x_very_near_goal, score, blocks_left, half, style, yards_gained)
expected_ytg = 10 - yards_gained  # Would be 5, but capped at 3 (distance to goal)
print(f"  Yards gained: {yards_gained}")
print(f"  Distance to goal: 3 yards")
print(f"  Yards to go: {yards_to_go}")
print(f"  Is 4th and goal: {is_4th_and_goal}")
print(f"  Result: {'PASS' if is_4th_and_goal and yards_to_go == 3 else 'FAIL'}")
print()

# Test 6: Different styles
print("Test 6: Run-first with 15 yard gain (should roll d8)")
style = "run"
yards_gained = 15
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x, score, blocks_left, half, style, yards_gained)
print(f"  Style: {style}")
print(f"  Yards gained: {yards_gained}")
print(f"  Yards to go: {yards_to_go} (rolled from d8)")
print(f"  Result: {'PASS' if 1 <= yards_to_go <= 8 else 'FAIL'}")
print()

print("Test 7: Pass-first with 20 yard gain (should roll d20)")
style = "pass"
yards_gained = 20
go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, x, score, blocks_left, half, style, yards_gained)
print(f"  Style: {style}")
print(f"  Yards gained: {yards_gained}")
print(f"  Yards to go: {yards_to_go} (rolled from d20)")
print(f"  Result: {'PASS' if 1 <= yards_to_go <= 20 else 'FAIL'}")
print()
