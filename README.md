# Discord Internship Bot

A Discord bot that automatically scrapes and posts internship opportunities from Australian job boards (Indeed, Seek, LinkedIn, GradConnection, Jora).

## 🤖 Add This Bot to Your Server

You can invite this bot to your Discord server using the following link:

**[➡️ Invite Internship Bot to Your Server](https://discord.com/oauth2/authorize?client_id=1465612396448972861)**

> **Note**: This bot is currently hosted on a free-tier server and may experience downtime. For the best experience, consider hosting your own instance using the instructions below.

---

## 🚀 Features

- **Multi-Platform Scraping**: Scrapes 5 major Australian job boards
  - Indeed Australia
  - Seek
  - LinkedIn
  - GradConnection
  - Jora
- **Automated Posting**: Posts new internships to Discord every 2 hours
- **Manual Search**: Use `!internjobs` command to search on-demand
- **Duplicate Prevention**: Tracks seen jobs to avoid reposting
- **Timeout Protection**: Prevents scrapers from hanging
- **User Agent Rotation**: Randomizes headers to avoid detection

## 📋 Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Discord Server with a channel for job postings

## 🛠️ Setup Instructions

> **Want to use the public bot?** Simply use the [invite link above](#-add-this-bot-to-your-server) to add the bot to your server. The instructions below are only needed if you want to host your own instance.

### 1. Clone the Repository

```bash
git clone https://github.com/bishal-uts/discord-internship-bot-public.git
cd discord-internship-bot-public
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
5. Click "Reset Token" and copy your bot token
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot`
8. Select bot permissions: `Send Messages`, `Embed Links`
9. Copy the generated URL and open it in your browser to add the bot to your server

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your values:

```
DISCORD_TOKEN=your_actual_bot_token_here
TARGET_CHANNEL_ID=your_channel_id_here
```

To get your channel ID:
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on your target channel and select "Copy ID"

### 5. Run the Bot

```bash
python main.py
```

## 💬 Commands

- `!ping` - Check if the bot is online
- `!internjobs` - Manually search for new internships

## 📝 How It Works

1. Bot connects to Discord using your token
2. Every 2 hours, it scrapes all configured job boards
3. Filters results for internship-related keywords
4. Checks against `seen_jobs.json` to avoid duplicates
5. Posts new jobs as embed messages to your Discord channel

## ⚠️ Important Notes

### Web Scraping Limitations

- This bot uses **web scraping** instead of official APIs
- Websites can change their HTML structure, breaking the scrapers
- Some sites may block or rate-limit scrapers
- LinkedIn's Terms of Service prohibit automated scraping

### Recommended Improvements

- Use official APIs where available (Indeed has a free tier)
- Add error notifications to Discord
- Implement retry logic with exponential backoff
- Add logging for debugging

## 🔒 Security

- **Never commit** your `.env` file to Git
- The `.gitignore` file is configured to prevent this
- Keep your Discord bot token secret
- Regenerate your token if it's ever exposed

## 📄 License

MIT License - feel free to use and modify

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Issues

If you encounter any issues or have suggestions, please open an issue on GitHub.

---

**Disclaimer**: This project is for educational purposes. Always respect websites' Terms of Service and robots.txt files.
