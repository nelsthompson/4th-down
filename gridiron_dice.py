# Gridiron Dice Football - full simulation (v0.6)
# Distance-based field goals + Turnovers + 4th Down Conversions
# Author: Synthia + You

import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

# -----------------------------
# Config
# -----------------------------
BLOCKS_PER_HALF = 180  # 30 minutes, 10 sec per block
PUNT_YARDS = 40
SEED = None  # set to an int for reproducible runs

# Field Goal Rules (distance-dependent on d6)
# Distance to opponent's goal -> Required roll
FG_RULES = {
    (0, 10): 2,    # 0-10 yards: 2+ on d6 (83.3%)
    (11, 20): 3,   # 11-20 yards: 3+ on d6 (66.7%)
    (21, 30): 4,   # 21-30 yards: 4+ on d6 (50%)
    (31, 40): 5,   # 31-40 yards: 5+ on d6 (33.3%)
    (41, 50): 6,   # 41-50 yards: 6 on d6 (16.7%)
}

# Turnover Rules (roll d20 for each drive)
# Style -> Turnover on these rolls
TURNOVER_THRESHOLDS = {
    "run": [0],           # 5% turnover rate
    "balanced": [0, 1],   # 10% turnover rate
    "pass": [0, 1, 2],    # 15% turnover rate
}

# 4th Down Rules
# Roll d10 (1-10) for yards to go
# If going for it, roll d10 again - succeed if roll > yards to go

# -----------------------------
# Drive tables
# Each entry is (yards, time_blocks) for rolls 0..19
# Yards can be "TD" and time may be "1-20" for TD results.
# These match the CSV you asked me to generate.
# -----------------------------
BALANCED = [
    (-10,4),(0,5),(3,6),(5,6),(6,7),(7,8),(9,9),(12,10),
    (15,11),(18,14),(25,17),(32,19),(38,22),(45,26),(55,31),(68,38),
    ("TD","1-20"),("TD","1-20"),("TD","1-20"),("TD","1-20"),
]

RUN_FIRST = [
    (-2,12),(0,12),(2,12),(3,12),(4,12),(6,12),(8,12),(10,15),
    (12,17),(15,18),(18,20),(22,22),(26,24),(30,27),(34,32),(38,35),
    (42,39),(60,40),(90,45),("TD","1-20"),
]

PASS_FIRST = [
    (-10,2),(-5,3),(0,4),(5,4),(8,5),(12,6),(15,7),(18,8),
    (22,9),(28,12),(35,15),(42,17),(50,20),(60,24),(70,29),(80,36),
    ("TD","1-20"),("TD","1-20"),("TD","1-20"),("TD","1-20"),
]

TABLES = {
    "balanced": BALANCED,
    "run": RUN_FIRST,
    "pass": PASS_FIRST,
}

STYLES = ("balanced", "run", "pass")

# -----------------------------
# Coordinate system:
# Absolute field coordinate 0..100:
# - 0 = Bombers' goal line
# - 100 = Gunners' goal line
# Offense advances TOWARD opponent's goal.
#   If team == "Bombers": advance +yards; yards_to_endzone = 100 - x
#   If team == "Gunners": advance -yards; yards_to_endzone = x - 0
# Kickoffs:
#   Bombers start @ 30  -> x=30
#   Gunners start @ 30 -> relative => x = 100-30 = 70
# -----------------------------

def kickoff_position(next_team: str) -> int:
    return 30 if next_team == "Bombers" else 70

def yards_to_endzone(team: str, x: int) -> int:
    return (100 - x) if team == "Bombers" else x

def advance(team: str, x: int, yards: int) -> int:
    if team == "Bombers":
        return min(100, x + yards)
    else:
        return max(0, x - yards)

def is_safety(team: str, x: int) -> bool:
    """Check if the field position results in a safety for the offense"""
    if team == "Bombers":
        return x < 0  # Bombers driven back past their own goal line
    else:
        return x > 100  # Gunners driven back past their own goal line

def within_fg_range(team: str, x: int) -> bool:
    return yards_to_endzone(team, x) <= 50

