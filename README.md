# Telegram AI Assistant Bot

A sophisticated Telegram bot powered by OpenAI's GPT-4o Mini and LangMem, designed to provide intelligent conversations with long-term memory capabilities. The bot can remember user preferences, conversation context, and group dynamics across multiple sessions and chats.

## Overview

This bot leverages advanced AI technologies to create a personalized chat experience:
- **Natural Language Understanding**: Uses OpenAI GPT-4o Mini for human-like conversations
- **Persistent Memory**: Stores and retrieves conversation history, user preferences, and facts using LangMem
- **Group Intelligence**: Tracks individual users within group chats and remembers group decisions
- **Profile Management**: Maintains detailed user profiles with interaction statistics
- **Multi-Chat Support**: Works seamlessly in both private and group conversations

## Features

- **Conversational AI**: Context-aware responses powered by GPT-4o Mini
- **Long-term Memory**: Remembers facts, preferences, and context using LangMem and MongoDB vector storage
- **Profile Management**: Stores Telegram user profiles with interaction tracking
- **Group & Private Chat Support**: Distinguishes between group and private conversations with appropriate context
- **Persistent Chat History**: MongoDB-backed conversation history for continuity across sessions
- **Customizable System Prompts**: Dynamic prompts adapted to chat type and user metadata
- **Structured Logging**: Comprehensive logging with Loguru for debugging and monitoring
- **Vector Search**: Semantic memory search using OpenAI embeddings

## Project Structure

```
.
├── main.py                      # Application entry point
├── check.py                     # Environment configuration checker
├── pyproject.toml               # Project dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── config/
│   ├── settings.py              # Configuration management
│   └── langfuse_client.py       # Langfuse tracing client
├── agents/
│   ├── base_agent.py            # Abstract base agent class
│   └── langmem_agent.py         # LangMem-powered agent implementation
├── bot/
│   ├── handlers.py              # Telegram message handlers
│   └── telegram_bot.py          # Bot application setup
├── memory/
│   └── user_manager.py          # User profile and interaction tracking
├── storage/
│   ├── mongodb_client.py        # MongoDB connection singleton
│   └── stores.py                # MongoDB store implementations
├── prompts/
│   └── langmem_prompt.py        # AI system prompts
├── llm/
│   └── openai_client.py         # OpenAI LLM client
├── utils/
│   └── logger.py                # Logging configuration
└── logs/                        # Log files directory
```

## Requirements

- **Python**: 3.13+
- **MongoDB**: Local instance or MongoDB Atlas cloud database
- **OpenAI API Key**: For GPT-4o Mini and embeddings
- **Telegram Bot Token**: From [@BotFather](https://t.me/botfather)

## Installation

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/telegram-bot.git
cd telegram-bot
```

### 2. Install Python 3.13+

#### macOS (using Homebrew):
```sh
brew install python@3.13
```

#### Linux (Ubuntu/Debian):
```sh
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev
```

#### Windows:
Download and install Python 3.13 from [python.org](https://www.python.org/downloads/)

Verify installation:
```sh
python3.13 --version
```

### 3. Install Dependencies with [uv](https://github.com/astral-sh/uv)

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver written in Rust.

#### Install uv:

**macOS and Linux:**
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or via pip:**
```sh
pip install uv
```

#### Install Project Dependencies:

```sh
uv sync
```

This command will:
- Create a virtual environment (`.venv/`) automatically
- Install all dependencies from [`pyproject.toml`](pyproject.toml)
- Lock dependency versions for reproducible builds

**Alternative installation method:**
```sh
uv pip install -e .
```

### 4. Telegram Bot Setup

Follow these steps to create and configure your Telegram bot:

#### Step 1: Create a New Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Start a chat with BotFather and send `/newbot`
3. Follow the prompts:
   - **Bot name**: Choose a display name (e.g., "My AI Assistant")
   - **Bot username**: Choose a unique username ending in "bot" (e.g., "my_ai_assistant_bot")

#### Step 2: Get Your Bot Token

After creating the bot, BotFather will send you a message containing your bot token:

```
Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
```

**⚠️ Keep this token secure!** Anyone with this token can control your bot.

#### Step 3: Configure Bot Settings (Optional)

You can customize your bot using BotFather commands:

- `/setdescription` - Set bot description shown in chat
- `/setabouttext` - Set "About" text in bot profile
- `/setuserpic` - Set bot profile picture
- `/setcommands` - Set bot commands menu

**Example commands to set:**
```
start - Initialize the bot
profile - View your stored profile
```

To set these commands, send `/setcommands` to BotFather, select your bot, and paste:
```
start - Initialize the bot
profile - View your stored profile
```

#### Step 4: Test Your Bot

1. Search for your bot by username in Telegram
2. Start a conversation with `/start`
3. You should see your bot (it won't respond yet until you complete the setup)

### 5. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-proj-...`)
6. **⚠️ Important**: Save this key immediately - you won't be able to see it again

