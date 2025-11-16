#!/usr/bin/env python3
"""
4th Down! A Dice Football Game - Discord Bot
Play turn-based football games with slash commands
"""

import os
import discord
from discord import app_commands
from discord.ext import commands
import random
from typing import Dict, Optional
from gridiron_dice import (
    simulate_half, kickoff_position, choose_style,
    yards_to_endzone, within_fg_range, attempt_field_goal,
    should_go_for_it, attempt_fourth_down, attempt_extra_point,
    BLOCKS_PER_HALF
)

# Bot setup
intents = discord.Intents.default()
intents.guilds = True  # Required to see servers
intents.message_content = True
intents.members = True  # Required to look up members by name
bot = commands.Bot(command_prefix="!", intents=intents)

# Game state storage: channel_id -> game_state
games: Dict[int, dict] = {}


class GameState:
    """Manages the state of an ongoing game"""

    def __init__(self, channel_id: int, player1: discord.Member, player2: discord.Member):
        self.channel_id = channel_id

        # Randomly assign teams
        if random.random() < 0.5:
            self.bombers_player = player1
            self.gunners_player = player2
        else:
            self.bombers_player = player2
            self.gunners_player = player1

        # Game state
        self.score = {"Bombers": 0, "Gunners": 0}
        self.half = 1
        self.blocks_left = BLOCKS_PER_HALF
        self.possession = "Bombers"  # Who has the ball
        self.field_position = 30  # Current yard line
        self.drive_start_blocks = BLOCKS_PER_HALF  # Track when current drive started

        # Stats tracking
        self.stats = {
            "Bombers": {
                "yards": 0,
                "possessions": 1,  # Start with 1 for opening possession
                "time_of_possession": 0,
                "fgs_made": 0,
                "fgs_missed": 0,
                "punts": 0,
                "turnovers": 0
            },
            "Gunners": {
                "yards": 0,
                "possessions": 0,
                "time_of_possession": 0,
                "fgs_made": 0,
                "fgs_missed": 0,
                "punts": 0,
                "turnovers": 0
            }
        }

        # Turn state
        self.awaiting_action = "play_style"  # play_style, 4th_down, extra_point
        self.last_drive_result = None
        self.yards_to_go = None
        self.is_4th_and_goal = False
        self.yards_gained_on_drive = None

    def current_player(self) -> discord.Member:
        """Get the player whose turn it is"""
        return self.bombers_player if self.possession == "Bombers" else self.gunners_player

    def opponent_player(self) -> discord.Member:
        """Get the opponent player"""
        return self.gunners_player if self.possession == "Bombers" else self.bombers_player

    def current_player_with_team(self) -> str:
        """Get formatted string with player and their team"""
        return f"{self.current_player().mention} ({self.possession})"

    def switch_possession(self, new_team: str, new_position: int):
        """Switch possession to the other team"""
        self.possession = new_team
        self.field_position = new_position
        self.drive_start_blocks = self.blocks_left  # Record start of new drive
        self.stats[new_team]["possessions"] += 1  # Track new possession
        self.awaiting_action = "play_style"
        self.last_drive_result = None
        self.yards_to_go = None
        self.is_4th_and_goal = False
        self.yards_gained_on_drive = None

    def format_score(self) -> str:
        """Format current score with team names"""
        return f"**Bombers {self.score['Bombers']} - {self.score['Gunners']} Gunners**"

    def format_time(self) -> str:
        """Format time remaining"""
        minutes = self.blocks_left // 6
        seconds = (self.blocks_left % 6) * 10
        half_str = "1st Half" if self.half == 1 else "2nd Half"
        return f"{half_str} - {minutes}:{seconds:02d} remaining"

    def format_drive_elapsed(self) -> str:
        """Format elapsed time on current drive"""
        elapsed_blocks = self.drive_start_blocks - self.blocks_left
        minutes = elapsed_blocks // 6
        seconds = (elapsed_blocks % 6) * 10
        return f"{minutes}:{seconds:02d}"

    def format_stats(self) -> discord.Embed:
        """Format game statistics as an embed"""
        embed = discord.Embed(
            title="📊 Game Statistics",
            color=discord.Color.purple()
        )

        bombers_stats = self.stats["Bombers"]
        gunners_stats = self.stats["Gunners"]

        # Format time of possession
        b_top_min = bombers_stats["time_of_possession"] // 6
        b_top_sec = (bombers_stats["time_of_possession"] % 6) * 10
        g_top_min = gunners_stats["time_of_possession"] // 6
        g_top_sec = (gunners_stats["time_of_possession"] % 6) * 10

        # Create stats table
        stats_text = (
            f"```\n"
            f"{'Stat':<20} {'Bombers':>10} {'Gunners':>10}\n"
            f"{'-'*42}\n"
            f"{'Total Yards':<20} {bombers_stats['yards']:>10} {gunners_stats['yards']:>10}\n"
            f"{'Possessions':<20} {bombers_stats['possessions']:>10} {gunners_stats['possessions']:>10}\n"
            f"{'Time of Poss.':<20} {b_top_min:>9}:{b_top_sec:02d} {g_top_min:>9}:{g_top_sec:02d}\n"
            f"{'FGs Made':<20} {bombers_stats['fgs_made']:>10} {gunners_stats['fgs_made']:>10}\n"
            f"{'FGs Missed':<20} {bombers_stats['fgs_missed']:>10} {gunners_stats['fgs_missed']:>10}\n"
            f"{'Punts':<20} {bombers_stats['punts']:>10} {gunners_stats['punts']:>10}\n"
            f"{'Turnovers':<20} {bombers_stats['turnovers']:>10} {gunners_stats['turnovers']:>10}\n"
            f"```"
        )

        embed.description = stats_text
        embed.add_field(name="Score", value=self.format_score(), inline=False)

        return embed