def attempt_field_goal(team: str, x: int) -> bool:
    """
    Attempt a field goal based on distance to opponent's goal.
    Returns True if successful, False if missed.
    """
    distance = yards_to_endzone(team, x)

    # Find the appropriate FG rule based on distance
    required_roll = None
    for (min_dist, max_dist), req_roll in FG_RULES.items():
        if min_dist <= distance <= max_dist:
            required_roll = req_roll
            break

    # If beyond 50 yards, can't attempt
    if required_roll is None:
        return False

    # Roll d6 and check if >= required roll
    roll = random.randint(1, 6)
    return roll >= required_roll

def check_turnover(style: str) -> bool:
    """
    Roll d20 to check for turnover based on play style.
    Returns True if turnover occurs.
    """
    turnover_roll = random.randint(0, 19)
    return turnover_roll in TURNOVER_THRESHOLDS[style]

def should_go_for_it(team: str, x: int, score: Dict[str, int], blocks_left: int, half: int, style: str) -> bool:
    """
    AI decision: should the team go for it on 4th down?
    Considers game situation, field position, and score.
    Uses style-dependent dice for 4th down distance.
    """
    opponent = "Gunners" if team == "Bombers" else "Bombers"
    lead = score[team] - score[opponent]
    distance_to_goal = yards_to_endzone(team, x)

    # Calculate yards to go based on play style
    # Run-first: d8 (1-8), Balanced: d10 (1-10), Pass-first: d20 (1-20)
    if style == "run":
        yards_to_go = random.randint(1, 8)
    elif style == "balanced":
        yards_to_go = random.randint(1, 10)
    else:  # pass
        yards_to_go = random.randint(1, 20)

    # If yards to go >= distance to goal, it's 4th and goal
    if yards_to_go >= distance_to_goal:
        yards_to_go = distance_to_goal
        fourth_and_goal = True
    else:
        fourth_and_goal = False

    # Base probability to go for it
    go_for_it_prob = 0.0

    # 4th and goal situations - more aggressive
    if fourth_and_goal:
        if distance_to_goal <= 3:
            go_for_it_prob = 0.60  # Very likely on 4th and goal from 3 or less
        elif distance_to_goal <= 5:
            go_for_it_prob = 0.40
        else:
            go_for_it_prob = 0.20
    else:
        # 4th and short
        if yards_to_go <= 3:
            go_for_it_prob = 0.30
        elif yards_to_go <= 5:
            go_for_it_prob = 0.15
        else:
            go_for_it_prob = 0.05

    # Adjust based on field position
    if distance_to_goal <= 20:  # In opponent's red zone
        go_for_it_prob += 0.15
    elif distance_to_goal <= 40:  # In opponent's territory
        go_for_it_prob += 0.05

    # Adjust based on game situation
    if half == 2:  # Second half
        if blocks_left <= 30:  # Last 5 minutes
            if lead < -3:  # Trailing by more than a field goal
                go_for_it_prob += 0.30
            elif lead < 0:  # Trailing
                go_for_it_prob += 0.15
            elif lead <= 7:  # Close game
                go_for_it_prob += 0.05

    # Random decision based on probability
    return random.random() < go_for_it_prob, yards_to_go, fourth_and_goal

def attempt_fourth_down(team: str, x: int, yards_to_go: int) -> tuple:
    """
    Attempt a 4th down conversion.
    Returns: (success: bool, yards_gained: int, is_td: bool)
    """
    # Impossible to convert if 11+ yards to go
    if yards_to_go >= 11:
        return False, 0, False, x

    # Roll d10 for attempt (1-10)
    attempt_roll = random.randint(1, 10)

    # Success if roll > yards to go
    success = attempt_roll > yards_to_go

    if success:
        yards_gained = attempt_roll
        # Check if it reaches the end zone
        new_x = advance(team, x, yards_gained)
        is_td = is_td_yardage(team, new_x)
        return True, yards_gained, is_td, new_x
    else:
        # Failed conversion - turnover on downs
        return False, 0, False, x

