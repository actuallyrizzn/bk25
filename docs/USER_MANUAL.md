# BK25 User Manual

**BK25: Multi-Persona Channel Simulator (Python Edition)**

> **Generate enterprise automation without enterprise complexity**

*"Agents for whomst?" - For humans who need automation that works.*

---

## 📖 Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding BK25](#understanding-bk25)
3. [Persona System](#persona-system)
4. [Channel Simulation](#channel-simulation)
5. [Code Generation](#code-generation)
6. [Script Execution](#script-execution)
7. [Web Interface](#web-interface)
8. [API Usage](#api-usage)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)
11. [Examples & Use Cases](#examples--use-cases)

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** installed on your system
- **Web browser** (Chrome, Firefox, Safari, Edge)
- **Optional**: Ollama for local LLM support

### Configuration
BK25 comes pre-configured for Ollama but supports multiple LLM providers:

1. **Copy the example configuration**:
   ```bash
   cp config/bk25_config.json.example config/bk25_config.json
   ```

2. **Edit the configuration file** with your preferred settings
3. **Or use the web interface** to configure LLM settings dynamically

### Installation

```bash
# Clone the repository
git clone https://github.com/actuallyrizzn/bk25.git
cd bk25

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python -m src.main
```

### First Launch

1. **Open your browser** and navigate to `http://localhost:3003`
2. **Welcome screen** will appear with the default Vanilla Chatbot persona
3. **Select your preferences** for Persona, Channel, and Platform
4. **Start chatting** about your automation needs

---

## ⚙️ Configuration

### LLM Provider Settings

BK25 supports multiple LLM providers, each with different capabilities:

#### **Ollama (Default)**
- **Best for**: Local development, privacy-focused users
- **Setup**: Install Ollama and download models
- **Cost**: Free (local resources)
- **Models**: Llama, Mistral, CodeLlama, and more

#### **OpenAI**
- **Best for**: Production use, advanced reasoning
- **Setup**: Get API key from OpenAI
- **Cost**: Pay-per-token
- **Models**: GPT-4, GPT-3.5-turbo

#### **Anthropic (Claude)**
- **Best for**: Complex reasoning, safety-focused
- **Setup**: Get API key from Anthropic
- **Cost**: Pay-per-token
- **Models**: Claude-3-5-Sonnet, Claude-3-Haiku

#### **Google (Gemini)**
- **Best for**: Multimodal tasks, Google ecosystem
- **Setup**: Get API key from Google AI Studio
- **Cost**: Pay-per-token
- **Models**: Gemini-1.5-Pro, Gemini-1.5-Flash

#### **Custom API**
- **Best for**: Self-hosted models, specialized APIs
- **Setup**: Configure your own endpoint
- **Cost**: Varies
- **Models**: Any compatible API

### Configuration Methods

1. **Configuration File**: Edit `config/bk25_config.json`
2. **Environment Variables**: Set system environment variables
3. **Web Interface**: Use the Settings modal in the UI
4. **Command Line**: Override settings when starting the server

### Advanced Settings

- **Temperature**: Controls creativity (0.0 = focused, 2.0 = creative)
- **Max Tokens**: Limits response length
- **Timeout**: Request timeout in seconds
- **CORS Origins**: Allowed web origins for security

---

## 🧠 Understanding BK25

### What BK25 Is

BK25 is a **conversational AI system** that helps you create automation scripts through natural language conversations. Instead of learning complex programming syntax, you simply describe what you want to accomplish.

### Core Philosophy

**Anti-Enterprise Approach:**
- ❌ No complex onboarding flows
- ❌ No over-engineered configuration
- ❌ No rigid interaction patterns
- ✅ Simple, direct conversations
- ✅ Focus on jobs-to-be-done
- ✅ Automation that just works

### How It Works

1. **You describe** your automation goal in plain English
2. **BK25 understands** your intent through conversation
3. **Persona guides** the interaction based on their expertise
4. **Channel simulates** real-world platform constraints
5. **Code generates** platform-specific automation scripts
6. **Scripts execute** safely with monitoring and safety policies

---

## 🎭 Persona System

### What Are Personas?

Personas are **AI personalities** with different expertise, communication styles, and problem-solving approaches. Each persona is designed for specific use cases and user preferences.

### Available Personas

#### 🎯 **Vanilla Chatbot** (Default)
- **Best for**: New users, general automation tasks
- **Style**: Onboarding-focused, jobs-to-be-done approach
- **Expertise**: General automation, user guidance
- **Use when**: You're new to BK25 or need general help

#### 🧠 **Ben Brown**
- **Best for**: Botkit and conversational AI projects
- **Style**: Practical, experience-based guidance
- **Expertise**: Bot development, conversational interfaces
- **Use when**: Building bots or conversational systems

#### 🏗️ **Peter Swimm**
- **Best for**: Product strategy and system design
- **Style**: Strategic thinking, architectural insights
- **Expertise**: Product management, system architecture
- **Use when**: Planning complex automation systems

#### 🐐 **The GOAT**
- **Best for**: Creative problem-solving and humor
- **Style**: Mystical wisdom with practical humor
- **Expertise**: Creative automation, thinking outside the box
- **Use when**: You need creative solutions or want entertainment

#### 🔧 **Technical Expert**
- **Best for**: Complex technical problems
- **Style**: Deep technical knowledge, systematic approach
- **Expertise**: Advanced automation, system integration
- **Use when**: Dealing with complex technical challenges

#### 🤝 **Friendly Helper**
- **Best for**: Encouraging support and guidance
- **Style**: Warm, encouraging, step-by-step assistance
- **Expertise**: User support, learning guidance
- **Use when**: You need encouragement or step-by-step help

#### 📊 **Business Analyst**
- **Best for**: Process optimization and business automation
- **Style**: Strategic thinking, process-focused
- **Expertise**: Business processes, workflow optimization
- **Use when**: Automating business processes or workflows

### Switching Personas

1. **Click the persona dropdown** in the left column
2. **Select your desired persona** from the list
3. **Persona will greet you** with their unique style
4. **Continue conversation** with the new personality

### Custom Personas

You can create custom personas with:
- **System prompts** defining behavior and expertise
- **Channel support** specifying which platforms they work with
- **Example interactions** showing their communication style
- **Greeting messages** for personalization

---

## 📺 Channel Simulation

### What Are Channels?

Channels simulate **real communication platforms** and their constraints. This helps you understand how your automation would work in different environments and generates appropriate artifacts for each platform.

### Available Channels

#### 🌐 **Web** (Default)
- **Artifacts**: HTML components, CSS styling, JavaScript widgets
- **Use cases**: Web applications, browser automation, UI components
- **Examples**: Form automation, web scraping, UI testing

#### 🍎 **Apple Business Chat**
- **Artifacts**: Rich interactive messages, payments, scheduling
- **Use cases**: Customer service, appointment booking, payments
- **Examples**: Customer support bots, booking systems

#### 🎮 **Discord**
- **Artifacts**: Embeds, slash commands, bot interactions
- **Use cases**: Gaming communities, team collaboration, moderation
- **Examples**: Moderation bots, game integration, team tools

#### 💼 **Microsoft Teams**
- **Artifacts**: Adaptive Cards, task modules, bot framework
- **Use cases**: Enterprise collaboration, project management
- **Examples**: Project tracking, team coordination, approvals

#### 💬 **Slack**
- **Artifacts**: Block Kit UI, workflows, app integrations
- **Use cases**: Team communication, workflow automation
- **Examples**: Notification bots, approval workflows, team tools

#### 📺 **Twitch**
- **Artifacts**: Chat commands, extensions, stream integration
- **Use cases**: Live streaming, community engagement
- **Examples**: Stream moderation, viewer interaction, alerts

#### 📱 **WhatsApp**
- **Artifacts**: Message templates, quick replies, media sharing
- **Use cases**: Customer communication, notifications
- **Examples**: Customer support, appointment reminders

### Channel Switching

1. **Select channel** from the middle column
2. **Interface updates** to show channel-specific features
3. **Generated artifacts** match the selected platform
4. **Examples and templates** reflect platform capabilities

---

## 🛠️ Code Generation

### Supported Platforms

BK25 generates automation scripts for three major platforms:

#### 🪟 **PowerShell** (Windows)
- **Use cases**: Windows administration, Active Directory, Azure
- **Examples**: User management, file operations, system configuration
- **Features**: Error handling, logging, parameter validation

#### 🍎 **AppleScript** (macOS)
- **Use cases**: macOS automation, application control, system integration
- **Examples**: App automation, file management, system preferences
- **Features**: Application integration, system control, user interaction

#### 🐧 **Bash** (Linux/Unix)
- **Use cases**: Linux administration, DevOps, system scripting
- **Examples**: Server management, deployment automation, monitoring
- **Features**: Cross-platform compatibility, system integration

### Code Generation Process

1. **Conversation Analysis**: BK25 understands your automation goal
2. **Platform Selection**: Choose PowerShell, AppleScript, or Bash
3. **Code Generation**: AI creates platform-specific automation
4. **Documentation**: Automatic documentation and comments
5. **Safety Validation**: Scripts checked for dangerous operations
6. **Export Options**: Copy, download, or execute directly

### Generated Script Features

- **Comprehensive Documentation**: Clear comments explaining each step
- **Error Handling**: Robust error checking and recovery
- **Parameter Validation**: Input validation and sanitization
- **Logging**: Detailed execution logging for debugging
- **Safety Checks**: Validation of potentially dangerous operations

---

## ⚡ Script Execution

### Execution Policies

BK25 provides multiple execution policies for different security needs:

#### 🛡️ **Safe Mode** (Default)
- **Allowed**: File operations, system queries, safe commands
- **Restricted**: Network access, system modifications, user data
- **Use when**: Learning, testing, safe automation tasks

#### 🔒 **Restricted Mode**
- **Allowed**: Read-only operations, safe queries
- **Restricted**: File modifications, system changes, network access
- **Use when**: Production environments, security-sensitive tasks

#### ⚖️ **Standard Mode**
- **Allowed**: Most automation tasks, system modifications
- **Restricted**: Dangerous operations, user data access
- **Use when**: Development, testing, controlled environments

#### 🚀 **Elevated Mode**
- **Allowed**: Full system access, administrative operations
- **Restricted**: None (use with extreme caution)
- **Use when**: Administrative tasks, system administration

### Execution Monitoring

- **Real-time Status**: Live updates on script execution
- **Resource Usage**: CPU, memory, and I/O monitoring
- **Performance Metrics**: Execution time and efficiency tracking
- **Error Logging**: Detailed error information and debugging
- **Task History**: Complete execution history and results

### Safety Features

- **Command Validation**: Automatic detection of dangerous commands
- **Resource Limits**: CPU and memory usage limits
- **Timeout Protection**: Automatic termination of long-running tasks
- **Sandbox Execution**: Isolated execution environment
- **Audit Logging**: Complete audit trail of all operations

---

## 🎨 Web Interface

### Interface Layout

BK25 uses a **three-column layout** for intuitive navigation:

#### 📱 **Left Column - Persona Selection**
- Persona dropdown menu
- Current persona information
- Persona switching controls
- Custom persona creation

#### 📺 **Middle Column - Channel Selection**
- Channel platform selection
- Channel-specific features
- Platform capabilities display
- Example artifacts

#### 💻 **Right Column - Platform & Output**
- Code generation platform
- Generated script display
- Execution controls
- Results and monitoring

### Key Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Dynamic content based on selections
- **Progressive Web App**: Offline capabilities and app-like experience
- **Dark Mode Support**: Easy on the eyes for extended use
- **Accessibility**: Screen reader support and keyboard navigation

### Navigation Tips

1. **Start with Persona**: Choose the AI personality that fits your needs
2. **Select Channel**: Pick the platform you're targeting
3. **Choose Platform**: Select your automation target (PowerShell/AppleScript/Bash)
4. **Begin Conversation**: Start describing your automation goal
5. **Review Output**: Check generated code and execute if needed

---

## 🔌 API Usage

### REST API Endpoints

BK25 provides a comprehensive REST API for integration:

#### 🏥 **Health & Status**
```http
GET /health                    # System health check
GET /api/status               # Detailed system status
GET /api/version              # API version information
```

#### 🎭 **Persona Management**
```http
GET /api/personas             # List all available personas
GET /api/personas/current     # Get current active persona
POST /api/personas/switch     # Switch to different persona
POST /api/personas/create     # Create custom persona
```

#### 📺 **Channel Management**
```http
GET /api/channels             # List available channels
GET /api/channels/current     # Get current channel
POST /api/channels/switch     # Switch channel
GET /api/channels/{id}/info   # Get channel details
```

#### 💬 **Chat & Generation**
```http
POST /api/chat               # Chat with current persona
POST /api/generate/script    # Generate automation script
POST /api/generate/platform  # Generate for specific platform
```

#### ⚡ **Execution & Monitoring**
```http
POST /api/execute/script     # Execute generated script
GET /api/tasks               # List running tasks
GET /api/tasks/{id}          # Get task details
POST /api/tasks/{id}/stop    # Stop running task
```

### API Authentication

Currently, BK25 runs without authentication for development. For production use:

1. **Set environment variables** for API keys
2. **Configure CORS** for your domain
3. **Implement rate limiting** if needed
4. **Add logging** for API usage monitoring

### Example API Usage

#### Python Client
```python
import requests

# Chat with BK25
response = requests.post('http://localhost:8000/api/chat', json={
    'message': 'Help me automate file backup on Windows',
    'context': {'platform': 'powershell'}
})

# Generate script
script_response = requests.post('http://localhost:8000/api/generate/script', json={
    'prompt': 'Create a PowerShell script to backup files',
    'platform': 'powershell'
})
```

#### JavaScript Client
```javascript
// Chat with BK25
const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: 'Help me automate file backup on Windows',
        context: {platform: 'powershell'}
    })
});
```

---

## 🚀 Advanced Features

### Custom Persona Creation

Create personas tailored to your specific needs:

```json
{
    "id": "my-custom-persona",
    "name": "My Custom Persona",
    "description": "Specialized for my automation needs",
    "systemPrompt": "You are an expert in...",
    "greeting": "Hello! I'm specialized in...",
    "channels": ["web", "slack"],
    "examples": ["Example conversation starters"]
}
```

### Batch Processing

Process multiple automation requests:

1. **Prepare requests** in JSON format
2. **Send batch** to `/api/batch/process`
3. **Monitor progress** with task IDs
4. **Retrieve results** when complete

### Integration Hooks

BK25 supports webhooks for external integration:

- **Script Generation**: Notify external systems when scripts are created
- **Execution Complete**: Alert systems when automation finishes
- **Error Notifications**: Send alerts for execution failures
- **Usage Analytics**: Track automation usage patterns

### Performance Optimization

- **Async Processing**: Non-blocking script generation
- **Caching**: Intelligent caching of common requests
- **Resource Management**: Efficient memory and CPU usage
- **Connection Pooling**: Optimized database and external connections

---

## 🔧 Troubleshooting

### Common Issues

#### 🚫 **Application Won't Start**
- **Check Python version**: Ensure Python 3.9+ is installed
- **Verify dependencies**: Run `pip install -r requirements.txt`
- **Check port availability**: Ensure port 8000 is free
- **Review logs**: Check console output for error messages

#### 🔌 **LLM Connection Issues**
- **Ollama not running**: Start Ollama service if using local LLM
- **Network issues**: Check firewall and network configuration
- **API key problems**: Verify external API keys if using cloud LLM
- **Fallback mode**: BK25 works without LLM for basic features

#### 📱 **Web Interface Problems**
- **Browser compatibility**: Use modern browsers (Chrome, Firefox, Safari, Edge)
- **JavaScript errors**: Check browser console for error messages
- **CORS issues**: Ensure proper CORS configuration for external access
- **Cache problems**: Clear browser cache and reload

#### ⚡ **Script Execution Issues**
- **Permission problems**: Check execution policy settings
- **Path issues**: Verify script paths and working directories
- **Dependency missing**: Ensure required tools are installed
- **Safety restrictions**: Check execution policy settings

### Getting Help

1. **Check logs**: Review application logs for error details
2. **Review documentation**: Consult this manual and API reference
3. **Test with simple examples**: Start with basic automation tasks
4. **Check system requirements**: Verify Python version and dependencies
5. **Community support**: Visit project repository for issues and discussions

---

## 📚 Examples & Use Cases

### 🪟 Windows Automation

#### File Management
**Goal**: Automate daily file backup
**Persona**: Technical Expert
**Channel**: Web
**Platform**: PowerShell

**Conversation**:
```
User: "I need to backup my Documents folder to a network drive every day"
BK25: "I'll help you create a PowerShell script for automated file backup. Let me ask a few questions..."
```

**Generated Script**: PowerShell script with:
- Daily backup scheduling
- Error handling and logging
- Network drive validation
- Progress reporting

#### User Management
**Goal**: Bulk user creation in Active Directory
**Persona**: Business Analyst
**Channel**: Microsoft Teams
**Platform**: PowerShell

**Generated Script**: AD management script with:
- CSV import functionality
- User validation
- Group assignment
- Audit logging

### 🍎 macOS Automation

#### Application Control
**Goal**: Automate repetitive tasks in applications
**Persona**: Friendly Helper
**Channel**: Slack
**Platform**: AppleScript

**Generated Script**: AppleScript with:
- Application launching
- UI automation
- Data processing
- Result export

#### System Maintenance
**Goal**: Automated system cleanup
**Persona**: Technical Expert
**Channel**: Web
**Platform**: AppleScript

**Generated Script**: Maintenance script with:
- Temporary file cleanup
- Log rotation
- System health checks
- Performance optimization

### 🐧 Linux/Unix Automation

#### Server Management
**Goal**: Automated server monitoring
**Persona**: Technical Expert
**Channel**: Discord
**Platform**: Bash

**Generated Script**: Monitoring script with:
- System metrics collection
- Alert generation
- Performance tracking
- Report generation

#### Deployment Automation
**Goal**: Automated application deployment
**Persona**: Business Analyst
**Channel**: Web
**Platform**: Bash

**Generated Script**: Deployment script with:
- Code deployment
- Database migrations
- Service restart
- Health verification

### 🔄 Cross-Platform Automation

#### Data Processing
**Goal**: Process data files across platforms
**Persona**: Technical Expert
**Channel**: Web
**Platform**: All (PowerShell, AppleScript, Bash)

**Generated Scripts**: Platform-specific scripts with:
- File format detection
- Data validation
- Processing logic
- Output formatting

#### System Integration
**Goal**: Connect different systems and services
**Persona**: Business Analyst
**Channel**: Microsoft Teams
**Platform**: All

**Generated Scripts**: Integration scripts with:
- API connections
- Data transformation
- Error handling
- Monitoring and alerts

---

## 📞 Support & Resources

### Documentation
- **User Manual**: This comprehensive guide
- **API Reference**: Complete API documentation
- **Migration Guide**: Python migration details
- **Contributing Guide**: How to contribute to the project

### Community
- **GitHub Repository**: [github.com/actuallyrizzn/bk25](https://github.com/actuallyrizzn/bk25)
- **Issues**: Report bugs and request features
- **Discussions**: Community discussions and support
- **Wiki**: Community-maintained documentation

### Contact
- **Python Port Developer**: Mark Rizzn Hopkins
- **Email**: [guesswho@rizzn.com](mailto:guesswho@rizzn.com)
- **Website**: [rizzn.net](https://rizzn.net)

---

## 📜 License Information

**BK25 Python Edition** is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0)**.

The **original Node.js implementation** remains licensed under the **MIT License**.

For complete license details, see [LICENSE.md](../LICENSE.md).

---

**"Agents for whomst?"** - For humans who need automation that works! 🤖✨

*This user manual is part of BK25 Python Edition - A love letter to the conversational AI community.*
