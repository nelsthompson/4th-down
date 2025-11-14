# 4th Down - Gridiron Dice Football Simulator

A Python-based dice-driven football simulation game that models complete football games with realistic drive mechanics, play-calling strategies, and game situations.

## Overview

Gridiron Dice Football simulates complete football games between two teams (Bombers and Gunners) using dice rolls and lookup tables to determine drive outcomes. The game features:

- **Three play-calling styles**: Balanced, Run-First, and Pass-First
- **Dynamic AI coaching**: Teams adjust strategy based on score and time remaining
- **Realistic game mechanics**: Field goals, punts, touchdowns, and time management
- **Drive-by-drive simulation**: Each possession is resolved with yards gained and time consumed
- **Batch simulation**: Run multiple games to analyze statistics

## How It Works

The game divides each half into 180 time blocks (representing 30 minutes of game time). Each drive:

1. The offensive team chooses a play style (balanced, run, or pass)
2. A 20-sided die roll determines the outcome from the chosen table
3. The drive advances the ball and consumes time
4. Drives end in touchdowns, field goals (good or missed), or punts
5. Special late-game logic adjusts for remaining time

### Field Position System

The game uses an absolute coordinate system (0-100):
- 0 = Bombers' goal line
- 100 = Gunners' goal line
- Teams advance toward the opponent's goal
- Field goal range: within 35 yards of the end zone

## Installation

### Requirements

Python 3.7 or higher (uses standard library only)

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd 4th_down

# Run the simulator
python gridiron_dice.py
```

## Usage

### Simulate a Single Game

```python
from gridiron_dice import simulate_game

game = simulate_game()
print(f"FINAL: Bombers {game.score['Bombers']} - Gunners {game.score['Gunners']}")

# View drive-by-drive breakdown
for drive in game.drives:
    print(f"H{drive.half} | {drive.team} | {drive.result}")
```

### Simulate Multiple Games

```python
from gridiron_dice import simulate_many

stats = simulate_many(n=100)
print(stats)
# Output: {'Bombers': 45, 'Gunners': 52, 'ties': 3, 'avg_pts': 28.5}
```

### Reproducible Results

Set a seed for consistent results:

```python
game = simulate_game(seed=42)
```

## Configuration

Edit the constants at the top of `gridiron_dice.py`:

- `BLOCKS_PER_HALF`: Time blocks per half (default: 180)
- `PUNT_YARDS`: Average punt distance (default: 40)
- `FG_GOOD_ON`: Successful field goal rolls on 1d4 (default: {2, 3, 4})
- `SEED`: Random seed for reproducibility (default: None)

## Play Styles

Each style has different risk/reward profiles:

- **Balanced**: Moderate yards, moderate time
- **Run-First**: Consumes more time, steady gains, fewer TDs
- **Pass-First**: Less time, higher variance, more big plays

## Example Output

```
FINAL: Bombers 24 - Gunners 21
H1 | Bombers  | balanced | roll=12 | start= 30 -> end= 75 | yds= 45 | t=22 | FG Good              | pts=3
H1 | Gunners  | pass     | roll=16 | start= 70 -> end=  0 | yds= 70 | t=24 | TD                   | pts=7
...
```

## Future Enhancements

Potential areas for development:

- [ ] Add defensive ratings and team customization
- [ ] Implement turnovers (fumbles, interceptions)
- [ ] Add special teams plays (kickoff returns, blocked kicks)
- [ ] Create a command-line interface with team selection
- [ ] Add game logs and statistics tracking
- [ ] Build a web interface for interactive play
- [ ] Implement overtime rules
- [ ] Add weather conditions affecting play outcomes

## Contributing

Contributions welcome! Feel free to:

- Report bugs or suggest features via issues
- Submit pull requests with improvements
- Share interesting game simulations or statistics

## License

MIT License - feel free to use and modify for your projects.

## Credits

Original concept and implementation by Synthia + ChatGPT
Further development and maintenance by the community
