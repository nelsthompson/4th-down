# Discord Bot Setup Guide

Complete setup guide for deploying your 4th Down Discord bot.

## Step 1: Create a Discord Server

1. Open Discord and click the **+** button on the left sidebar
2. Click **Create My Own**
3. Choose **For me and my friends**
4. Name your server (e.g., "4th Down")
5. Click **Create**

## Step 2: Create Discord Bot Application

1. Go to https://discord.com/developers/applications
2. Click **New Application**
3. Name it "4th Down Bot" (or your preferred name)
4. Click **Create**

### Configure Bot Settings

1. In the left sidebar, click **Bot**
2. Click **Reset Token** (or **Add Bot** if you don't have one)
3. Click **Yes, do it!**
4. **IMPORTANT:** Copy your bot token and save it somewhere safe
   - You'll need this later as `DISCORD_BOT_TOKEN`
   - **Never share this token publicly!**

### Set Bot Permissions

1. Still in the **Bot** section, scroll down to **Privileged Gateway Intents**
2. Enable:
   - ✅ **Message Content Intent**
   - ✅ **Server Members Intent** (optional)

### Generate Invite Link

1. In the left sidebar, click **OAuth2** → **URL Generator**
2. Under **SCOPES**, select:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Under **BOT PERMISSIONS**, select:
   - ✅ Send Messages
   - ✅ Send Messages in Threads
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Use Slash Commands
4. Copy the **Generated URL** at the bottom
5. Open the URL in a new tab
6. Select your server from the dropdown
7. Click **Authorize**

Your bot should now appear in your server (offline until we deploy it)!

## Step 3: Deploy to Railway (Recommended - Easiest)

Railway offers free hosting perfect for Discord bots.

### A. Create Railway Account

1. Go to https://railway.app
2. Click **Sign in with GitHub**
3. Authorize Railway

### B. Deploy from GitHub

**First, push your code to GitHub:**

```bash
# If you haven't already
cd /Users/bryanthompson/Library/CloudStorage/Dropbox/code/4th_down
git add discord_bot.py requirements.txt Procfile runtime.txt
git commit -m "Add Discord bot"
git push
```

**Then deploy on Railway:**

1. Go to https://railway.app/new
2. Click **Deploy from GitHub repo**
3. Click **Configure GitHub App**
4. Select your repository (e.g., `4th-down`)
5. Click **Deploy Now**

### C. Add Environment Variable

1. Once deployed, click on your project
2. Click the **Variables** tab
3. Click **+ New Variable**
4. Add:
   - **Key:** `DISCORD_BOT_TOKEN`
   - **Value:** [Paste your bot token from Step 2]
5. Click **Add**

### D. Verify Deployment

1. Go to the **Deployments** tab
2. Wait for the status to show **Success** (takes ~1-2 minutes)
3. Check your Discord server - your bot should now be **online**! 🟢

---

## Alternative: Deploy to Fly.io

If Railway doesn't work, Fly.io is another excellent free option.

### A. Install Fly.io CLI

```bash
# macOS
brew install flyctl

# Or download from https://fly.io/docs/hands-on/install-flyctl/
```

### B. Sign Up and Login

```bash
flyctl auth signup  # Or: flyctl auth login
```

### C. Create fly.toml Configuration

Create a file named `fly.toml` in your project directory:

```toml
app = "gridiron-dice-bot"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[processes]
  worker = "python discord_bot.py"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
```

### D. Deploy

```bash
cd /Users/bryanthompson/Library/CloudStorage/Dropbox/code/4th_down

# Create app
flyctl launch --no-deploy

# Set your bot token
flyctl secrets set DISCORD_BOT_TOKEN="your_token_here"

# Deploy
flyctl deploy
```

---

## Step 4: Test Your Bot

In your Discord server:

1. Type `/newgame @friend` (mention a friend)
2. You should see the game start!
3. Use `/balanced`, `/run`, or `/pass` to choose your play style
4. The bot will guide you through the rest

### Available Commands

- `/newgame @opponent` - Start a new game
- `/balanced` - Choose balanced offense
- `/run` - Choose run-first offense
- `/pass` - Choose pass-first offense
- `/goforit` - Attempt 4th down conversion
- `/fieldgoal` - Attempt field goal
- `/punt` - Punt the ball
- `/1pt` - Attempt 1-point conversion
- `/2pt` - Attempt 2-point conversion
- `/status` - Check game status
- `/endgame` - End the current game

---

## Troubleshooting

### Bot is Offline

**Check Railway/Fly.io logs:**

Railway:
1. Go to your project
2. Click **Deployments**
3. Click the latest deployment
4. Check the logs for errors

Fly.io:
```bash
flyctl logs
```

**Common issues:**
- Missing `DISCORD_BOT_TOKEN` environment variable
- Incorrect token (make sure no extra spaces)
- Code errors (check logs)

### Commands Not Showing Up

1. Wait 1-2 minutes after deployment for Discord to sync commands
2. Try typing `/` in your Discord server - commands should appear
3. If not, check bot permissions (Step 2)
4. Restart Discord completely

### Bot Responds But Commands Don't Work

- Make sure you enabled **Message Content Intent** in Discord Developer Portal (Step 2)
- Check Railway/Fly.io logs for Python errors

### Game State Lost After Restart

The bot stores game state in memory, so games will be lost if the bot restarts. This is normal for the free tier. Games typically last 10-15 minutes, so this shouldn't be an issue.

---

## Local Testing (Optional)

To test the bot locally before deploying:

```bash
cd /Users/bryanthompson/Library/CloudStorage/Dropbox/code/4th_down

# Install dependencies
pip3 install -r requirements.txt

# Set your token (macOS/Linux)
export DISCORD_BOT_TOKEN="your_token_here"

# Run the bot
python3 discord_bot.py
```

The bot will connect to Discord and be online in your server. Press Ctrl+C to stop.

---

## Updating the Bot

After making changes:

**Railway:**
1. Commit and push to GitHub
2. Railway auto-deploys new changes

**Fly.io:**
```bash
flyctl deploy
```

---

## Cost

Both Railway and Fly.io offer **free tiers** that are perfect for this bot:

- **Railway:** $5/month free credit (more than enough for a Discord bot)
- **Fly.io:** Free tier includes 3 shared VMs

The bot uses minimal resources and should run completely free!

---

## Security Notes

⚠️ **NEVER commit your bot token to Git!**

Your `.gitignore` should include:
```
.env
*.token
```

The bot reads the token from an environment variable, so it's safe to commit the code.

---

## Next Steps

Once your bot is running:

1. Invite friends to your Discord server
2. Challenge them to a game with `/newgame @friend`
3. Have fun!

If you encounter any issues, check the Railway/Fly.io logs first. Most issues are related to the bot token or permissions.

Happy gaming! 🏈
