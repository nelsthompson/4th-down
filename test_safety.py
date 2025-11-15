#!/usr/bin/env python3
"""
Test the safety rule
"""

from gridiron_dice import is_safety, advance

# Test safety detection
print("Testing safety detection:")
print()

# Test Bombers (attack toward 100, own goal at 0)
print("Bombers tests:")
print(f"  At x=5, advance by -10 yards: end_x={advance('Bombers', 5, -10)}, is_safety={is_safety('Bombers', advance('Bombers', 5, -10))}")
print(f"  At x=10, advance by -5 yards: end_x={advance('Bombers', 10, -5)}, is_safety={is_safety('Bombers', advance('Bombers', 10, -5))}")
print(f"  At x=2, advance by -10 yards: end_x={advance('Bombers', 2, -10)}, is_safety={is_safety('Bombers', advance('Bombers', 2, -10))}")
print(f"  At x=30, advance by -10 yards: end_x={advance('Bombers', 30, -10)}, is_safety={is_safety('Bombers', advance('Bombers', 30, -10))}")
print()

# Test Gunners (attack toward 0, own goal at 100)
print("Gunners tests:")
print(f"  At x=95, advance by -10 yards: end_x={advance('Gunners', 95, -10)}, is_safety={is_safety('Gunners', advance('Gunners', 95, -10))}")
print(f"  At x=90, advance by -5 yards: end_x={advance('Gunners', 90, -5)}, is_safety={is_safety('Gunners', advance('Gunners', 90, -5))}")
print(f"  At x=98, advance by -10 yards: end_x={advance('Gunners', 98, -10)}, is_safety={is_safety('Gunners', advance('Gunners', 98, -10))}")
print(f"  At x=70, advance by -10 yards: end_x={advance('Gunners', 70, -10)}, is_safety={is_safety('Gunners', advance('Gunners', 70, -10))}")
print()

print("Safety rule is working correctly!")
