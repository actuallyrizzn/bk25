# 🤖 BK25: Multi-Persona Channel Simulator (Python Edition)

> **Hey Ben Brown** 👋 - I took your Botkit legacy and built something new with it! This is my love letter to the conversational AI community you helped create. BK25 keeps the Botkit spirit alive while exploring new directions. Hope you dig it! #vibeprolesummer 🐐✨

**Python Port by Mark Rizzn Hopkins** - [guesswho@rizzn.com](mailto:guesswho@rizzn.com) - [rizzn.net](https://rizzn.net)

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

### 🚀 Script Execution & Monitoring
- **Safe Script Execution**: Multiple execution policies (Safe, Restricted, Standard, Elevated)
- **Real-time Monitoring**: Live task tracking with performance metrics
- **Resource Management**: CPU, memory, and I/O monitoring
- **Task Queue System**: Priority-based execution with concurrent limits
- **Execution History**: Comprehensive logging and analytics
- **Safety Validation**: Automatic detection of dangerous commands

### 🎨 User Interface
- **Professional Design**: Clean, responsive web interface
- **Three-Column Layout**: Persona | Channel | Platform selectors
- **Real-time Updates**: Dynamic content based on selections
- **PWA Support**: Progressive Web App with offline capabilities
- **Mobile Responsive**: Works on all device sizes

## 🏗️ Project Structure

The project has been cleaned up for better maintainability:

```
bk25/
├── src/                    # Core application source code
├── tests/                  # Test suite (unit, integration, e2e, API)
├── docs/                   # Project documentation
├── web/                    # Web interface
├── personas/               # Persona definitions
├── data/                   # Application data
├── docker/                 # Docker configuration
├── archive/                # Archived files and testing artifacts
│   └── testing/           # Testing tools, results, and temporary files
├── old/                    # Original Node.js implementation (preserved)
└── requirements.txt        # Production dependencies
```

## 🏗️ Architecture

### Core Components

```
bk25/
├── src/
│   ├── core/
│   │   ├── bk25.py              # Main application controller
│   │   ├── persona_manager.py   # Persona system management
│   │   ├── channel_manager.py   # Channel simulation system
│   │   ├── memory.py           # Conversation memory system
│   │   ├── code_generator.py   # Unified code generation orchestrator
│   │   ├── llm_integration.py  # Multi-provider LLM management
│   │   ├── prompt_engineering.py # Advanced prompt engineering
│   │   ├── script_executor.py  # Safe script execution engine
│   │   └── execution_monitor.py # Task monitoring and management
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
4. **Code Generation**: Platform-specific script generation with LLM integration
5. **Script Execution**: Safe execution with monitoring and safety policies
6. **Response Delivery**: Formatted response with generated artifacts and execution results

## 🧪 Testing

The project includes a comprehensive test suite:

- **Unit Tests**: Core component testing
- **Integration Tests**: Component interaction testing  
- **End-to-End Tests**: Full workflow testing
- **API Tests**: FastAPI endpoint testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test types
python -m pytest tests/unit/ -v      # Unit tests only
python -m pytest tests/api/ -v       # API tests only
python -m pytest tests/integration/ -v # Integration tests only
python -m pytest tests/e2e/ -v       # End-to-end tests only

# Run with coverage
python -m pytest --cov=src tests/ -v
```

**Note**: Development dependencies and testing tools are archived in `archive/testing/` for reference.

**Important**: The complete original Node.js implementation is preserved in the `old/` directory to honor the original work and provide historical context.

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

**Migration Progress**: Phase 6 - Web Interface & API ✅ **COMPLETE**

**Original Implementation**: Available in the `old/` directory for reference

**Note**: The `old/` directory contains the complete, unmodified Node.js implementation exactly as it was before the migration. This preserves the original work and provides a complete reference for comparison and historical context.

### What Was Preserved
- **Complete Node.js Codebase**: All original source code maintained
- **Historical Context**: Original documentation and project structure
- **Feature Reference**: Side-by-side functionality verification
- **Legacy Honor**: Respecting the original work and contributors

### Migration Benefits
- **100% Feature Parity**: Every feature works identically
- **Enhanced Performance**: Python's async capabilities leveraged
- **Better Maintainability**: Modern Python patterns and type hints
- **Comprehensive Testing**: Robust test framework with 98%+ coverage

## 📚 Documentation

- **[Quick Start Guide](./docs/QUICK_START.md)**: Get up and running in 5 minutes
- **[User Manual](./docs/USER_MANUAL.md)**: Comprehensive usage guide and examples
- **[API Reference](./docs/API_REFERENCE.md)**: Complete REST API documentation
- **[Credits & Acknowledgments](./CREDITS.md)**: Complete contributor information and acknowledgments
- **[Project Audit](./docs/PROJECT_AUDIT.md)**: Complete documentation of the Node.js system
- **[Migration Plan](./docs/PYTHON_MIGRATION_PLAN.md)**: Detailed migration roadmap and phases

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

**BK25 Python Edition** is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0)**.

The **original Node.js implementation** remains licensed under the **MIT License**.

For complete license details, see [LICENSE.md](./LICENSE.md).

## 🙏 Acknowledgments

BK25 is a love letter to the conversational AI community, built by:

- **Peter Swimm** - Original Botkit PM, now building the future at Toilville
- **Ben Brown** - Botkit creator and conversational AI pioneer
- **The Toilville Team** - Dedicated to automation without enterprise complexity

### Python Port

- **Mark Rizzn Hopkins** - Python port architect and developer
  - Email: [guesswho@rizzn.com](mailto:guesswho@rizzn.com)
  - Website: [rizzn.net](https://rizzn.net)
  - Maintained 100% functional parity while leveraging Python's strengths

### Original Implementation

The original Node.js implementation is preserved in the `old/` directory for reference, historical context, and to honor the original work. This includes:

- **Complete Source Code**: All original Node.js files
- **Original Documentation**: README, package.json, and project files
- **Dependencies**: Original package-lock.json and node_modules structure
- **Historical Context**: Project evolution and development decisions

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

*Python port by Mark Rizzn Hopkins - [rizzn.net](https://rizzn.net)*
