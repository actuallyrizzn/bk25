# BK25 Quick Start Guide

**Get up and running with BK25 in 5 minutes!**

---

## 🚀 Quick Start (5 Minutes)

### 1. Install & Run
```bash
# Clone and setup
git clone https://github.com/actuallyrizzn/bk25.git
cd bk25
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure BK25 (optional)
cp config/bk25_config.json.example config/bk25_config.json
# Edit config/bk25_config.json with your preferences

# Run the server
python -m src.main
```

### 2. Open Browser
Navigate to: `http://localhost:3003`

### 3. Start Automating!
- **Select Persona**: Choose your AI assistant
- **Pick Channel**: Select your target platform
- **Choose Platform**: PowerShell, AppleScript, or Bash
- **Describe Goal**: "Help me backup my Documents folder"

---

## ⚙️ Configuration

### LLM Settings
BK25 supports multiple LLM providers:
- **Ollama** (default): Local models, no API keys needed
- **OpenAI**: GPT-4, GPT-3.5 with API key
- **Anthropic**: Claude models with API key
- **Google**: Gemini models with API key
- **Custom**: Your own API endpoints

### Quick Configuration
1. Click the ⚙️ **Settings** button in the web interface
2. Select your preferred LLM provider
3. Enter API keys and model settings
4. Test the connection
5. Save your configuration

**Note**: Settings are automatically saved to `config/bk25_config.json`

---

## 🎯 Your First Automation

### Example: File Backup Script

1. **Persona**: Vanilla Chatbot (default)
2. **Channel**: Web
3. **Platform**: PowerShell
4. **Message**: "I need to backup my Documents folder to a network drive every day"

**BK25 will:**
- Ask clarifying questions
- Generate a PowerShell script
- Include error handling and logging
- Provide documentation

---

## 🔧 Common Use Cases

### Windows (PowerShell)
- **File Management**: Backup, cleanup, organization
- **User Management**: Active Directory automation
- **System Configuration**: Registry, services, tasks
- **Azure Integration**: Resource management, monitoring

### macOS (AppleScript)
- **App Automation**: Control applications, workflows
- **File Operations**: Finder automation, batch processing
- **System Preferences**: Configuration management
- **Integration**: Connect apps and services

### Linux/Unix (Bash)
- **Server Management**: Monitoring, maintenance
- **DevOps**: Deployment, CI/CD automation
- **System Administration**: User management, security
- **Data Processing**: Log analysis, reporting

---

## 🎭 Persona Quick Reference

| Persona | Best For | Style |
|---------|----------|-------|
| **Vanilla Chatbot** | New users, general tasks | Onboarding-focused |
| **Technical Expert** | Complex problems | Deep technical knowledge |
| **Business Analyst** | Process optimization | Strategic thinking |
| **Ben Brown** | Bot development | Practical experience |
| **Peter Swimm** | System design | Architectural insights |
| **The GOAT** | Creative solutions | Mystical wisdom + humor |
| **Friendly Helper** | Step-by-step guidance | Encouraging support |

---

## 📺 Channel Quick Reference

| Channel | Artifacts | Use Cases |
|---------|-----------|-----------|
| **Web** | HTML, CSS, JS | Web apps, browser automation |
| **Slack** | Block Kit UI | Team workflows, notifications |
| **Teams** | Adaptive Cards | Enterprise collaboration |
| **Discord** | Embeds, commands | Gaming, community tools |
| **WhatsApp** | Templates, replies | Customer communication |
| **Apple Business Chat** | Rich messages | Customer service |
| **Twitch** | Chat commands | Streaming, moderation |

---

## ⚡ Script Execution Policies

| Policy | Allowed | Use When |
|--------|---------|----------|
| **Safe** (Default) | File ops, queries | Learning, testing |
| **Restricted** | Read-only operations | Production, security |
| **Standard** | Most automation | Development, testing |
| **Elevated** | Full system access | Admin tasks (caution!) |

---

## 🔌 API Quick Start

### Basic Usage
```python
import requests

# Chat with BK25
response = requests.post('http://localhost:8000/api/chat', json={
    'message': 'Help me automate file backup',
    'context': {'platform': 'powershell'}
})

# Generate script
script = requests.post('http://localhost:8000/api/generate/script', json={
    'prompt': 'Create a PowerShell backup script',
    'platform': 'powershell'
})
```

### Key Endpoints
- `POST /api/chat` - Start conversation
- `POST /api/generate/script` - Generate automation
- `POST /api/execute/script` - Run scripts
- `GET /api/tasks/{id}` - Monitor progress

---

## 🚨 Troubleshooting

### Common Issues

**App won't start?**
- Check Python version (3.9+)
- Verify port 8000 is free
- Run `pip install -r requirements.txt`

**LLM not working?**
- BK25 works without LLM for basic features
- Install Ollama for local AI: `ollama run llama2:7b`

**Script execution fails?**
- Check execution policy settings
- Verify platform tools are installed
- Review error logs in console

### Getting Help
1. Check this guide
2. Review [User Manual](./USER_MANUAL.md)
3. Check [API Reference](./API_REFERENCE.md)
4. Visit [GitHub Issues](https://github.com/actuallyrizzn/bk25/issues)

---

## 📚 Next Steps

### Learn More
- **[User Manual](./USER_MANUAL.md)**: Comprehensive guide
- **[API Reference](./API_REFERENCE.md)**: Complete API docs
- **[Examples](./USER_MANUAL.md#examples--use-cases)**: Real-world use cases

### Advanced Features
- **Custom Personas**: Create specialized AI assistants
- **Batch Processing**: Handle multiple automation requests
- **Integration Hooks**: Connect with external systems
- **Performance Monitoring**: Track script execution metrics

### Community
- **GitHub**: [github.com/actuallyrizzn/bk25](https://github.com/actuallyrizzn/bk25)
- **Issues**: Report bugs, request features
- **Discussions**: Community support and ideas

---

## 🎉 You're Ready!

**BK25 is designed to be simple and powerful:**

✅ **No complex setup** - Just install and run  
✅ **Natural conversations** - Describe what you want  
✅ **Multiple platforms** - PowerShell, AppleScript, Bash  
✅ **Safe execution** - Built-in safety policies  
✅ **Professional output** - Production-ready scripts  

**Start automating today!** 🤖✨

---

## 📞 Support

- **Developer**: Mark Rizzn Hopkins
- **Email**: [guesswho@rizzn.com](mailto:guesswho@rizzn.com)
- **Website**: [rizzn.net](https://rizzn.net)

---

**"Agents for whomst?"** - For humans who need automation that works! 🤖✨

*This quick start guide is part of BK25 Python Edition - A love letter to the conversational AI community.*