def punt_spot(offense: str, x: int) -> int:
    # Punt goes 40 toward opponent goal; touchback puts receiving team at their 20
    if offense == "Bombers":
        raw = x + PUNT_YARDS
        return 80 if raw >= 100 else raw
    else:
        raw = x - PUNT_YARDS
        return 20 if raw <= 0 else raw

def missed_fg_spot(offense: str, x: int) -> int:
    # After a missed FG, move ball back 7 yards from the attempt line
    # Then receiving team starts at that spot UNLESS it's inside their 20, then at their 20.
    if offense == "Bombers":
        new_spot = max(0, x - 7)  # move back toward Bombers' goal
        # Receiving = Gunners (own 20 is x=80)
        return 80 if new_spot > 80 else new_spot
    else:
        new_spot = min(100, x + 7)  # move back toward Gunners' goal
        # Receiving = Bombers (own 20 is x=20)
        return 20 if new_spot < 20 else new_spot

def time_for_required_yards(style: str, yards_needed: int) -> int:
    """
    For TD time-capping rule:
    Find the smallest non-TD row with yards >= yards_needed; return its time.
    If none, return the largest non-TD time for that style.
    """
    rows = TABLES[style]
    candidates = [t for (y,t) in rows if y != "TD"]
    # rows are in order of roll; pick the first where yards >= needed:
    for y, t in rows:
        if y == "TD":
            continue
        if y >= yards_needed:
            return t
    # if none large enough, use the last non-TD time:
    return candidates[-1]

def roll_time_for_td(style: str, yards_needed: int) -> int:
    # 1d20 time with cap by time_for_required_yards
    raw = random.randint(1, 20)
    cap = time_for_required_yards(style, yards_needed)
    return min(raw, cap)

def choose_style(team: str, lead: int, blocks_left_in_half: int) -> str:
    """
    A simple 'AI coach':
    - If trailing and <= 60 blocks (~10 min): more pass
    - If leading and <= 60 blocks: more run
    - Else: balanced bias
    """
    if blocks_left_in_half <= 60:
        if lead < 0:  # trailing
            weights = {"pass": 0.55, "balanced": 0.35, "run": 0.10}
        elif lead > 0:  # leading
            weights = {"run": 0.50, "balanced": 0.40, "pass": 0.10}
        else:  # tied late
            weights = {"pass": 0.40, "balanced": 0.45, "run": 0.15}
    else:
        weights = {"balanced": 0.5, "pass": 0.30, "run": 0.20}

    r = random.random()
    cum = 0
    for s, w in weights.items():
        cum += w
        if r <= cum:
            return s
    return "balanced"

@dataclass
class DriveLog:
    half: int
    team: str
    start_x: int
    style: str
    roll: int
    yards: int
    time_blocks: int
    end_x: int
    result: str
    points: int

@dataclass
class GameResult:
    drives: List[DriveLog] = field(default_factory=list)
    score: Dict[str, int] = field(default_factory=lambda: {"Bombers":0, "Gunners":0})