def get_game(channel_id: int) -> Optional[GameState]:
    """Get game state for a channel"""
    return games.get(channel_id)


def relative_position(possession: str, field_position: int) -> str:
    """Convert absolute field position to relative position (+/- from team's perspective)

    Negative = in own territory (yards from own goal line)
    Positive = in opponent territory (yards from opponent's goal line)
    """
    if field_position == 50:
        return "Midfield"

    if possession == "Bombers":
        # Bombers go from 0 (their goal) to 100 (opponent's goal)
        if field_position < 50:
            # Own territory - show as negative (yards from own goal)
            return f"-{field_position}"
        else:
            # Opponent territory - show as positive (yards from opponent's goal)
            return f"+{100 - field_position}"
    else:  # Gunners
        # Gunners go from 100 (their goal) to 0 (opponent's goal)
        if field_position > 50:
            # Own territory - show as negative (yards from own goal)
            return f"-{100 - field_position}"
        else:
            # Opponent territory - show as positive (yards from opponent's goal)
            return f"+{field_position}"


def format_field_position(game: GameState) -> str:
    """Create a visual field position indicator"""
    pos = game.field_position
    rel_pos = relative_position(game.possession, pos)

    # Create a simple field diagram
    if game.possession == "Bombers":
        marker = "🏈→"
        goal_info = f"{100 - pos} yards to goal"
    else:
        marker = "←🏈"
        goal_info = f"{pos} yards to goal"

    return f"**Field Position:** {marker} {rel_pos} ({goal_info})"


