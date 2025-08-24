# 🤖 BK25: Multi-Persona Channel Simulator (Python Edition)

> **Hey Ben Brown** 👋 - I took your Botkit legacy and built something new with it! This is my love letter to the conversational AI community you helped create. BK25 keeps the Botkit spirit alive while exploring new directions. Hope you dig it! #vibeprolesummer 🐐✨

---

> **Generate enterprise automation without enterprise complexity**

*"Agents for whomst?" - For humans who need automation that works.*

BK25 is a sophisticated multi-persona conversational AI system that helps users generate automation scripts through natural language conversations. Built with an onboarding-focused approach, it guides users through understanding their jobs-to-be-done before generating platform-specific automation code.

## 🎯 Philosophy

BK25 embodies an **anti-enterprise** philosophy:

**What BK25 Delivers:**
- Simple onboarding focused on jobs to be done
- Multi-persona system without complexity
- Channel simulation for real-world testing
- Custom persona creation without enterprise overhead
- Automation that just works

**What BK25 Avoids:**
- Complex onboarding flows
- Over-engineered persona management
- Enterprise-grade configuration nightmares
- Forcing users into rigid interaction patterns

## ✨ Current Features

### 🎭 Multi-Persona System
- **8 Built-in Personas** with unique personalities and expertise
- **Custom Persona Creation** with intuitive modal interface
- **Real-time Persona Switching** with dynamic greetings
- **Onboarding-Focused Default** (Vanilla Chatbot)

#### Available Personas
- **Vanilla Chatbot** (Default): Onboarding-focused, jobs-to-be-done approach
- **Ben Brown**: Botkit creator with practical experience
- **Peter Swimm**: Original Botkit PM with product insights
- **The GOAT** 🐐: Mystical wisdom with humor
- **Technical Expert**: Deep technical knowledge and solutions
- **Friendly Helper**: Warm, encouraging assistance
- **Business Analyst**: Strategic thinking and process optimization
- **+ Custom Personas**: Create your own with system prompts

### 📺 Channel Simulator
**7 Communication Channels** with native artifact generation:

1. **Web** (Default): HTML components, CSS styling, JavaScript widgets
2. **Apple Business Chat**: Rich interactive messages, payments, scheduling
3. **Discord**: Embeds, slash commands, bot interactions
4. **Microsoft Teams**: Adaptive Cards, task modules, bot framework
5. **Slack**: Block Kit UI, workflows, app integrations
6. **Twitch**: Chat commands, extensions, stream integration
7. **WhatsApp**: Message templates, quick replies, media sharing

### 🛠️ Code Generation
- **3 Platform Support**: PowerShell (Windows), AppleScript (macOS), Bash (Linux/Unix)
- **Context-Aware Generation**: Based on conversation history
- **Documentation Included**: Automatic documentation for generated scripts
- **Copy & Export**: Easy script copying and sharing

### 🎨 User Interface
- **Professional Design**: Clean, responsive web interface
- **Three-Column Layout**: Persona | Channel | Platform selectors
- **Real-time Updates**: Dynamic content based on selections
- **PWA Support**: Progressive Web App with offline capabilities
- **Mobile Responsive**: Works on all device sizes

## 🏗️ Architecture

### Core Components

```
bk25/
├── src/
│   ├── core/
│   │   ├── bk25.py              # Main application controller
│   │   ├── persona_manager.py   # Persona system management
│   │   ├── channel_manager.py   # Channel simulation system
│   │   └── memory.py           # Conversation memory system
│   ├── generators/
│   │   ├── powershell.py       # PowerShell script generation
│   │   ├── applescript.py      # AppleScript generation
│   │   └── bash.py             # Bash script generation
│   └── main.py                 # FastAPI server entry point
├── personas/                   # Persona definition files
├── web/                       # Frontend web interface
└── docker/                    # Containerization configs
```

### System Flow

1. **User Interaction**: User selects persona, channel, and platform
2. **Persona Processing**: Selected persona processes user input with context
3. **Channel Simulation**: Channel-specific formatting and capabilities
4. **Code Generation**: Platform-specific script generation
5. **Response Delivery**: Formatted response with generated artifacts

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or poetry
- (Optional) Ollama for local LLM support

### Installation

```bash
# Clone the repository
git clone https://github.com/actuallyrizzn/bk25.git
cd bk25

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
python src/main.py
```

### Usage

1. **Open Browser**: Navigate to `http://localhost:8000`
2. **Select Configuration**: Choose Persona, Channel, and Platform
3. **Start Conversation**: Describe your automation needs
4. **Get Code**: Receive generated scripts with documentation

### Docker Deployment

```bash
# Build and run with Docker Compose
cd docker && docker-compose up -d

# Or build manually
cd docker && docker build -t bk25 .
docker run -p 8000:8000 bk25
```

## 🔄 Migration Status

This is the **Python Edition** of BK25, migrated from the original Node.js implementation. The migration maintains 100% functional parity while leveraging Python's strengths.

**Migration Progress**: Phase 1 - Foundation & Core Infrastructure

**Original Implementation**: Available in the `old/` directory for reference

## 📚 Documentation

- **[Project Audit](./docs/PROJECT_AUDIT.md)**: Complete documentation of the Node.js system
- **[Migration Plan](./docs/PYTHON_MIGRATION_PLAN.md)**: Detailed migration roadmap and phases
- **[API Reference](./docs/API_REFERENCE.md)**: REST API documentation (coming soon)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server with hot reload
uvicorn src.main:app --reload --port 8000

# Run tests
pytest

# Lint code
flake8 src/
```

## 📜 License

BK25 is released under the [MIT License](./LICENSE.md).

## 🙏 Acknowledgments

BK25 is a love letter to the conversational AI community, built by:

- **Peter Swimm** - Original Botkit PM, now building the future at Toilville
- **Ben Brown** - Botkit creator and conversational AI pioneer
- **The Toilville Team** - Dedicated to automation without enterprise complexity

### Inspiration

BK25 builds upon the legacy of:
- **Botkit** - The original conversational AI framework
- **Microsoft Bot Framework** - Enterprise bot development platform
- **The conversational AI community** - Years of innovation and collaboration

## 🔗 Links

- **Website**: [https://toilville.com/bk25](https://toilville.com/bk25)
- **Documentation**: [https://docs.toilville.com/bk25](https://docs.toilville.com/bk25)
- **Community**: [https://community.toilville.com](https://community.toilville.com)
- **Issues**: [https://github.com/actuallyrizzn/bk25/issues](https://github.com/actuallyrizzn/bk25/issues)

---

**"Agents for whomst?"** - For humans who need automation that works! 🤖✨

*Built with ❤️ by the Toilville team - Now in Python! 🐍*
