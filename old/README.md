# 🤖 BK25: Multi-Persona Channel Simulator

> **Hey Ben Brown** 👋 - I took your Botkit legacy and built something new with it! This is my love letter to the conversational AI community you helped create. BK25 keeps the Botkit spirit alive while exploring new directions. Hope you dig it! #vibeprolesummer 🐐✨
> 
> *P.S. - You're one of the personas in here, so you can chat with yourself if you want.*

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
│   │   ├── bk25.js              # Main application controller
│   │   ├── persona-manager.js   # Persona system management
│   │   ├── channel-manager.js   # Channel simulation system
│   │   └── memory.js           # Conversation memory system
│   ├── generators/
│   │   ├── powershell.js       # PowerShell script generation
│   │   ├── applescript.js      # AppleScript generation
│   │   └── bash.js             # Bash script generation
│   └── index.js                # Server entry point
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

### Persona System

Each persona is defined by:
```json
{
  "id": "unique-identifier",
  "name": "Display Name",
  "description": "Brief description",
  "greeting": "Initial user greeting",
  "capabilities": ["list", "of", "capabilities"],
  "systemPrompt": "Detailed system prompt for AI",
  "examples": ["example", "interactions"],
  "channels": ["supported", "channels"]
}
```

### Channel System

Channels provide:
- **Native Artifacts**: Platform-specific components (Slack blocks, Teams cards, etc.)
- **Simulation Environment**: Test multi-modal experiences
- **Context Awareness**: Channel-specific capabilities and limitations

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- (Optional) Ollama for local LLM support

### Installation

```bash
# Clone the repository
git clone https://github.com/toilville/bk25.git
cd bk25

# Install dependencies
npm install

# Start the development server
npm start
```

### Usage

1. **Open Browser**: Navigate to `http://localhost:3000`
2. **Select Configuration**: Choose Persona, Channel, and Platform
3. **Start Conversation**: Describe your automation needs
4. **Get Code**: Receive generated scripts with documentation

### Docker Deployment

```bash
# Build and run with Docker Compose
cd docker && docker-compose up -d

# Or build manually
cd docker && docker build -t bk25 .
docker run -p 3000:3000 bk25
```

## 🎭 Creating Custom Personas

### Via Web Interface
1. Click the **"+ Add Persona"** button
2. Fill in the persona details:
   - **Name**: Display name for the persona
   - **Description**: Brief description of expertise
   - **System Prompt**: Detailed instructions for AI behavior
3. Click **"Create Persona"** to add to the system

### Via JSON File
Create a new file in the `personas/` directory:

```json
{
  "id": "my-expert",
  "name": "My Expert",
  "description": "Specialized expert in my domain",
  "greeting": "Hello! I'm your specialized expert.",
  "capabilities": [
    "Domain-specific knowledge",
    "Specialized automation",
    "Expert guidance"
  ],
  "personality": {
    "tone": "professional and knowledgeable",
    "approach": "methodical and thorough",
    "philosophy": "expertise through experience"
  },
  "systemPrompt": "You are a specialized expert...",
  "examples": [
    "Help with domain-specific tasks",
    "Generate specialized automation",
    "Provide expert guidance"
  ],
  "channels": ["web", "slack", "teams"]
}
```

## 📊 API Reference

### Core Endpoints

```http
# Health check
GET /health

# Chat with current persona
POST /api/chat
{
  "message": "User message",
  "context": {
    "platform": "powershell|applescript|bash"
  }
}

# Persona management
GET /api/personas
GET /api/personas/current
POST /api/personas/switch
POST /api/personas/create

# Channel management
GET /api/channels
GET /api/channels/current
POST /api/channels/switch
```

### Response Format