def play_drive(team: str, opponent: str, x: int, style: str, blocks_left: int, half: int, score) -> Tuple[DriveLog, int, Optional[str], int]:
    """
    Returns: (DriveLog, blocks_spent, next_possession_team, next_start_x)
    If next_possession_team is None, same team continues (shouldn't happen in this possession-based design).
    """
    # Roll 1d20 on the chosen table
    roll = random.randint(0, 19)
    y, t = TABLES[style][roll]

    # Roll for turnover
    turnover_occurred = check_turnover(style)

    # If TD row:
    if y == "TD":
        yards_needed = yards_to_endzone(team, x)
        time_spent = roll_time_for_td(style, yards_needed)
        # Late-half enforcement:
        if time_spent > blocks_left:
            # Step back: find largest row that leaves >=1 block
            adj_y, adj_t = largest_fitting_row(style, blocks_left)
            # Apply adjusted row:
            end_x = advance(team, x, adj_y)
            # Check for safety BEFORE checking turnover or TD
            if is_safety(team, end_x):
                # Safety: opponent gets 2 points and ball at their 30
                log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "Safety (late-half)", 0)
                score[opponent] += 2
                return log, blocks_left, opponent, kickoff_position(opponent)
            # Check: is adjusted yardage a TD? Our non-TD rows are numeric yards only.
            if is_td_yardage(team, end_x):
                # Check for turnover
                if turnover_occurred:
                    opponent_20 = 20 if opponent == "Bombers" else 80
                    log = DriveLog(half, team, x, style, roll, adj_y, adj_t, opponent_20, "Turnover (late-half, would be TD)", 0)
                    return log, blocks_left, opponent, kickoff_position(opponent)
                # TD and end half immediately
                log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "TD (late-half adj)", 7)
                score[team] += 7
                return log, blocks_left, opponent, kickoff_position(opponent)  # half ends by caller when it sees 0 left
            # Not TD; check for turnover first
            if turnover_occurred:
                log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "Turnover (late-half)", 0)
                return log, blocks_left, opponent, kickoff_position(opponent)
            # if FG range, allow FG attempt as the final action:
            if within_fg_range(team, end_x):
                fg_good = attempt_field_goal(team, end_x)
                if fg_good:
                    log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "FG Good (late-half)", 3)
                    score[team] += 3
                else:
                    # Missed FG late-half: move back 7, clamp at receiving 20
                    miss_spot = missed_fg_spot(team, end_x)
                    log = DriveLog(half, team, x, style, roll, adj_y, adj_t, miss_spot, "FG Miss (late-half, spot set)", 0)
                return log, blocks_left, opponent, kickoff_position(opponent)  # half ends
            # Otherwise half ends with no score:
            log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "Half Ends (adj)", 0)
            return log, blocks_left, opponent, kickoff_position(opponent)

        # TD fits in time:
        end_x = 100 if team == "Bombers" else 0
        yards_gained = yards_to_endzone(team, x)

        # Check for turnover
        if turnover_occurred:
            # Turnover on TD: opponent gets ball at their 20
            opponent_20 = 20 if opponent == "Bombers" else 80
            log = DriveLog(half, team, x, style, roll, yards_gained, time_spent, opponent_20, "Turnover (would be TD)", 0)
            return log, time_spent, opponent, opponent_20

        log = DriveLog(half, team, x, style, roll, yards_gained, time_spent, end_x, "TD", 7)
        score[team] += 7
        return log, time_spent, opponent, kickoff_position(opponent)

    # Non-TD row
    time_spent = t
    yards = y

    # Late-half enforcement if it would overflow:
    if time_spent > blocks_left:
        # Use largest row that leaves >=1 block
        adj_y, adj_t = largest_fitting_row(style, blocks_left)
        end_x = advance(team, x, adj_y)
        # Check for safety BEFORE checking turnover or TD
        if is_safety(team, end_x):
            # Safety: opponent gets 2 points and ball at their 30
            log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "Safety (late-half)", 0)
            score[opponent] += 2
            return log, blocks_left, opponent, kickoff_position(opponent)
        # If adjusted row reaches TD:
        if is_td_yardage(team, end_x):
            # Check for turnover
            if turnover_occurred:
                opponent_20 = 20 if opponent == "Bombers" else 80
                log = DriveLog(half, team, x, style, roll, adj_y, adj_t, opponent_20, "Turnover (late-half, would be TD)", 0)
                return log, blocks_left, opponent, kickoff_position(opponent)
            log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "TD (late-half adj)", 7)
            score[team] += 7
            return log, blocks_left, opponent, kickoff_position(opponent)  # half ends
        # Check for turnover before FG/punt
        if turnover_occurred:
            log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "Turnover (late-half)", 0)
            return log, blocks_left, opponent, kickoff_position(opponent)
        # Else if FG range, allow final FG and end half:
        if within_fg_range(team, end_x):
            fg_good = attempt_field_goal(team, end_x)
            if fg_good:
                log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "FG Good (late-half)", 3)
                score[team] += 3
            else:
                # Missed FG late-half: move back 7, clamp at receiving 20
                miss_spot = missed_fg_spot(team, end_x)
                log = DriveLog(half, team, x, style, roll, adj_y, adj_t, miss_spot, "FG Miss (late-half, spot set)", 0)
            return log, blocks_left, opponent, kickoff_position(opponent)  # half ends
        # Otherwise half ends immediately:
        log = DriveLog(half, team, x, style, roll, adj_y, adj_t, end_x, "Half Ends (adj)", 0)
        return log, blocks_left, opponent, kickoff_position(opponent)

    # Fits in time -> resolve normally
    end_x = advance(team, x, yards)

    # Check for safety BEFORE checking turnover
    if is_safety(team, end_x):
        # Safety: opponent gets 2 points and ball at their 30
        log = DriveLog(half, team, x, style, roll, yards, time_spent, end_x, "Safety", 0)
        score[opponent] += 2
        return log, time_spent, opponent, kickoff_position(opponent)

    # If yardage reaches end zone by yardage (not TD row), apply TD-time cap rule:
    if is_td_yardage(team, end_x):
        # time cap by "required yards" row
        yards_needed = yards_to_endzone(team, x)
        td_time = roll_time_for_td(style, yards_needed)
        time_spent = min(time_spent, td_time)
        end_x_td = 100 if team == "Bombers" else 0

        # Check for turnover
        if turnover_occurred:
            # Turnover on TD: opponent gets ball at their 20
            opponent_20 = 20 if opponent == "Bombers" else 80
            log = DriveLog(half, team, x, style, roll, yards_needed, time_spent, opponent_20, "Turnover (would be TD)", 0)
            return log, time_spent, opponent, opponent_20

        log = DriveLog(half, team, x, style, roll, yards_needed, time_spent, end_x_td, "TD (by yardage)", 7)
        score[team] += 7
        return log, time_spent, opponent, kickoff_position(opponent)

    # No TD: decide FG, Punt, or 4th down attempt
    # Check for turnover first - turnovers prevent 4th down attempts
    if turnover_occurred:
        # Turnover: opponent gets ball at current spot
        log = DriveLog(half, team, x, style, roll, yards, time_spent, end_x, "Turnover", 0)
        return log, time_spent, opponent, end_x

    # 4th down decision (only if no turnover)
    go_for_it, yards_to_go, is_4th_and_goal = should_go_for_it(team, end_x, score, blocks_left, half, style)

    if go_for_it:
        # Attempt 4th down conversion
        success, yards_gained, is_td_conv, new_x = attempt_fourth_down(team, end_x, yards_to_go)

        if success:
            if is_td_conv:
                # Successful 4th down conversion for TD
                end_x_td = 100 if team == "Bombers" else 0
                result_str = f"4th down conversion TD ({'goal' if is_4th_and_goal else yards_to_go})"
                log = DriveLog(half, team, x, style, roll, yards, time_spent, end_x_td, result_str, 7)
                score[team] += 7
                return log, time_spent, opponent, kickoff_position(opponent)
            else:
                # Successful 4th down conversion, drive continues
                result_str = f"4th down conversion ({'goal' if is_4th_and_goal else yards_to_go})"
                log = DriveLog(half, team, x, style, roll, yards, time_spent, new_x, result_str, 0)
                # Same team keeps ball at new position for fresh drive
                return log, time_spent, team, new_x
        else:
            # Failed 4th down conversion - turnover on downs
            result_str = f"4th down failed ({'goal' if is_4th_and_goal else yards_to_go})"
            log = DriveLog(half, team, x, style, roll, yards, time_spent, end_x, result_str, 0)
            return log, time_spent, opponent, end_x

    # Not going for it - normal FG/Punt decision
    if within_fg_range(team, end_x):
        fg_good = attempt_field_goal(team, end_x)
        if fg_good:
            log = DriveLog(half, team, x, style, roll, yards, time_spent, end_x, "FG Good", 3)
            score[team] += 3
            return log, time_spent, opponent, kickoff_position(opponent)
        else:
            # missed FG: move back 7, clamp at receiving 20
            miss_spot = missed_fg_spot(team, end_x)
            log = DriveLog(half, team, x, style, roll, yards, time_spent, miss_spot, "FG Miss (spot set)", 0)
            return log, time_spent, opponent, miss_spot
    else:
        # Punt
        spot = punt_spot(team, end_x)
        log = DriveLog(half, team, x, style, roll, yards, time_spent, spot, "Punt", 0)
        return log, time_spent, opponent, spot