@bot.event
async def on_ready():
    """Bot startup"""
    print(f'{bot.user} is now online!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.tree.command(name="newgame", description="Start a new game of 4th Down")
@app_commands.describe(opponent="The player you want to play against")
@app_commands.guild_only()  # Ensure this command only works in servers
async def newgame(interaction: discord.Interaction, opponent: discord.User):
    """Start a new game"""
    channel_id = interaction.channel_id

    # Check if game already exists
    if channel_id in games:
        await interaction.response.send_message(
            "⚠️ A game is already in progress in this channel! Finish it first.",
            ephemeral=True
        )
        return

    # Can't play against bots
    if opponent.bot:
        await interaction.response.send_message(
            "⚠️ You can't play against a bot!",
            ephemeral=True
        )
        return

    # Create new game - interaction.user is already a Member in guild context
    game = GameState(channel_id, interaction.user, opponent)
    games[channel_id] = game

    # Announce game start
    embed = discord.Embed(
        title="🏈 NEW GAME STARTED! 🏈",
        description=f"**{game.bombers_player.mention}** (Bombers) vs **{game.gunners_player.mention}** (Gunners)",
        color=discord.Color.green()
    )
    embed.add_field(name="Score", value=game.format_score(), inline=True)
    embed.add_field(name="Time", value=game.format_time(), inline=True)
    embed.add_field(
        name="Kickoff",
        value=f"{game.possession} receive at -30",
        inline=False
    )
    embed.add_field(
        name="First Possession",
        value=f"{game.current_player_with_team()}, choose your play style:\n`/balanced` | `/run` | `/pass`",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="balanced", description="Choose Balanced offense (10% turnover, moderate yards)")
async def balanced(interaction: discord.Interaction):
    """Choose balanced play style"""
    await handle_play_style(interaction, "balanced")


@bot.tree.command(name="run", description="Choose Run-First offense (5% turnover, grinds clock)")
async def run(interaction: discord.Interaction):
    """Choose run-first play style"""
    await handle_play_style(interaction, "run")


@bot.tree.command(name="pass", description="Choose Pass-First offense (20% turnover, big plays)")
async def pass_play(interaction: discord.Interaction):
    """Choose pass-first play style"""
    await handle_play_style(interaction, "pass")


async def handle_play_style(interaction: discord.Interaction, style: str):
    """Handle play style selection"""
    game = get_game(interaction.channel_id)

    if not game:
        await interaction.response.send_message(
            "⚠️ No game in progress. Start one with `/newgame`",
            ephemeral=True
        )
        return

    # Check if it's this player's turn
    if interaction.user.id != game.current_player().id:
        await interaction.response.send_message(
            f"⚠️ It's {game.current_player_with_team()}'s turn!",
            ephemeral=True
        )
        return

    # Check if we're awaiting play style
    if game.awaiting_action != "play_style":
        await interaction.response.send_message(
            f"⚠️ Not the right time for this command. Current action needed: {game.awaiting_action}",
            ephemeral=True
        )
        return

    # Execute the drive
    await execute_drive(interaction, game, style)


async def execute_drive(interaction: discord.Interaction, game: GameState, style: str):
    """Execute a drive with the chosen style"""
    from gridiron_dice import (
        TABLES, TURNOVER_THRESHOLDS, advance, is_safety, is_td_yardage,
        roll_time_for_td, time_for_required_yards, FIELD_GOAL_DISTANCE
    )

    # Roll for drive outcome
    roll = random.randint(1, 20)
    y, t = TABLES[style][roll - 1]

    # For TD rows, need to roll time to check if it expires
    if y == "TD":
        yards_needed = yards_to_endzone(game.possession, game.field_position)
        t = roll_time_for_td(style, yards_needed)

    # Check if time expires during this drive
    time_expired = False
    if game.blocks_left - t <= 0:
        # Find the minimum time row that still expires the clock
        time_expired = True
        min_time_row = None
        for yds, time in TABLES[style]:
            if yds != "TD" and game.blocks_left - time <= 0:
                if min_time_row is None or time < min_time_row[1]:
                    min_time_row = (yds, time)

        # If we found a valid row, use it; otherwise keep the rolled result
        if min_time_row:
            y, t = min_time_row

    # Roll for turnover (do the roll here so we can show the actual roll used)
    turnover_roll = random.randint(1, 20)
    turnover_occurred = turnover_roll in TURNOVER_THRESHOLDS[style]

    # Build response
    embed = discord.Embed(
        title=f"🎲 {style.upper()} OFFENSE",
        color=discord.Color.blue()
    )

    opponent = "Gunners" if game.possession == "Bombers" else "Bombers"

    # Handle TD row
    if y == "TD":
        # Time was already rolled earlier to check for expiration
        time_spent = t

        embed.add_field(name="Drive Roll", value=f"🎲 Rolled **{roll}** → TD!", inline=False)
        embed.add_field(name="Turnover Check", value=f"🎲 Rolled **{turnover_roll}**", inline=True)

        if turnover_occurred:
            # Turnover on would-be TD
            embed.add_field(name="Result", value="❌ **TURNOVER!**", inline=True)
            embed.add_field(
                name="Outcome",
                value=f"Would have been a TD, but turnover! {opponent} gets ball at -20.",
                inline=False
            )

            game.blocks_left -= time_spent
            game.stats[game.possession]["time_of_possession"] += time_spent
            game.stats[game.possession]["turnovers"] += 1
            opponent_20 = 20 if opponent == "Bombers" else 80
            game.switch_possession(opponent, opponent_20)

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Next",
                value=f"{game.current_player_with_team()}'s turn at -20.\nChoose: `/balanced` | `/run` | `/pass`",
                inline=False
            )
        else:
            # Touchdown!
            yards_gained = yards_to_endzone(game.possession, game.field_position)
            embed.add_field(name="Result", value="✅ Safe!", inline=True)
            embed.add_field(
                name="Outcome",
                value=f"🎉 **TOUCHDOWN!** {game.possession} +6",
                inline=False
            )

            game.score[game.possession] += 6
            game.blocks_left -= time_spent
            game.stats[game.possession]["yards"] += yards_gained
            game.stats[game.possession]["time_of_possession"] += time_spent
            game.awaiting_action = "extra_point"

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Extra Point",
                value=f"{game.current_player_with_team()}, choose conversion:\n`/1pt` (95% success) | `/2pt` (40% success)",
                inline=False
            )
    else:
        # Non-TD row
        time_spent = t
        yards = y

        embed.add_field(name="Drive Roll", value=f"🎲 Rolled **{roll}**", inline=True)
        embed.add_field(name="Result", value=f"**{yards:+d}** yards, **{time_spent}** time blocks", inline=True)

        # Calculate end position
        end_x = advance(game.possession, game.field_position, yards)

        # Check for safety
        if is_safety(game.possession, end_x):
            embed.add_field(name="Turnover Check", value=f"🎲 Rolled **{turnover_roll}**", inline=False)
            embed.add_field(name="Outcome", value=f"⚠️ **SAFETY!** {opponent} +2", inline=False)

            game.score[opponent] += 2
            game.blocks_left -= time_spent
            game.stats[game.possession]["yards"] += yards
            game.stats[game.possession]["time_of_possession"] += time_spent
            game.stats[game.possession]["turnovers"] += 1  # Safety counts as turnover
            game.switch_possession(opponent, kickoff_position(opponent))

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Next",
                value=f"{game.current_player_with_team()}'s turn at -30.\nChoose: `/balanced` | `/run` | `/pass`",
                inline=False
            )
        else:
            # Check for turnover
            embed.add_field(name="Turnover Check", value=f"🎲 Rolled **{turnover_roll}**", inline=True)

            if turnover_occurred:
                # Check if would have been TD
                if is_td_yardage(game.possession, end_x):
                    embed.add_field(name="Result", value="❌ **TURNOVER!**", inline=True)
                    embed.add_field(
                        name="Outcome",
                        value=f"Would have been a TD, but turnover! {opponent} gets ball at -20.",
                        inline=False
                    )

                    # For non-TD rows that reach endzone, use time from minimum yardage row
                    yards_needed = yards_to_endzone(game.possession, game.field_position)
                    time_spent = time_for_required_yards(style, yards_needed)

                    game.blocks_left -= time_spent
                    game.stats[game.possession]["yards"] += yards_needed
                    game.stats[game.possession]["time_of_possession"] += time_spent
                    game.stats[game.possession]["turnovers"] += 1
                    opponent_20 = 20 if opponent == "Bombers" else 80
                    game.switch_possession(opponent, opponent_20)
                else:
                    embed.add_field(name="Result", value="❌ **TURNOVER!**", inline=True)
                    embed.add_field(
                        name="Outcome",
                        value=f"{opponent} gets ball at {relative_position(opponent, end_x)}.",
                        inline=False
                    )

                    game.blocks_left -= time_spent
                    game.stats[game.possession]["yards"] += yards
                    game.stats[game.possession]["time_of_possession"] += time_spent
                    game.stats[game.possession]["turnovers"] += 1
                    game.switch_possession(opponent, end_x)

                embed.add_field(name="Score", value=game.format_score(), inline=True)
                embed.add_field(name="Time", value=game.format_time(), inline=True)
                embed.add_field(
                    name="Next",
                    value=f"{game.current_player_with_team()}'s turn.\nChoose: `/balanced` | `/run` | `/pass`",
                    inline=False
                )
            else:
                # No turnover - check for TD
                embed.add_field(name="Result", value="✅ Safe!", inline=True)

                if is_td_yardage(game.possession, end_x):
                    # TD by yardage - use time from minimum yardage row needed for TD
                    yards_needed = yards_to_endzone(game.possession, game.field_position)
                    time_spent = time_for_required_yards(style, yards_needed)

                    embed.add_field(
                        name="Outcome",
                        value=f"🎉 **TOUCHDOWN!** {game.possession} +6",
                        inline=False
                    )

                    game.score[game.possession] += 6
                    game.blocks_left -= time_spent
                    game.stats[game.possession]["yards"] += yards_needed
                    game.stats[game.possession]["time_of_possession"] += time_spent
                    game.field_position = end_x
                    game.awaiting_action = "extra_point"

                    embed.add_field(name="Score", value=game.format_score(), inline=True)
                    embed.add_field(name="Time", value=game.format_time(), inline=True)
                    embed.add_field(
                        name="Extra Point",
                        value=f"{game.current_player_with_team()}, choose conversion:\n`/1pt` (95% success) | `/2pt` (40% success)",
                        inline=False
                    )
                else:
                    # No TD - check if time expired
                    game.field_position = end_x
                    game.blocks_left -= time_spent
                    game.stats[game.possession]["yards"] += yards
                    game.stats[game.possession]["time_of_possession"] += time_spent
                    game.yards_gained_on_drive = yards

                    if time_expired and game.blocks_left <= 0:
                        # Time expired - final play scenario
                        game.blocks_left = 0
                        distance_to_goal = yards_to_endzone(game.possession, end_x)

                        # Calculate yards to go for the final play
                        if yards < 10:
                            ytg = 10 - yards
                        else:
                            if style == "run":
                                ytg = random.randint(1, 8)
                            elif style == "balanced":
                                ytg = random.randint(1, 10)
                            else:  # pass
                                ytg = random.randint(1, 20)

                        if ytg >= distance_to_goal:
                            ytg = distance_to_goal
                            game.is_4th_and_goal = True
                        else:
                            game.is_4th_and_goal = False

                        game.yards_to_go = ytg
                        game.awaiting_action = "final_play"

                        embed.add_field(
                            name="Field Position",
                            value=format_field_position(game),
                            inline=False
                        )
                        embed.add_field(name="Score", value=game.format_score(), inline=True)
                        embed.add_field(name="Time", value="⏰ **TIME EXPIRED - 1 Second Remaining**", inline=True)
                        embed.add_field(name="Drive Elapsed", value=game.format_drive_elapsed(), inline=True)

                        # Final play options: field goal or go for it (no punt)
                        options = []
                        if within_fg_range(game.possession, end_x):
                            options.append("`/fieldgoal`")
                        options.append("`/goforit`")

                        embed.add_field(
                            name="Final Play",
                            value=f"Time expired! One final play available.\n{game.current_player_with_team()}: {' | '.join(options)}",
                            inline=False
                        )
                    else:
                        # Normal 4th down situation
                        distance_to_goal = yards_to_endzone(game.possession, end_x)

                        if yards < 10:
                            ytg = 10 - yards
                        else:
                            if style == "run":
                                ytg = random.randint(1, 8)
                            elif style == "balanced":
                                ytg = random.randint(1, 10)
                            else:  # pass
                                ytg = random.randint(1, 20)

                        if ytg >= distance_to_goal:
                            ytg = distance_to_goal
                            game.is_4th_and_goal = True
                        else:
                            game.is_4th_and_goal = False

                        game.yards_to_go = ytg
                        game.awaiting_action = "4th_down"

                        embed.add_field(
                            name="Field Position",
                            value=format_field_position(game),
                            inline=False
                        )

                        situation = "goal" if game.is_4th_and_goal else f"{ytg}"
                        embed.add_field(
                            name="4th Down",
                            value=f"**4th and {situation}**",
                            inline=False
                        )

                        # Determine available options
                        options = ["`/goforit`"]
                        if within_fg_range(game.possession, end_x):
                            options.append("`/fieldgoal`")
                        options.append("`/punt`")

                        embed.add_field(name="Score", value=game.format_score(), inline=True)
                        embed.add_field(name="Time", value=game.format_time(), inline=True)
                        embed.add_field(name="Drive Elapsed", value=game.format_drive_elapsed(), inline=True)
                        embed.add_field(
                            name="Choose",
                            value=f"{game.current_player_with_team()}: {' | '.join(options)}",
                            inline=False
                        )

    await interaction.response.send_message(embed=embed)

    # Check for half/game end - but NOT if we're awaiting a final play
    if game.blocks_left <= 0 and game.awaiting_action != "final_play":
        await end_half(interaction.channel, game)


