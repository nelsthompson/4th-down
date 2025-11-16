# Gridiron Dice Football

A fast-paced, dice-driven football simulation game for 2 players or AI simulation. Play face-to-face with physical dice or run thousands of simulated games to analyze strategies.

## Overview

Gridiron Dice Football uses simple dice rolls and lookup tables to create realistic football games with:

- **Three offensive styles**: Balanced, Run-First, and Pass-First (each with different risk/reward)
- **Complete scoring**: Touchdowns (6 pts) + extra points (1pt or 2pt), field goals (3 pts), safeties (2 pts)
- **Realistic mechanics**: Turnovers, 4th down conversions, time management, field position strategy
- **Strategic depth**: 10-yard first downs, untimed down at end of half, distance-based field goals
- **AI coaching**: Dynamic play-calling based on score, time, and field position

## Game Modes

### Human vs Human (Physical Dice)

Play face-to-face using physical dice:
- **2 d20** (twenty-sided dice, 1-20)
- **1 d10** (ten-sided die, 1-10)
- **1 d8** (eight-sided die, 1-8)

See **[RULEBOOK.md](RULEBOOK.md)** for complete rules and **[GAME_CHARTS.md](GAME_CHARTS.md)** for quick reference tables.

### Computer Simulation

Run single games or batch simulations using Python:

```bash
python gridiron_dice.py
```

## Quick Start (Human Play)

1. Print **GAME_CHARTS.md** for easy reference
2. Flip a coin to determine who receives the opening kickoff
3. Each half starts with the receiving team at their **30-yard line**
4. On each drive:
   - Choose a play style (Balanced, Run-First, or Pass-First)
   - Roll d20 for drive outcome → get yards and time
   - Roll d20 for turnover check
   - Resolve outcome (TD, safety, or 4th down decision)
5. Game has two 30-minute halves (180 time blocks each)

## Key Mechanics

### Play Styles

Each style uses different dice for 4th down distance and has different turnover rates:

| Style | Turnover Risk | Characteristics | 4th Down Distance |
|-------|---------------|-----------------|-------------------|
| **Run-First** | 5% (roll 1) | Lower yardage, higher time consumption, safest | d8 (1-8 yards) |
| **Balanced** | 10% (rolls 1-2) | Moderate yardage and time, balanced approach | d10 (1-10 yards) |
| **Pass-First** | 20% (rolls 1-4) | Highest yardage, lowest time, riskiest | d20 (1-20 yards) |

### Scoring

- **Touchdown**: 6 points
  - **1-point conversion**: Use field goal table, success if make distance ≥ 15 yards (~85% success)
  - **2-point conversion**: Roll d10, success on 7+ (40% success)
- **Field Goal**: 3 points (roll d20 for make distance, compare to actual distance)
- **Safety**: 2 points to defense (when offense is tackled at/behind their own goal line)

### First Downs & 4th Down

- **10 yards for a first down**: If drive gains < 10 yards, 4th down distance = 10 - yards gained
  - Example: Gain 3 yards → 4th and 7
  - Example: Lose 5 yards → 4th and 15
- **If drive gains ≥ 10 yards**: Roll for distance based on style (d8/d10/d20)
- **4th down options**: Go for it, kick field goal (if within 50 yards), or punt (40 yards)
- **Conversions**: Roll d20 on conversion table, gain first down if yards ≥ yards needed

### Field Goals

- **Range**: Within 50 yards of goal line
- **Roll d20** for make distance (0-45 yards based on roll)
- **Success**: If make distance ≥ actual distance to goal
- **Miss**: Opponent gets ball 7 yards back (minimum at their 20-yard line)

### Special Rules

- **Turnovers**: Checked before scoring; on would-be TD, opponent gets ball at their 20
- **Safeties**: When offense is pushed to/past their own goal line
- **Untimed Down**: At end of half, offense can choose to let half end, attempt FG, or go for it
- **Time Capping**: TD plays use capped time based on yards needed to score

## Installation & Usage

### Requirements

Python 3.7+ (uses standard library only)

### Basic Simulation

```python
from gridiron_dice import simulate_game

# Run a single game
game = simulate_game()
print(f"FINAL: Bombers {game.score['Bombers']} - Gunners {game.score['Gunners']}")

# View drive-by-drive results
for drive in game.drives:
    print(f"H{drive.half} | {drive.team:8s} | {drive.style:8s} | {drive.result}")
```

### Batch Analysis

```python
from gridiron_dice import simulate_many

# Simulate 200 games
stats = simulate_many(200)
print(stats)
# Output: {'Bombers': 93, 'Gunners': 102, 'ties': 5, 'avg_pts': 46.4}
```

### Reproducible Results

```python
# Use a seed for consistent results
game = simulate_game(seed=42)
```

## Analysis Tools

The project includes several analysis scripts:

- **analyze_drive_types.py**: Compare average points per drive by play style
- **analyze_drives_per_game.py**: Distribution of possessions per game
- **analyze_4th_down_frequency.py**: 4th down attempt rates and success by style
- **analyze_fg_distances.py**: Field goal attempt distances and success rates
- **test_4th_down_distance.py**: Test suite for 10-yard first down rule