def largest_fitting_row(style: str, blocks_left: int) -> Tuple[int,int]:
    """
    Find the non-TD row with the largest time <= blocks_left-1 (leave >= 1 block).
    If none fit (e.g., blocks_left == 1), return (0,0).
    """
    limit = max(0, blocks_left - 1)
    best = (0, 0)
    for (y, t) in TABLES[style]:
        if y == "TD":
            continue
        if t <= limit and t >= best[1]:
            best = (y, t)
    return best

def is_td_yardage(team: str, x: int) -> bool:
    return (x >= 100) if team == "Bombers" else (x <= 0)

def simulate_half(start_team: str, start_x: int, score: Dict[str,int], half: int, rng_seed=None) -> Tuple[List[DriveLog], Dict[str,int], str, int]:
    drives = []
    team = start_team
    opponent = "Gunners" if team == "Bombers" else "Bombers"
    x = start_x
    blocks = BLOCKS_PER_HALF

    while blocks > 0:
        lead = score[team] - score[opponent]
        style = choose_style(team, lead, blocks)
        log, spent, next_team, next_x = play_drive(team, opponent, x, style, blocks, half, score)
        drives.append(log)

        # deduct time:
        # If late-half branch consumed "blocks_left" (we passed blocks_left in play_drive),
        # we ensure the half ends right after recording the drive:
        if log.result.startswith("TD (late-half") or log.result.startswith("FG Good (late-half)") or log.result.startswith("FG Miss (late-half") or log.result == "Half Ends (adj)":
            # end half immediately after applying the adjustment
            blocks = 0
            break
        else:
            blocks -= spent

        # possession flips:
        team = next_team
        opponent = "Gunners" if team == "Bombers" else "Bombers"
        x = next_x

    # Return next half's opening possession:
    # The team that kicked off to start the half will receive next half (handled by caller).
    return drives, score, team, x