@bot.tree.command(name="goforit", description="Attempt to convert on 4th down")
async def goforit(interaction: discord.Interaction):
    """Go for it on 4th down"""
    await handle_fourth_down_decision(interaction, "goforit")


@bot.tree.command(name="fieldgoal", description="Attempt a field goal")
async def fieldgoal(interaction: discord.Interaction):
    """Attempt field goal"""
    await handle_fourth_down_decision(interaction, "fieldgoal")


@bot.tree.command(name="punt", description="Punt the ball away")
async def punt(interaction: discord.Interaction):
    """Punt"""
    await handle_fourth_down_decision(interaction, "punt")


async def handle_fourth_down_decision(interaction: discord.Interaction, decision: str):
    """Handle 4th down decision"""
    game = get_game(interaction.channel_id)

    if not game:
        await interaction.response.send_message("⚠️ No game in progress.", ephemeral=True)
        return

    if interaction.user.id != game.current_player().id:
        await interaction.response.send_message(
            f"⚠️ It's {game.current_player_with_team()}'s turn!",
            ephemeral=True
        )
        return

    if game.awaiting_action not in ["4th_down", "final_play"]:
        await interaction.response.send_message(
            f"⚠️ Not the right time for this command.",
            ephemeral=True
        )
        return

    is_final_play = (game.awaiting_action == "final_play")

    from gridiron_dice import punt_spot, missed_fg_spot, kickoff_position

    opponent = "Gunners" if game.possession == "Bombers" else "Bombers"
    embed = discord.Embed(title=f"🏈 4TH DOWN", color=discord.Color.orange())

    if decision == "goforit":
        # Attempt 4th down conversion - roll here so we can show the actual roll
        roll = random.randint(1, 20)
        from gridiron_dice import FOURTH_DOWN_CONVERSION

        success, yards_gained, is_td, new_x, is_first_down = attempt_fourth_down(
            game.possession, game.field_position, game.yards_to_go, roll
        )

        embed.add_field(name="Attempt", value=f"🎲 Rolled **{roll}** on conversion table", inline=False)
        embed.add_field(name="Result", value=f"**{yards_gained:+d}** yards gained", inline=False)

        if is_td:
            embed.add_field(name="Outcome", value=f"🎉 **TOUCHDOWN!** {game.possession} +6", inline=False)
            game.score[game.possession] += 6
            game.field_position = new_x
            game.awaiting_action = "extra_point"

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Extra Point",
                value=f"{game.current_player_with_team()}, choose:\n`/1pt` | `/2pt`",
                inline=False
            )
        elif is_first_down:
            embed.add_field(name="Outcome", value=f"✅ **FIRST DOWN!** {game.possession} keeps the ball", inline=False)
            game.field_position = new_x
            game.awaiting_action = "play_style"

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Field Position",
                value=format_field_position(game),
                inline=False
            )
            embed.add_field(
                name="Next",
                value=f"{game.current_player_with_team()}, choose:\n`/balanced` | `/run` | `/pass`",
                inline=False
            )
        else:
            embed.add_field(name="Outcome", value=f"❌ **TURNOVER ON DOWNS**", inline=False)
            embed.add_field(name="Result", value=f"{opponent} gets ball at {relative_position(opponent, new_x)}", inline=False)

            game.switch_possession(opponent, new_x)

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Next",
                value=f"{game.current_player_with_team()}'s turn.\n Choose: `/balanced` | `/run` | `/pass`",
                inline=False
            )

    elif decision == "fieldgoal":
        if not within_fg_range(game.possession, game.field_position):
            await interaction.response.send_message("⚠️ Not in field goal range!", ephemeral=True)
            return

        distance = yards_to_endzone(game.possession, game.field_position)

        # Roll for field goal attempt
        roll = random.randint(1, 20)
        from gridiron_dice import FIELD_GOAL_DISTANCE
        make_distance = FIELD_GOAL_DISTANCE[roll - 1]
        fg_good = make_distance >= distance

        embed.add_field(name="Attempt", value=f"FG from **{distance}** yards", inline=False)
        embed.add_field(name="Roll", value=f"🎲 Rolled **{roll}** → Make distance: **{make_distance}** yards", inline=False)

        if fg_good:
            embed.add_field(name="Result", value="✅ **FIELD GOAL GOOD!** +3", inline=False)
            game.score[game.possession] += 3
            game.stats[game.possession]["fgs_made"] += 1

            game.switch_possession(opponent, kickoff_position(opponent))

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Kickoff",
                value=f"{opponent} receives at -30.",
                inline=False
            )
            embed.add_field(
                name="Next",
                value=f"{game.current_player_with_team()}, choose:\n`/balanced` | `/run` | `/pass`",
                inline=False
            )
        else:
            miss_spot = missed_fg_spot(game.possession, game.field_position)
            embed.add_field(name="Result", value="❌ **FIELD GOAL MISS**", inline=False)
            embed.add_field(name="Ball Placement", value=f"{opponent} gets ball at {relative_position(opponent, miss_spot)}", inline=False)

            game.stats[game.possession]["fgs_missed"] += 1
            game.switch_possession(opponent, miss_spot)

            embed.add_field(name="Score", value=game.format_score(), inline=True)
            embed.add_field(name="Time", value=game.format_time(), inline=True)
            embed.add_field(
                name="Next",
                value=f"{game.current_player_with_team()}, choose:\n`/balanced` | `/run` | `/pass`",
                inline=False
            )

    else:  # punt
        if is_final_play:
            await interaction.response.send_message("⚠️ Cannot punt on final play of half!", ephemeral=True)
            return

        spot = punt_spot(game.possession, game.field_position)
        embed.add_field(name="Result", value="📤 **PUNT**", inline=False)
        embed.add_field(name="Ball Placement", value=f"{opponent} gets ball at {relative_position(opponent, spot)}", inline=False)

        game.stats[game.possession]["punts"] += 1
        game.switch_possession(opponent, spot)

        embed.add_field(name="Score", value=game.format_score(), inline=True)
        embed.add_field(name="Time", value=game.format_time(), inline=True)
        embed.add_field(
            name="Next",
            value=f"{game.current_player_with_team()}, choose:\n`/balanced` | `/run` | `/pass`",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

    # Check if this was the final play and end the half
    if is_final_play and game.blocks_left <= 0:
        await end_half(interaction.channel, game)


@bot.tree.command(name="1pt", description="Attempt 1-point conversion (95% success)")
async def one_point(interaction: discord.Interaction):
    """Attempt 1-point conversion"""
    await handle_extra_point(interaction, False)


@bot.tree.command(name="2pt", description="Attempt 2-point conversion (40% success)")
async def two_point(interaction: discord.Interaction):
    """Attempt 2-point conversion"""
    await handle_extra_point(interaction, True)


async def handle_extra_point(interaction: discord.Interaction, go_for_two: bool):
    """Handle extra point attempt"""
    game = get_game(interaction.channel_id)

    if not game:
        await interaction.response.send_message("⚠️ No game in progress.", ephemeral=True)
        return

    if interaction.user.id != game.current_player().id:
        await interaction.response.send_message(
            f"⚠️ It's {game.current_player_with_team()}'s turn!",
            ephemeral=True
        )
        return

    if game.awaiting_action != "extra_point":
        await interaction.response.send_message("⚠️ Not the right time for this command.", ephemeral=True)
        return

    opponent = "Gunners" if game.possession == "Bombers" else "Bombers"

    embed = discord.Embed(title="🏈 EXTRA POINT", color=discord.Color.gold())

    if go_for_two:
        # 2-point conversion
        roll = random.randint(1, 10)
        success = roll >= 7

        embed.add_field(name="Attempt", value="2-Point Conversion", inline=False)
        embed.add_field(name="Roll", value=f"🎲 Rolled **{roll}** on d10 (need 7+)", inline=False)

        if success:
            embed.add_field(name="Result", value="✅ **GOOD!** +2", inline=False)
            game.score[game.possession] += 2
        else:
            embed.add_field(name="Result", value="❌ **NO GOOD**", inline=False)
    else:
        # 1-point conversion
        from gridiron_dice import FIELD_GOAL_DISTANCE
        roll = random.randint(1, 20)
        make_distance = FIELD_GOAL_DISTANCE[roll - 1]
        success = make_distance >= 15

        embed.add_field(name="Attempt", value="1-Point Conversion", inline=False)
        embed.add_field(name="Roll", value=f"🎲 Rolled **{roll}** → Make distance: **{make_distance}** (need 15+)", inline=False)

        if success:
            embed.add_field(name="Result", value="✅ **GOOD!** +1", inline=False)
            game.score[game.possession] += 1
        else:
            embed.add_field(name="Result", value="❌ **NO GOOD**", inline=False)

    # Kickoff to opponent
    game.switch_possession(opponent, kickoff_position(opponent))

    embed.add_field(name="Score", value=game.format_score(), inline=True)
    embed.add_field(name="Time", value=game.format_time(), inline=True)
    embed.add_field(
        name="Kickoff",
        value=f"{opponent} receives at the 30.",
        inline=False
    )
    embed.add_field(
        name="Next",
        value=f"{game.current_player_with_team()}, choose:\n`/balanced` | `/run` | `/pass`",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

    # Check for half/game end
    if game.blocks_left <= 0:
        await end_half(interaction.channel, game)


async def end_half(channel, game: GameState):
    """End the current half"""
    original_half = game.half  # Save before we modify it

    embed = discord.Embed(
        title="⏰ END OF HALF" if game.half == 1 else "🏁 GAME OVER",
        color=discord.Color.red()
    )

    embed.add_field(name="Final Score", value=game.format_score(), inline=False)

    if game.half == 1:
        # Start second half
        game.half = 2
        game.blocks_left = BLOCKS_PER_HALF
        game.drive_start_blocks = BLOCKS_PER_HALF  # Reset drive start for new half

        # Switch possession (team that kicked off in H1 receives in H2)
        # Bombers received first, so Gunners receive second half
        second_half_receiver = "Gunners"
        game.switch_possession(second_half_receiver, kickoff_position(second_half_receiver))

        embed.add_field(
            name="Second Half Kickoff",
            value=f"{second_half_receiver} receive at -30.",
            inline=False
        )
        embed.add_field(
            name="Next",
            value=f"{game.current_player_with_team()}, choose:\n`/balanced` | `/run` | `/pass`",
            inline=False
        )
    else:
        # Game over
        bombers_score = game.score["Bombers"]
        gunners_score = game.score["Gunners"]

        if bombers_score > gunners_score:
            winner = game.bombers_player.mention
            result = f"🏆 **{winner} (Bombers) WINS!** 🏆"
        elif gunners_score > bombers_score:
            winner = game.gunners_player.mention
            result = f"🏆 **{winner} (Gunners) WINS!** 🏆"
        else:
            result = "🤝 **TIE GAME!** 🤝"

        embed.add_field(name="Result", value=result, inline=False)

    await channel.send(embed=embed)

    # Send stats after end of half/game
    stats_embed = game.format_stats()
    await channel.send(embed=stats_embed)

    # Remove game from active games after game over (not at halftime)
    if original_half == 2:
        del games[game.channel_id]


@bot.tree.command(name="status", description="Check current game status")
async def status(interaction: discord.Interaction):
    """Show current game status"""
    game = get_game(interaction.channel_id)

    if not game:
        await interaction.response.send_message("⚠️ No game in progress.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🏈 GAME STATUS",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Matchup",
        value=f"{game.bombers_player.mention} (Bombers) vs {game.gunners_player.mention} (Gunners)",
        inline=False
    )
    embed.add_field(name="Score", value=game.format_score(), inline=True)
    embed.add_field(name="Time", value=game.format_time(), inline=True)
    embed.add_field(
        name="Possession",
        value=f"{game.current_player_with_team()}",
        inline=False
    )
    embed.add_field(
        name="Field Position",
        value=format_field_position(game),
        inline=False
    )
    embed.add_field(
        name="Awaiting",
        value=f"{game.awaiting_action.replace('_', ' ').title()}",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stats", description="View game statistics")
async def stats_command(interaction: discord.Interaction):
    """Show game statistics"""
    game = get_game(interaction.channel_id)

    if not game:
        await interaction.response.send_message("⚠️ No game in progress.", ephemeral=True)
        return

    embed = game.format_stats()
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Show how to play 4th Down")
async def help_command(interaction: discord.Interaction):
    """Show game help and commands"""
    embed = discord.Embed(
        title="🏈 4th Down! A Dice Football Game",
        description="Turn-based dice football for 2 players",
        color=discord.Color.blue()
    )

    # How to start
    embed.add_field(
        name="🎮 How to Start",
        value="Use `/newgame @opponent` to challenge someone to a game!",
        inline=False
    )

    # Play styles
    embed.add_field(
        name="📊 Play Styles (Choose each drive)",
        value=(
            "**`/balanced`** - Moderate yards, 10% turnover risk\n"
            "**`/run`** - Grinds clock, 5% turnover risk (safest)\n"
            "**`/pass`** - Big plays, 20% turnover risk (riskiest)"
        ),
        inline=False
    )

    # 4th down options
    embed.add_field(
        name="🏁 4th Down Options",
        value=(
            "**`/goforit`** - Attempt conversion (or TD!)\n"
            "**`/fieldgoal`** - Try for 3 points\n"
            "**`/punt`** - Kick it away (40 yards)"
        ),
        inline=False
    )

    # Scoring
    embed.add_field(
        name="⚡ Extra Points (After TD)",
        value=(
            "**`/1pt`** - Kick (95% success) → 7 total\n"
            "**`/2pt`** - Go for 2 (40% success) → 8 total"
        ),
        inline=False
    )

    # Utility commands
    embed.add_field(
        name="🔧 Utility",
        value=(
            "**`/status`** - Check current game state\n"
            "**`/stats`** - View game statistics\n"
            "**`/endgame`** - End current game\n"
            "**`/help`** - Show this message"
        ),
        inline=False
    )

    # Quick rules
    embed.add_field(
        name="📜 Quick Rules",
        value=(
            "• Game = 2 halves of 30 game minutes\n"
            "• First downs: Need 10 total yards\n"
            "• Field goals: Must be within 50 yards\n"
            "• TD = 6 points + conversion attempt\n"
            "• Take turns choosing plays"
        ),
        inline=False
    )

    embed.set_footer(text="Good luck! 🏈")

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="endgame", description="End the current game (both players must agree)")
async def endgame(interaction: discord.Interaction):
    """End the current game"""
    game = get_game(interaction.channel_id)

    if not game:
        await interaction.response.send_message("⚠️ No game in progress.", ephemeral=True)
        return

    # Check if user is one of the players
    if interaction.user.id not in [game.bombers_player.id, game.gunners_player.id]:
        await interaction.response.send_message("⚠️ You're not in this game!", ephemeral=True)
        return

    # Remove game
    del games[game.channel_id]

    await interaction.response.send_message("🛑 Game ended. Start a new one with `/newgame`")


# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
        print("Please set your bot token in the environment.")
        exit(1)

    bot.run(TOKEN)