**Pricing**: OpenAI charges per token. GPT-4o Mini is cost-effective for most use cases. Check [OpenAI Pricing](https://openai.com/pricing) for current rates.

### 6. MongoDB Setup

#### Option A: Local MongoDB (Development)

**macOS:**
```sh
# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB service
brew services start mongodb-community@7.0

# Verify it's running
mongosh
```

**Linux (Ubuntu/Debian):**
```sh
# Import MongoDB GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
mongosh
```

**Windows:**
1. Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Run the installer (choose "Complete" installation)
3. Install MongoDB Compass (GUI tool) if desired
4. MongoDB will run as a Windows service automatically

**Connection URI for local MongoDB:**
```
mongodb://localhost:27017
```

#### Option B: MongoDB Atlas (Cloud - Recommended for Production)

1. **Create an Account**:
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for a free account

2. **Create a Cluster**:
   - Click **"Build a Database"**
   - Select **"M0 FREE"** tier
   - Choose your preferred cloud provider and region
   - Click **"Create Cluster"**

3. **Create a Database User**:
   - Go to **"Database Access"** in the left sidebar
   - Click **"Add New Database User"**
   - Choose **"Password"** authentication
   - Set username and password (save these!)
   - Set permissions to **"Read and write to any database"**
   - Click **"Add User"**

4. **Configure Network Access**:
   - Go to **"Network Access"** in the left sidebar
   - Click **"Add IP Address"**
   - For development: Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - For production: Add your specific IP addresses
   - Click **"Confirm"**

5. **Get Connection String**:
   - Go to **"Database"** in the left sidebar
   - Click **"Connect"** on your cluster
   - Choose **"Connect your application"**
   - Select **"Python"** driver version **3.12 or later**
   - Copy the connection string:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   - Replace `<username>` with your database username
   - Replace `<password>` with your database password

6. **Optional: Create Vector Search Index**:
   - Go to your cluster → **"Search"** tab
   - Click **"Create Search Index"**
   - Choose **"JSON Editor"**
   - Database: `telegram_bot` (or your `DB_NAME`)
   - Collection: `langmem_store`
   - Paste this configuration:
   ```json
   {
     "fields": [
       {
         "type": "vector",
         "path": "embedding",
         "numDimensions": 1536,
         "similarity": "cosine"
       }
     ]
   }
   ```
   - Name the index: `vector_index`
   - Click **"Create Search Index"**

### 7. Set Up Environment Variables

Copy the example environment file:

```sh
cp .env.example .env
```

Edit `.env` with your favorite text editor and add your credentials:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
LLM_MODEL=gpt-4o-mini

# MongoDB Configuration (Local)
MONGO_URI=mongodb://localhost:27017
DB_NAME=telegram_bot

# OR MongoDB Atlas (Cloud)
# MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
# DB_NAME=telegram_bot

# Optional: Langfuse Configuration (for tracing/monitoring)
# LANGFUSE_SECRET_KEY=sk-lf-...
# LANGFUSE_PUBLIC_KEY=pk-lf-...
# LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

**⚠️ Security Note**: Never commit your `.env` file to version control! It's already listed in [`.gitignore`](.gitignore).

### 8. Verify Configuration

Run the configuration checker to ensure everything is set up correctly:

```sh
python check.py
```

Expected output:
```
============================================================
🔍 Checking Environment Configuration
============================================================
✅ TELEGRAM_BOT_TOKEN: 12345678...xyz123456
✅ OPENAI_API_KEY: sk-proj-...key_here
✅ MONGO_URI: mongodb:...27017
✅ DB_NAME: telegram_bot_langmem
============================================================
✨ All environment variables are set correctly!
   You can now run: python main.py
```

If any variables are missing, the script will show you what needs to be configured.

### 9. Run the Bot

Activate the virtual environment (if not already activated):

```sh
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Start the bot:

```sh
python main.py
```

**Or run directly with uv (without activating venv):**
```sh
uv run python main.py
```

The bot will start and display:

```
2024-01-15 10:30:00 | INFO     | config.settings:from_env:45 - Loaded settings - Database: telegram_bot
2024-01-15 10:30:01 | INFO     | storage.mongodb_client:initialize:25 - ✅ Connected to MongoDB (async)
2024-01-15 10:30:01 | INFO     | storage.mongodb_client:initialize:30 - ✅ Connected to MongoDB (sync)
2024-01-15 10:30:02 | INFO     | storage.stores:initialize:42 - ✅ MemoryStore initialized
2024-01-15 10:30:02 | INFO     | storage.stores:initialize:42 - ✅ UserProfileStore initialized
2024-01-15 10:30:03 | INFO     | agents.langmem_agent:initialize:55 - ✅ LangMemAgent initialized
2024-01-15 10:30:03 | INFO     | bot.telegram_bot:run:28 - 🤖 Telegram bot is running...
🤖 Telegram bot is running... (Press Ctrl+C to stop)
```

**To stop the bot**: Press `Ctrl+C`

### 10. Test Your Bot

1. Open Telegram and search for your bot by username
2. Start a conversation:

```
You: /start
Bot: 👋 Hi! I'm an AI assistant powered by OpenAI GPT-4o Mini.
     I can remember conversations in this group and individual preferences.
     Just chat naturally and I'll help you!

You: I love pizza
Bot: Pizza is great! What's your favorite topping?

You: /profile
Bot: 👤 Your Stored Profile:
     🆔 User ID: 123456789
     👤 Name: John Doe
     🔖 Username: @johndoe
     📅 Last Updated: 2024-01-15T10:35:22
```

## Usage

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot and receive a welcome message |
| `/profile` | View your stored Telegram profile and interaction statistics |

### Conversation Features

The bot automatically:
- **Remembers preferences**: "I like coffee" → Bot will remember this across sessions
- **Tracks group context**: Understands who said what in group chats
- **Maintains continuity**: Recalls previous conversations even after restarts
- **Adapts responses**: Different behavior in groups vs. private chats
- **Stores user profiles**: Keeps track of your Telegram information

### Example Interactions

**Private Chat:**
```
You: I prefer morning meetings
Bot: Got it! Morning meetings work better for you.

[Later session - bot is restarted]
You: When should we schedule our next call?
Bot: Based on your preference for morning meetings, how about 10 AM tomorrow?
```

**Group Chat:**
```
Alice: I'm the project lead for the mobile app team
Bot: Noted!

[Later in the conversation]
Bob: @bot who's leading the mobile app project?
Bot: Alice is the project lead for the mobile app team.

Charlie: What's Alice's role?
Bot: Alice is the project lead for the mobile app team.
```

### Adding Bot to Groups

1. Add your bot to a Telegram group
2. Make sure the bot has permission to read messages:
   - Go to BotFather
   - Send `/setprivacy`
   - Select your bot
   - Choose **"Disable"** to allow the bot to see all messages

3. The bot will now respond to mentions and remember group context

## Configuration

All configuration is managed via environment variables in `.env`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from BotFather | - | ✅ Yes |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o Mini | - | ✅ Yes |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` | ✅ Yes |
| `DB_NAME` | MongoDB database name | `telegram_bot` | No |
| `LLM_MODEL` | OpenAI model to use | `gpt-4o-mini` | No |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key for tracing | - | No |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key for tracing | - | No |
| `LANGFUSE_BASE_URL` | Langfuse server URL | - | No |

### Optional: Langfuse Integration

[Langfuse](https://langfuse.com/) provides observability and tracing for LLM applications.

To enable Langfuse:
1. Sign up at [Langfuse Cloud](https://cloud.langfuse.com/)
2. Create a new project
3. Get your API keys from project settings
4. Add to `.env`:
   ```env
   LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
   LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
   LANGFUSE_BASE_URL=https://cloud.langfuse.com
   ```

## Architecture

### Memory System

The bot uses a multi-layered memory architecture:

1. **Short-term Memory**: Recent conversation context (via LangGraph checkpointer)
2. **Long-term Memory**: User preferences and facts (via LangMem + MongoDB)
3. **Vector Search**: Semantic memory retrieval using OpenAI embeddings
4. **Profile Storage**: User metadata and interaction statistics

### Data Flow

```
User Message → Telegram Bot → Message Handler
                                     ↓
                              User Manager (Profile & Context)
                                     ↓
                              LangMem Agent (Memory Search)
                                     ↓
                              OpenAI GPT-4o Mini (Response)
                                     ↓
                              MongoDB (Store Memory)
                                     ↓
                              Response to User
```

### Database Collections

The bot creates and manages these MongoDB collections:

| Collection | Purpose |
|------------|---------|
| `langmem_store` | Long-term memories and preferences |
| `user_profiles` | User Telegram profiles |
| `checkpoints` | LangGraph conversation checkpoints |

## Logging

Logs are written to both console and files:

- **Console**: Colored, formatted output for real-time monitoring
- **Files**: `logs/bot_YYYY-MM-DD.log` with 30-day automatic rotation
- **Levels**: INFO (default), DEBUG (for detailed troubleshooting)

**Log file location**: [`logs/`](logs/)

**View logs in real-time**:
```sh
tail -f logs/bot_$(date +%Y-%m-%d).log
```

## Development

### Project Dependencies

Main dependencies (see [`pyproject.toml`](pyproject.toml)):
- `python-telegram-bot`: Telegram Bot API wrapper
- `langchain`: LLM framework
- `langchain-openai`: OpenAI integration
- `langchain-google-genai`: Google Gemini integration (available for future use)
- `langgraph`: Agent workflow orchestration
- `langmem`: Long-term memory management
- `pymongo`: MongoDB Python driver
- `motor`: Async MongoDB driver
- `loguru`: Advanced logging
- `langfuse`: LLM tracing and observability

### Adding New Features

1. **New Agent**: Extend [`BaseAgent`](agents/base_agent.py) class
2. **New Prompts**: Modify [`SystemPrompts`](prompts/langmem_prompt.py)
3. **New Handlers**: Update [`BotHandlers`](bot/handlers.py)
4. **New Storage**: Extend [`BaseStore`](storage/stores.py) class

### Running Tests

```sh
# Install development dependencies
uv sync --dev

# Run tests (when available)
pytest
```

## Troubleshooting

### Bot doesn't respond

**Check 1**: MongoDB connection
```sh
# Test MongoDB connection
mongosh  # For local MongoDB
# OR check MongoDB Atlas dashboard
```

**Check 2**: Telegram bot token
```sh
python check.py  # Verify all environment variables
```

**Check 3**: Review logs
```sh
tail -n 50 logs/bot_$(date +%Y-%m-%d).log
```

**Check 4**: Bot privacy settings
- Go to BotFather
- Send `/setprivacy`
- Select your bot
- Choose **"Disable"** to allow bot to read all messages

### Memory not working

**Issue**: Bot doesn't remember past conversations

**Solutions**:
1. Verify MongoDB is running:
   ```sh
   mongosh  # Should connect successfully
   ```

2. Check OpenAI API key for embeddings:
   ```sh
   python check.py
   ```

3. Verify vector search index in MongoDB Atlas (optional but recommended for better search):
   - Go to Atlas → Your Cluster → Search tab
   - Ensure index exists on `langmem_store` collection

4. Check logs for memory-related errors:
   ```sh
   grep -i "memory\|langmem" logs/bot_$(date +%Y-%m-%d).log
   ```

### Dependencies issues

```sh
# Reinstall all dependencies
uv sync --reinstall

# Clear UV cache
uv cache clean

# Update uv itself
pip install --upgrade uv
```

### Connection timeout errors

**MongoDB Atlas**:
1. Check Network Access settings in Atlas dashboard
2. Verify your IP is whitelisted
3. Test connection string:
   ```python
   from pymongo import MongoClient
   client = MongoClient("your-mongodb-uri")
   client.admin.command('ping')
   print("Connected!")
   ```

**OpenAI API**:
1. Verify API key is valid
2. Check your OpenAI account has available credits
3. Test API connection:
   ```python
   from openai import OpenAI
   client = OpenAI(api_key="your-key")
   response = client.chat.completions.create(
       model="gpt-4o-mini",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   print(response.choices[0].message.content)
   ```

### Bot crashes on startup

1. **Check Python version**:
   ```sh
   python --version  # Should be 3.13+
   ```

2. **Verify all dependencies installed**:
   ```sh
   uv sync
   ```

3. **Check environment variables**:
   ```sh
   python check.py
   ```

4. **Review startup logs**:
   ```sh
   python main.py 2>&1 | tee startup.log
   ```

## Production Deployment

### Recommended Setup

1. **MongoDB**: Use MongoDB Atlas for reliability and backups
2. **Hosting**: Deploy on VPS (DigitalOcean, AWS, GCP) or PaaS (Heroku, Railway)
3. **Process Manager**: Use systemd (Linux) or supervisor to keep bot running
4. **Monitoring**: Enable Langfuse for LLM observability
5. **Backups**: Regular MongoDB backups via Atlas or custom scripts

### Example systemd Service (Linux)

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram AI Assistant Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/telegram-bot
Environment=PATH=/path/to/.venv/bin:/usr/bin
ExecStart=/path/to/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```sh
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use environment variables** - Don't hardcode API keys
3. **Restrict MongoDB access** - Use IP whitelist in Atlas
4. **Rotate API keys regularly** - Update OpenAI and Telegram tokens periodically
5. **Monitor usage** - Track OpenAI API costs and MongoDB storage
6. **Use HTTPS** - For webhook mode (if you switch from polling)

## Cost Considerations

### OpenAI Costs

- **GPT-4o Mini**: Check [OpenAI Pricing](https://openai.com/pricing) for current rates
- **Text Embedding (text-embedding-3-small)**: Check [OpenAI Pricing](https://openai.com/pricing) for current rates
- **Typical conversation**: 500-2000 tokens per interaction

**Example**: Costs vary based on usage. Monitor your usage in the [OpenAI Dashboard](https://platform.openai.com/usage)

### MongoDB Atlas

- **Free Tier (M0)**: 512MB storage - sufficient for 10,000+ conversations
- **Paid tiers**: Start at $9/month for 2GB

### Total Estimated Cost

- **Development**: Free (local MongoDB + minimal OpenAI usage)
- **Small-scale production**: Varies based on usage - monitor OpenAI and MongoDB costs
- **Medium-scale production**: Costs scale with usage

**Tip**: Set up billing alerts in [OpenAI Dashboard](https://platform.openai.com/account/billing) and [MongoDB Atlas](https://cloud.mongodb.com/) to monitor costs.

## License

MIT License

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests (if available)
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup for Contributors

```sh
# Clone your fork
git clone https://github.com/your-username/telegram-bot.git
cd telegram-bot

# Add upstream remote
git remote add upstream https://github.com/original-username/telegram-bot.git

# Create virtual environment and install dependencies
uv sync --dev

# Make your changes and test
python main.py

# Create pull request when ready
```

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/telegram-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/telegram-bot/discussions)
- **Documentation**: This README and inline code documentation

## Acknowledgments

**Powered by:**
- [OpenAI GPT-4o Mini](https://openai.com/) - Language model
- [LangMem](https://github.com/langchain-ai/langmem) - Long-term memory
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [LangChain](https://www.langchain.com/) - LLM framework
- [MongoDB](https://www.mongodb.com/) - Database
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram API wrapper
- [Langfuse](https://langfuse.com/) - LLM observability

## Changelog

### Version 0.1.0 (Current)
- Initial release
- OpenAI GPT-4o Mini integration
- LangMem long-term memory
- MongoDB storage
- User profile management
- Group chat support
- Vector search capabilities