# Forking Guide - Make Your Own Variant!

Want to create your own version of 4th Down with custom rules? Here's how!

## Prerequisites

- A GitHub account
- Claude Code access (https://claude.com/claude-code)
- A Discord account
- (Optional) Railway account for hosting

---

## Step 1: Fork the Repository

1. Go to https://github.com/nelsthompson/4th-down
2. Click the **Fork** button (top right)
3. This creates your own copy of the code

---

## Step 2: Clone Your Fork

Open your terminal and run:

```bash
# Replace YOUR-USERNAME with your GitHub username
git clone https://github.com/YOUR-USERNAME/4th-down.git
cd 4th-down
```

---

## Step 3: Explore the Code with Claude Code

1. **Open Claude Code** in the project directory
2. **Ask Claude to explain the code:**
   ```
   Read discord_bot.py and gridiron_dice.py and explain how the game works
   ```

3. **Understand the structure:**
   - `discord_bot.py` - Discord commands and game flow
   - `gridiron_dice.py` - Core game simulation and rules
   - `requirements.txt` - Python dependencies

---

## Step 4: Make Your Modifications

### Example Modifications You Could Make:

**Change to 4 Quarters Instead of 2 Halves:**
```
I want to change the game from 2 halves to 4 quarters.
Each quarter should be 15 game minutes (90 blocks).
```

**Add New Play Styles:**
```
Add a new "trick play" style with 15% turnover rate but bigger yard gains.
Update the help command and add a /trick command.
```

**Add Power-Ups:**
```
After each touchdown, give the scoring team a random power-up they can use
once (extra timeout, guaranteed conversion, etc.)
```

**Different Sport:**
```
Modify this to be a basketball dice game instead of football.
Keep the turn-based structure but change scoring and mechanics.
```

**Tournament Mode:**
```
Add a /tournament command that lets 4-8 players compete in a bracket.
Track wins/losses and declare a champion.
```

### Tips for Working with Claude:

- Start with: "Read the existing code first"
- Be specific about what you want to change
- Ask Claude to explain trade-offs before making changes
- Test incrementally - make one change at a time

---

## Step 5: Test Locally

Before deploying, test your changes:

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set your bot token (see DISCORD_SETUP.md for getting a token)
export DISCORD_BOT_TOKEN="your_token_here"

# Run the bot
python3 discord_bot.py
```

---

## Step 6: Deploy Your Variant

### Option A: Railway (Recommended)

Follow the Railway deployment steps in `DISCORD_SETUP.md` but use **your** repository instead.

### Option B: Keep It Local

Just run it on your computer when you want to play! No hosting needed.

---

## Step 7: Share Your Variant (Optional)

If you make something cool:

1. **Rename your bot** to distinguish it from the original
   - Example: "4th Down Extreme", "Gridiron Chaos", "Dice Football Pro"

2. **Update the README** with your changes
   ```bash
   # Edit README.md to describe your variant
   git add README.md
   git commit -m "Update README for my variant"
   git push
   ```

3. **Share the repo link** with friends so they can try it!

---

## Ideas for Variants

### Easy Modifications:
- Change time limits (shorter/longer games)
- Adjust turnover rates
- Modify field goal ranges
- Add weather effects (random modifiers)

### Medium Modifications:
- Add 4 quarters instead of 2 halves
- Special teams plays (onside kicks, fake punts)
- Player ratings/stats that persist across games
- Achievements and unlockables

### Advanced Modifications:
- Tournament brackets with multiple players
- League/season mode with standings
- Team builder (customize your team's strengths)
- Convert to a different sport entirely
- Add AI opponent for solo play

---

## Getting Help

If you get stuck:

1. **Ask Claude Code** - It can help debug errors and suggest fixes
2. **Check the original repo** - See if there are updates you can merge
3. **Discord community** - Share your variant and get feedback!

---

## Etiquette

- Give credit to the original game in your README
- Don't claim you wrote it from scratch
- Share your cool ideas back with the community!

---

## Example Claude Code Session

Here's how a typical modification session might go:

```
You: Read discord_bot.py and gridiron_dice.py

Claude: [Explains the code structure]

You: I want to add a "hail mary" command that can only be used once per
half. It's a risky play with 50% turnover but guaranteed TD if successful.

Claude: [Implements the feature, updates game state tracking, adds command]

You: Test it by showing me what happens if I use /hailmary

Claude: [Walks through the logic]

You: Great! Now update the /help command to mention this new feature.

Claude: [Updates help text]
```

---

## Have Fun!

The best part about having access to the code is making it your own.
Experiment, break things, and see what cool variants you can create!

🏈 Happy coding!