def simulate_game(seed: Optional[int]=SEED) -> GameResult:
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    result = GameResult()

    # First half: Bombers receive at B30
    score = {"Bombers": 0, "Gunners": 0}
    h1_drives, score, _, _ = simulate_half("Bombers", 30, score, half=1)
    result.drives.extend(h1_drives)

    # Second half: Gunners receive at G30 => x=70
    h2_drives, score, _, _ = simulate_half("Gunners", 70, score, half=2)
    result.drives.extend(h2_drives)

    result.score = score
    return result

def simulate_many(n: int=100, seed: Optional[int]=SEED) -> Dict[str, float]:
    if seed is not None:
        random.seed(seed)
    totals = {"Bombers":0, "Gunners":0, "ties":0, "avg_pts":0.0}
    for _ in range(n):
        gr = simulate_game(seed=None)
        b, g = gr.score["Bombers"], gr.score["Gunners"]
        totals["avg_pts"] += (b + g)
        if b > g:
            totals["Bombers"] += 1
        elif g > b:
            totals["Gunners"] += 1
        else:
            totals["ties"] += 1
    totals["avg_pts"] /= n
    return totals

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Single game
    game = simulate_game()
    print(f"FINAL: Bombers {game.score['Bombers']} - Gunners {game.score['Gunners']}")
    for d in game.drives:
        print(f"H{d.half} | {d.team:8s} | {d.style:8s} | roll={d.roll:2d} | "
              f"start={d.start_x:3d} -> end={d.end_x:3d} | yds={d.yards:>3} | "
              f"t={d.time_blocks:2d} | {d.result:20s} | pts={d.points}")

    # Batch
    stats = simulate_many(200)
    print("\nBatch (200 games):", stats)