```bash
# Run drive analysis
python analyze_drive_types.py

# Sample output:
# BALANCED OFFENSE:
#   Average Points/Drive:      1.825
#   Touchdowns:                21.4%
#   Field Goals:               22.8%
#   Average Opponent Start:    69.2 yards
```

## Game Statistics

Based on 10,000 drive simulations from the 30-yard line:

| Metric | Balanced | Run-First | Pass-First |
|--------|----------|-----------|------------|
| **Avg Points/Drive** | 1.825 | 1.041 | 2.072 |
| **TD %** | 21.4% | 10.3% | 25.6% |
| **Turnover %** | 10.0% | 5.0% | 20.0% |
| **4th Down Attempts** | 13.7% | 16.3% | 8.1% |
| **FG Attempts** | 23.2% | 27.1% | 20.1% |

**Typical Game**: ~27 total drives (13-14 per team), avg score 23-24 points per team

## Project Structure

```
4th_down/
├── gridiron_dice.py              # Main simulation engine
├── RULEBOOK.md                   # Complete rules for human play
├── GAME_CHARTS.md                # Quick reference tables
├── drive_outcomes_draft.csv      # Drive outcome tables (editable)
├── analyze_drive_types.py        # Drive analysis tool
├── analyze_drives_per_game.py    # Game possession analysis
├── analyze_4th_down_frequency.py # 4th down statistics
├── analyze_fg_distances.py       # Field goal analysis
├── test_4th_down_distance.py     # Test suite
└── README.md                     # This file
```

## Configuration

Edit constants in `gridiron_dice.py`:

```python
BLOCKS_PER_HALF = 180  # Time blocks per half (30 game minutes)
PUNT_YARDS = 40        # Average punt distance

# Turnover thresholds (d20 rolls that cause turnovers)
TURNOVER_THRESHOLDS = {
    "run": [1],           # 5%
    "balanced": [1, 2],   # 10%
    "pass": [1, 2, 3, 4], # 20%
}
```

## Example Game Output

```
FINAL: Bombers 34 - Gunners 28

H1 | Bombers  | pass     | roll=19 | start= 30 -> end=100 | yds= 70 | t=17 | TD+1pt               | pts=7
H1 | Gunners  | balanced | roll= 5 | start= 70 -> end= 24 | yds=  6 | t= 7 | Punt                 | pts=0
H1 | Bombers  | balanced | roll=13 | start= 24 -> end= 69 | yds= 38 | t=26 | 4th down conversion (2) | pts=0
H1 | Bombers  | balanced | roll= 1 | start= 69 -> end= 52 | yds=-10 | t= 4 | FG Miss (spot set)   | pts=0
H1 | Gunners  | run      | roll=16 | start= 52 -> end=  0 | yds= 38 | t=35 | 4th down TD+1pt (3)  | pts=7
...
```

## Field Position System

The game uses absolute coordinates (0-100):
- **0** = Bombers' goal line (Bombers advance toward 100)
- **100** = Gunners' goal line (Gunners advance toward 0)
- **30** = Standard kickoff position for receiving team
- **20** = Touchback position on punts/missed FGs

## Strategy Tips

### For Human Players

- **Run-First**: Best when protecting a lead late in the game (burns clock, low turnovers)
- **Balanced**: Safe all-around choice, good for most situations
- **Pass-First**: Use when trailing (high scoring, saves time, but risky)
- **4th Down**: Consider going for it on 4th and 3 or less, especially near the goal
- **Extra Points**: Go for 2 when down by 7 late in game (2pt takes the lead, 1pt only ties)
- **End of Half**: Attempt FGs from under 35 yards, consider going for it when trailing

### AI Coaching Logic

The AI adjusts strategy based on:
- **Score differential**: More aggressive when trailing
- **Time remaining**: Clock management in final minutes
- **Field position**: More aggressive in opponent's territory
- **Half**: More conservative in first half, aggressive in second half when behind

## Development History

- **v0.1**: Initial drive mechanics with basic tables
- **v0.2**: Added field goals and punts
- **v0.3**: Implemented turnovers (5%, 10%, 20% by style)
- **v0.4**: 4th down conversions with first down continuation
- **v0.5**: Distance-based field goals, TD + extra point system
- **v0.6**: 1-indexed dice, safety scoring, untimed down rule
- **v0.7**: Turnover-before-TD logic, 10-yard first down rule

## Contributing

Contributions welcome! Areas for enhancement:

- Defensive ratings and team customization
- Special teams plays (kickoff returns, blocked kicks)
- Overtime rules
- Web interface for interactive play
- Additional analysis and visualization tools
- Weather/field conditions

## License

MIT License - free to use and modify for your projects.

## Credits

Game design and development: Synthia + You
Generated with assistance from Claude Code (Anthropic)

---

**Ready to play?** See [RULEBOOK.md](RULEBOOK.md) to get started!