```json
{
  "message": "AI response text",
  "automation": {
    "platform": "powershell",
    "script": "Generated script content",
    "filename": "suggested-filename.ps1",
    "documentation": "Script documentation"
  },
  "persona": {
    "id": "current-persona-id",
    "name": "Current Persona Name"
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Server configuration
PORT=3000
NODE_ENV=development

# LLM configuration (optional)
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=your-api-key

# Feature flags
ENABLE_ANALYTICS=false
ENABLE_AUTH=false
```

### Persona Configuration

Personas are automatically loaded from the `personas/` directory. The system supports:
- **Hot reloading** during development
- **Validation** of persona structure
- **Fallback personas** if loading fails

## 🛣️ Roadmap

### 🚀 High Priority (Next 3 months)
- **Complete LLM Integration**: Ollama and OpenAI API support
- **Enhanced Code Generation**: Context-aware, multi-step automation
- **Channel-Specific Features**: Slack Block Kit builder, Teams Adaptive Cards
- **Advanced Personas**: Industry-specific and skill-based personas

### 🎯 Medium Priority (3-6 months)
- **Developer Experience**: REST API docs, CLI tool, plugin system
- **User Interface**: Dark mode, mobile optimization, accessibility
- **Analytics & Insights**: Usage tracking, persona effectiveness metrics
- **Infrastructure**: Docker Compose, K8s manifests, CI/CD pipeline

### 🧪 Experimental (6+ months)
- **AI/ML Enhancements**: Intent recognition, code optimization
- **Advanced Automation**: Workflow orchestration, conditional logic
- **Business Features**: Multi-tenant support, team collaboration
- **Enterprise Integration**: SSO, audit logging, compliance features

See [TODO.md](./TODO.md) for the complete feature roadmap.

## ❓ Technical FAQ

### Project Structure & Architecture

**Q: How is BK25 structured internally?**
A: BK25 uses a modular Node.js architecture:
- **Core System** (`src/core/`): Main application logic, persona management, channel simulation, memory system
- **Generators** (`src/generators/`): Platform-specific code generators (PowerShell, AppleScript, Bash)
- **Personas** (`personas/`): JSON configuration files defining AI personalities and capabilities
- **Web Interface** (`web/`): Single-page application with vanilla JavaScript
- **No Framework Dependencies**: Pure Node.js with Express, no React/Vue/Angular complexity

**Q: What does the persona system actually do?**
A: Each persona is a JSON configuration that defines:
- **System prompts** for AI behavior and personality
- **Supported channels** and their capabilities
- **Example interactions** and conversation starters
- **Greeting messages** and onboarding approaches
- The system loads these at runtime and switches context dynamically

**Q: How does channel simulation work?**
A: Channels are abstraction layers that:
- **Generate platform-specific artifacts** (Slack blocks, Teams cards, Discord embeds)
- **Simulate UI constraints** and interaction patterns
- **Provide context-aware examples** based on platform capabilities
- **Enable testing** of multi-modal conversational experiences
- Currently simulated in the web interface, designed for future native integration

**Q: What's the difference between BK25 and traditional chatbots?**
A: BK25 focuses on:
- **Jobs-to-be-done approach**: Understanding user goals before generating solutions
- **Multi-persona flexibility**: Different AI personalities for different use cases
- **Channel-agnostic design**: Same conversation logic across platforms
- **Code generation focus**: Specifically built for automation script creation
- **Anti-enterprise philosophy**: Simple, direct, no unnecessary complexity

### Current Capabilities

**Q: What platforms can BK25 generate code for?**
A: Currently supports:
- **PowerShell**: Windows automation, Active Directory, Azure, file operations
- **AppleScript**: macOS automation, application control, system integration
- **Bash**: Linux/Unix scripting, system administration, DevOps tasks
- **Documentation**: Automatic documentation generation for all scripts
- **Context awareness**: Uses conversation history to improve code quality

**Q: How does the LLM integration work?**
A: Current implementation:
- **Ollama support**: Local LLM integration (in development)
- **OpenAI API**: Cloud-based option (planned)
- **Model flexibility**: Designed to support multiple LLM providers
- **Streaming responses**: Real-time conversation experience
- **Context management**: Maintains conversation history and persona context

