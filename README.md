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
├── pyproject.toml               # Project dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── config/
│   └── settings.py              # Configuration management
├── agents/
│   ├── base_agent.py            # Abstract base agent class
│   └── langmem_agent.py         # LangMem-powered agent implementation
├── bot/
│   ├── handlers.py              # Telegram message handlers
│   └── telegram_bot.py          # Bot application setup
├── memory/
│   ├── chat_history.py          # Chat history management
│   └── user_manager.py          # User profile and interaction tracking
├── storage/
│   ├── mongodb_client.py        # MongoDB connection singleton
│   └── stores.py                # MongoDB store implementations
├── prompts/
│   └── system_prompts.py        # AI system prompts
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

### 2. Set Up Environment Variables

Copy the example environment file and configure your credentials:

```sh
cp .env.example .env
```

Edit `.env` and provide the following required variables:

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
OPENAI_API_KEY=your-openai-api-key-here
MONGO_URI=mongodb://localhost:27017
LLM_MODEL=gpt-4o-mini
```

### 3. Install Dependencies with [uv](https://github.com/astral-sh/uv)

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver written in Rust.

#### Install uv (if not already installed):

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
- Create a virtual environment (if it doesn't exist)
- Install all dependencies from `pyproject.toml`
- Lock dependency versions for reproducible builds

Alternatively, you can use:

```sh
uv pip install -e .
```

### 4. MongoDB Setup

#### Option A: Local MongoDB
```sh
# Install MongoDB locally
# macOS
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community
```

#### Option B: MongoDB Atlas (Cloud)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Get your connection string and add it to `.env`

### 5. Run the Bot

Activate the virtual environment (if using uv sync):
```sh
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Start the bot:
```sh
python main.py
```

Or run directly with uv:
```sh
uv run python main.py
```

The bot will start and display:
```
🤖 Telegram bot is running... (Press Ctrl+C to stop)
```

## Usage

### Bot Commands

- **/start**: Initialize the bot and receive a welcome message
- **/profile**: View your stored Telegram profile and interaction statistics

### Conversation Features

The bot automatically:
- **Remembers preferences**: "I like coffee" → Bot will remember this
- **Tracks group context**: Understands who said what in group chats
- **Maintains continuity**: Recalls previous conversations across sessions
- **Adapts responses**: Different behavior in groups vs. private chats

### Example Interactions

**Private Chat:**
```
You: I prefer morning meetings
Bot: Got it! I'll remember you prefer morning meetings.

[Later session]
You: When should we meet?
Bot: Based on your preference for morning meetings, how about 10 AM?
```

**Group Chat:**
```
Alice: I'm the project lead for this team
Bot: Noted! Alice is the project lead.

[Later]
Bob: Who's leading this project?
Bot: Alice is the project lead for this team.
```

## Configuration

All configuration is managed via environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | **Required** |
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `LLM_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `DB_NAME` | MongoDB database name | `telegram_bot` |
| `COLLECTION_NAME` | Chat history collection | `chat_history` |

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

## Logging

Logs are written to both console and files:
- **Console**: Colored, formatted output for development
- **Files**: `logs/bot_YYYY-MM-DD.log` with 30-day retention
- **Levels**: INFO (default), DEBUG (for troubleshooting)

## Development

### Project Dependencies

Main dependencies (see [`pyproject.toml`](pyproject.toml)):
- `python-telegram-bot`: Telegram Bot API wrapper
- `langchain`: LLM framework
- `langchain-openai`: OpenAI integration
- `langgraph`: Agent workflow orchestration
- `langmem`: Long-term memory management
- `pymongo`: MongoDB driver
- `loguru`: Advanced logging

### Adding New Features

1. **New Agent**: Extend [`BaseAgent`](agents/base_agent.py)
2. **New Prompts**: Add to [`SystemPrompts`](prompts/system_prompts.py)
3. **New Handlers**: Modify [`BotHandlers`](bot/handlers.py)
4. **New Storage**: Extend [`BaseStore`](storage/stores.py)

## Troubleshooting

### Bot doesn't respond
- Check MongoDB connection
- Verify `TELEGRAM_BOT_TOKEN` in `.env`
- Review logs in `logs/` directory

### Memory not working
- Ensure MongoDB is running
- Check `OPENAI_API_KEY` for embeddings
- Verify vector search index (optional but recommended)

### Dependencies issues
```sh
# Reinstall dependencies
uv sync --reinstall

# Clear cache
uv cache clean
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

**Powered by:**
- [OpenAI GPT-4o Mini](https://openai.com/)
- [LangMem](https://github.com/langchain-ai/langmem)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [MongoDB](https://www.mongodb.com/)
- [python-telegram-bot](https://python-telegram-bot.org/)