**Q: Can I add my own personas?**
A: Yes, two ways:
- **Web interface**: Use the "+ Add Persona" button for quick creation
- **JSON files**: Create custom persona files in the `personas/` directory
- **Hot reloading**: Changes are picked up automatically in development
- **Validation**: System validates persona structure and provides fallbacks

**Q: How extensible is the channel system?**
A: Highly extensible:
- **Plugin architecture**: New channels can be added as modules
- **Artifact generation**: Each channel defines its own output formats
- **Native integration ready**: Designed for future webhook/API integration
- **Simulation first**: Test channel behavior before building native integrations

### Future Capabilities

**Q: What could BK25 easily support in the future?**
A: The architecture enables:

**Additional Platforms**:
- **Python**: Data science, web scraping, automation
- **JavaScript/Node.js**: Web automation, API integration
- **Go**: System tools, microservices, CLI applications
- **Rust**: System programming, performance-critical automation
- **SQL**: Database operations, data analysis queries

**Enhanced Channels**:
- **Native integrations**: Direct API connections to Slack, Teams, Discord
- **Webhook support**: External systems triggering automations
- **Email integration**: Automation results via email
- **SMS/WhatsApp**: Mobile-first automation interfaces
- **Voice interfaces**: Alexa, Google Assistant integration

**Advanced Features**:
- **Multi-step workflows**: Chain multiple automations together
- **Conditional logic**: If-then-else automation flows
- **Scheduled execution**: Time-based automation triggers
- **Error handling**: Robust error recovery and reporting
- **Testing integration**: Automated testing of generated scripts

**Q: How would you add a new code generator?**
A: Simple process:
1. Create new file in `src/generators/` (e.g., `python.js`)
2. Implement the generator interface with `generate()` method
3. Add platform option to web interface dropdown
4. Update persona configurations to support the new platform
5. The system automatically picks up and integrates the new generator

**Q: How would you add a new channel?**
A: Straightforward extension:
1. Create channel module in `src/core/channels/`
2. Define artifact generation methods for the platform
3. Add channel configuration to channel manager
4. Update web interface to include new channel option
5. Create example artifacts and interaction patterns

**Q: What's the deployment story?**
A: Multiple options:
- **Local development**: `npm start` for immediate use
- **Docker**: Containerized deployment with docker-compose
- **Cloud deployment**: Designed for Heroku, Railway, Vercel
- **Self-hosted**: Can run on any Node.js-capable server
- **Kubernetes**: Manifests planned for enterprise deployment

**Q: How does BK25 handle security?**
A: Security considerations:
- **No data persistence**: Conversations are ephemeral by default
- **Local LLM option**: Keep sensitive data on-premises with Ollama
- **API key management**: Secure handling of external service credentials
- **Input validation**: Sanitization of user inputs and generated code
- **Future auth**: Planned support for authentication and authorization

**Q: What's the performance profile?**
A: Optimized for:
- **Fast startup**: Minimal dependencies, quick server initialization
- **Low memory**: Efficient persona and channel management
- **Scalable**: Stateless design enables horizontal scaling
- **Responsive UI**: Vanilla JavaScript for fast interactions
- **LLM flexibility**: Support for both local and cloud AI processing

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Run tests
npm test

# Lint code
npm run lint

# Build for production
npm run build
```

### Project Structure

- **`src/core/`**: Core system components
- **`src/generators/`**: Platform-specific code generators
- **`personas/`**: Persona definition files
- **`web/`**: Frontend web interface
- **`tests/`**: Test files
- **`docs/`**: Documentation

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
- **Issues**: [https://github.com/toilville/bk25/issues](https://github.com/toilville/bk25/issues)

---

**"Agents for whomst?"** - For humans who need automation that works! 🤖✨

*Built with ❤️ by the Toilville team*
