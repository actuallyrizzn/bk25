# BK25 API Reference

**BK25: Multi-Persona Channel Simulator (Python Edition)**

> **Complete REST API documentation for BK25**

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL & Endpoints](#base-url--endpoints)
4. [Response Formats](#response-formats)
5. [Error Handling](#error-handling)
6. [Core Endpoints](#core-endpoints)
7. [Persona Management](#persona-management)
8. [Channel Management](#channel-management)
9. [Chat & Generation](#chat--generation)
10. [Script Execution](#script-execution)
11. [System & Status](#system--status)
12. [Examples](#examples)
13. [Rate Limiting](#rate-limiting)
14. [Webhooks](#webhooks)

---

## 🌐 Overview

BK25 provides a comprehensive REST API for programmatic access to all features. The API is designed to be:

- **RESTful**: Follows REST principles and conventions
- **JSON-based**: All requests and responses use JSON format
- **Async-ready**: Built for asynchronous operations
- **Stateless**: No session management required
- **Versioned**: API versioning for future compatibility

### API Version

Current API version: **v1**

### Content Type

All requests and responses use: `application/json`

---

## 🔐 Authentication

**Current Status**: No authentication required for development

**Production Recommendations**:
- Implement API key authentication
- Use HTTPS for all communications
- Implement rate limiting
- Add request logging and monitoring

### Future Authentication

```http
Authorization: Bearer YOUR_API_KEY
X-API-Key: YOUR_API_KEY
```

---

## 🌍 Base URL & Endpoints

### Development
```
http://localhost:8000
```

### Production
```
https://your-domain.com
```

### API Base Path
```
/api/v1
```

---

## 📤 Response Formats

### Success Response
```json
{
    "success": true,
    "data": {
        // Response data here
    },
    "timestamp": "2025-01-27T19:00:00Z",
    "request_id": "req_123456789"
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message",
        "details": "Additional error details"
    },
    "timestamp": "2025-01-27T19:00:00Z",
    "request_id": "req_123456789"
}
```

### Pagination Response
```json
{
    "success": true,
    "data": {
        "items": [],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 100,
            "pages": 5,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

---

## ❌ Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `PERSONA_NOT_FOUND` | 404 | Requested persona doesn't exist |
| `CHANNEL_NOT_FOUND` | 404 | Requested channel doesn't exist |
| `PLATFORM_NOT_SUPPORTED` | 400 | Platform not supported |
| `EXECUTION_FAILED` | 500 | Script execution failed |
| `LLM_ERROR` | 503 | LLM service unavailable |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

## 🏥 Core Endpoints

### Health Check

#### GET /health
Check if the service is running.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-27T19:00:00Z",
    "version": "1.0.0",
    "uptime": "2h 15m 30s"
}
```

### System Status

#### GET /api/status
Get detailed system status and component health.

**Response:**
```json
{
    "status": "operational",
    "components": {
        "persona_manager": "healthy",
        "channel_manager": "healthy",
        "code_generator": "healthy",
        "llm_manager": "degraded",
        "script_executor": "healthy",
        "execution_monitor": "healthy"
    },
    "personas": {
        "total": 8,
        "loaded": 8,
        "current": "vanilla"
    },
    "channels": {
        "total": 7,
        "available": 7,
        "current": "web"
    },
    "generators": {
        "total": 3,
        "platforms": ["powershell", "applescript", "bash"]
    },
    "llm": {
        "providers": 1,
        "status": "connected",
        "model": "llama2:7b"
    },
    "execution": {
        "active_tasks": 0,
        "total_tasks": 15,
        "successful": 14,
        "failed": 1
    }
}
```

### Version Information

#### GET /api/version
Get API version and build information.

**Response:**
```json
{
    "version": "1.0.0",
    "build": "2025.01.27.1",
    "python_version": "3.11.0",
    "fastapi_version": "0.104.1",
    "migration_phase": "Phase 6 - Web Interface & API"
}
```

---

## 🎭 Persona Management

### List All Personas

#### GET /api/personas
Get a list of all available personas.

**Query Parameters:**
- `include_details` (boolean): Include full persona details (default: false)
- `filter` (string): Filter personas by capability or type

**Response:**
```json
{
    "personas": [
        {
            "id": "vanilla",
            "name": "Vanilla Chatbot",
            "description": "Onboarding-focused, jobs-to-be-done approach",
            "channels": ["web", "slack", "teams", "discord"],
            "platforms": ["powershell", "applescript", "bash"]
        },
        {
            "id": "ben-brown",
            "name": "Ben Brown",
            "description": "Botkit creator with practical experience",
            "channels": ["web", "slack", "teams"],
            "platforms": ["powershell", "applescript", "bash"]
        }
    ]
}
```

### Get Current Persona

#### GET /api/personas/current
Get information about the currently active persona.

**Response:**
```json
{
    "persona": {
        "id": "vanilla",
        "name": "Vanilla Chatbot",
        "description": "Onboarding-focused, jobs-to-be-done approach",
        "systemPrompt": "You are a helpful AI assistant...",
        "greeting": "Hello! I'm here to help you with automation...",
        "channels": ["web", "slack", "teams", "discord"],
        "platforms": ["powershell", "applescript", "bash"],
        "examples": [
            "Help me automate file backup",
            "Create a PowerShell script for user management"
        ]
    }
}
```

### Switch Persona

#### POST /api/personas/switch
Switch to a different persona.

**Request Body:**
```json
{
    "persona_id": "technical-expert"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Switched to Technical Expert persona",
    "persona": {
        "id": "technical-expert",
        "name": "Technical Expert",
        "greeting": "Hello! I'm your technical expert..."
    }
}
```

### Create Custom Persona

#### POST /api/personas/create
Create a new custom persona.

**Request Body:**
```json
{
    "id": "my-custom-persona",
    "name": "My Custom Persona",
    "description": "Specialized for my automation needs",
    "systemPrompt": "You are an expert in...",
    "greeting": "Hello! I'm specialized in...",
    "channels": ["web", "slack"],
    "platforms": ["powershell", "bash"],
    "examples": ["Example conversation starters"]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Custom persona created successfully",
    "persona": {
        "id": "my-custom-persona",
        "name": "My Custom Persona"
    }
}
```

---

## 📺 Channel Management

### List All Channels

#### GET /api/channels
Get a list of all available channels.

**Response:**
```json
{
    "channels": [
        {
            "id": "web",
            "name": "Web",
            "description": "HTML components, CSS styling, JavaScript widgets",
            "icon": "[WEB]",
            "capabilities": {
                "rich_text": true,
                "media": true,
                "interactive": true,
                "templates": true
            }
        },
        {
            "id": "slack",
            "name": "Slack",
            "description": "Block Kit UI, workflows, app integrations",
            "icon": "[SLACK]",
            "capabilities": {
                "blocks": true,
                "workflows": true,
                "slash_commands": true,
                "modals": true
            }
        }
    ]
}
```

### Get Current Channel

#### GET /api/channels/current
Get information about the currently active channel.

**Response:**
```json
{
    "channel": {
        "id": "web",
        "name": "Web",
        "description": "HTML components, CSS styling, JavaScript widgets",
        "capabilities": {
            "rich_text": true,
            "media": true,
            "interactive": true,
            "templates": true
        },
        "examples": [
            "HTML form components",
            "CSS styling templates",
            "JavaScript widgets"
        ]
    }
}
```

### Switch Channel

#### POST /api/channels/switch
Switch to a different channel.

**Request Body:**
```json
{
    "channel_id": "slack"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Switched to Slack channel",
    "channel": {
        "id": "slack",
        "name": "Slack",
        "greeting": "Now working with Slack Block Kit UI..."
    }
}
```

### Get Channel Info

#### GET /api/channels/{channel_id}/info
Get detailed information about a specific channel.

**Path Parameters:**
- `channel_id` (string): The ID of the channel

**Response:**
```json
{
    "channel": {
        "id": "slack",
        "name": "Slack",
        "description": "Block Kit UI, workflows, app integrations",
        "icon": "[SLACK]",
        "capabilities": {
            "blocks": true,
            "workflows": true,
            "slash_commands": true,
            "modals": true
        },
        "examples": [
            "Slack Block Kit components",
            "Workflow automation",
            "Slash command responses"
        ],
        "templates": [
            "notification_block.json",
            "form_modal.json",
            "workflow_step.json"
        ]
    }
}
```

---

## 💬 Chat & Generation

### Chat with Persona

#### POST /api/chat
Have a conversation with the current persona.

**Request Body:**
```json
{
    "message": "Help me create a PowerShell script to backup files",
    "context": {
        "platform": "powershell",
        "channel": "web",
        "previous_messages": []
    }
}
```

**Response:**
```json
{
    "response": "I'll help you create a PowerShell script for file backup. Let me ask a few questions to understand your needs better...",
    "persona": {
        "id": "vanilla",
        "name": "Vanilla Chatbot"
    },
    "channel": {
        "id": "web",
        "name": "Web"
    },
    "conversation_id": "conv_123456789",
    "timestamp": "2025-01-27T19:00:00Z"
}
```

### Generate Script

#### POST /api/generate/script
Generate an automation script based on the conversation.

**Request Body:**
```json
{
    "prompt": "Create a PowerShell script to backup files from Documents folder to a network drive",
    "platform": "powershell",
    "context": {
        "conversation_id": "conv_123456789",
        "requirements": ["daily backup", "error handling", "logging"]
    }
}
```

**Response:**
```json
{
    "script": {
        "platform": "powershell",
        "filename": "backup-documents.ps1",
        "content": "# PowerShell Script: Document Backup\n# Generated by BK25\n\nparam(\n    [string]$SourcePath = \"$env:USERPROFILE\\Documents\",\n    [string]$DestinationPath = \"\\\\server\\backup\\documents\"\n)\n\n# ... script content ...",
        "documentation": "This script performs daily backup of Documents folder...",
        "requirements": ["PowerShell 5.1+", "Network access to backup location"],
        "safety_level": "safe",
        "estimated_runtime": "5-10 minutes"
    },
    "persona": {
        "id": "vanilla",
        "name": "Vanilla Chatbot"
    },
    "generation_id": "gen_123456789"
}
```

### Generate for Platform

#### POST /api/generate/platform/{platform}
Generate a script for a specific platform.

**Path Parameters:**
- `platform` (string): Target platform (powershell, applescript, bash)

**Request Body:**
```json
{
    "prompt": "Automate user creation in Active Directory",
    "context": {
        "conversation_id": "conv_123456789",
        "requirements": ["bulk import", "validation", "error handling"]
    }
}
```

**Response:**
```json
{
    "script": {
        "platform": "powershell",
        "filename": "create-ad-users.ps1",
        "content": "# PowerShell Script: AD User Creation\n# ... script content ...",
        "documentation": "This script creates users in Active Directory...",
        "requirements": ["Active Directory module", "Administrative privileges"],
        "safety_level": "elevated",
        "estimated_runtime": "2-5 minutes"
    }
}
```

---

## ⚡ Script Execution

### Execute Script

#### POST /api/execute/script
Execute a generated script.

**Request Body:**
```json
{
    "script_content": "# PowerShell script content...",
    "platform": "powershell",
    "execution_policy": "safe",
    "parameters": {
        "SourcePath": "C:\\Users\\username\\Documents",
        "DestinationPath": "\\\\server\\backup"
    }
}
```

**Response:**
```json
{
    "task_id": "task_123456789",
    "status": "running",
    "message": "Script execution started",
    "execution_policy": "safe",
    "estimated_completion": "2025-01-27T19:05:00Z"
}
```

### Get Task Status

#### GET /api/tasks/{task_id}
Get the status of a running or completed task.

**Path Parameters:**
- `task_id` (string): The ID of the task

**Response:**
```json
{
    "task": {
        "id": "task_123456789",
        "status": "completed",
        "started_at": "2025-01-27T19:00:00Z",
        "completed_at": "2025-01-27T19:02:30Z",
        "execution_time": "2m 30s",
        "exit_code": 0,
        "output": "Backup completed successfully...",
        "error": null,
        "resource_usage": {
            "cpu_percent": 15.2,
            "memory_mb": 45.8,
            "disk_io": "2.1 MB read, 1.8 MB written"
        }
    }
}
```

### List Running Tasks

#### GET /api/tasks
Get a list of all running and recent tasks.

**Query Parameters:**
- `status` (string): Filter by status (running, completed, failed)
- `limit` (integer): Maximum number of tasks to return (default: 20)
- `offset` (integer): Number of tasks to skip (default: 0)

**Response:**
```json
{
    "tasks": [
        {
            "id": "task_123456789",
            "status": "running",
            "platform": "powershell",
            "started_at": "2025-01-27T19:00:00Z",
            "execution_time": "1m 45s"
        }
    ],
    "pagination": {
        "total": 15,
        "running": 1,
        "completed": 13,
        "failed": 1
    }
}
```

### Stop Task

#### POST /api/tasks/{task_id}/stop
Stop a running task.

**Path Parameters:**
- `task_id` (string): The ID of the task to stop

**Response:**
```json
{
    "success": true,
    "message": "Task stopped successfully",
    "task_id": "task_123456789"
}
```

### Delete Task

#### DELETE /api/tasks/{task_id}
Delete a completed or failed task.

**Path Parameters:**
- `task_id` (string): The ID of the task to delete

**Response:**
```json
{
    "success": true,
    "message": "Task deleted successfully",
    "task_id": "task_123456789"
}
```

---

## 🔌 System & Status

### Get Platform Info

#### GET /api/platforms/{platform}/info
Get information about a specific platform.

**Path Parameters:**
- `platform` (string): Platform name (powershell, applescript, bash)

**Response:**
```json
{
    "platform": {
        "name": "PowerShell",
        "version": "7.3.0",
        "description": "Windows automation and administration",
        "capabilities": [
            "Active Directory management",
            "File system operations",
            "System configuration",
            "Azure integration"
        ],
        "examples": [
            "User management scripts",
            "File backup automation",
            "System monitoring"
        ],
        "requirements": ["Windows OS", "PowerShell 5.1+"]
    }
}
```

### Get LLM Provider Info

#### GET /api/llm/providers/{provider_id}/info
Get information about an LLM provider.

**Path Parameters:**
- `provider_id` (string): Provider ID (ollama, openai, etc.)

**Response:**
```json
{
    "provider": {
        "id": "ollama",
        "name": "Ollama",
        "status": "connected",
        "models": [
            "llama2:7b",
            "llama2:13b",
            "codellama:7b"
        ],
        "capabilities": {
            "code_generation": true,
            "conversation": true,
            "fine_tuning": false
        },
        "endpoint": "http://localhost:11434"
    }
}
```

---

## 📚 Examples

### Complete Workflow Example

#### 1. Start Chat
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me create a PowerShell script to backup files",
    "context": {"platform": "powershell"}
  }'
```

#### 2. Generate Script
```bash
curl -X POST "http://localhost:8000/api/generate/script" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a PowerShell script to backup Documents folder",
    "platform": "powershell"
  }'
```

#### 3. Execute Script
```bash
curl -X POST "http://localhost:8000/api/execute/script" \
  -H "Content-Type: application/json" \
  -d '{
    "script_content": "# Generated script content...",
    "platform": "powershell",
    "execution_policy": "safe"
  }'
```

#### 4. Monitor Progress
```bash
curl "http://localhost:8000/api/tasks/task_123456789"
```

### Python Client Example

```python
import requests
import json

class BK25Client:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def chat(self, message, platform=None):
        """Send a chat message to BK25"""
        data = {"message": message}
        if platform:
            data["context"] = {"platform": platform}
        
        response = self.session.post(f"{self.base_url}/api/chat", json=data)
        return response.json()
    
    def generate_script(self, prompt, platform):
        """Generate a script for a specific platform"""
        data = {
            "prompt": prompt,
            "platform": platform
        }
        response = self.session.post(f"{self.base_url}/api/generate/script", json=data)
        return response.json()
    
    def execute_script(self, script_content, platform, policy="safe"):
        """Execute a generated script"""
        data = {
            "script_content": script_content,
            "platform": platform,
            "execution_policy": policy
        }
        response = self.session.post(f"{self.base_url}/api/execute/script", json=data)
        return response.json()
    
    def get_task_status(self, task_id):
        """Get the status of a task"""
        response = self.session.get(f"{self.base_url}/api/tasks/{task_id}")
        return response.json()

# Usage example
client = BK25Client()

# Start a conversation
response = client.chat("Help me create a PowerShell backup script", "powershell")
print(f"BK25: {response['response']}")

# Generate the script
script_response = client.generate_script(
    "Create a PowerShell script to backup Documents folder",
    "powershell"
)
script = script_response['script']

# Execute the script
execution = client.execute_script(script['content'], 'powershell')
task_id = execution['task_id']

# Monitor progress
while True:
    status = client.get_task_status(task_id)
    if status['task']['status'] in ['completed', 'failed']:
        print(f"Task {status['task']['status']}: {status['task']['output']}")
        break
    time.sleep(2)
```

### JavaScript Client Example

```javascript
class BK25Client {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async chat(message, platform = null) {
        const data = { message };
        if (platform) {
            data.context = { platform };
        }
        
        const response = await fetch(`${this.baseUrl}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        return response.json();
    }
    
    async generateScript(prompt, platform) {
        const response = await fetch(`${this.baseUrl}/api/generate/script`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, platform })
        });
        
        return response.json();
    }
    
    async executeScript(scriptContent, platform, policy = 'safe') {
        const response = await fetch(`${this.baseUrl}/api/execute/script`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                script_content: scriptContent,
                platform,
                execution_policy: policy
            })
        });
        
        return response.json();
    }
    
    async getTaskStatus(taskId) {
        const response = await fetch(`${this.baseUrl}/api/tasks/${taskId}`);
        return response.json();
    }
}

// Usage example
const client = new BK25Client();

async function automateBackup() {
    try {
        // Start conversation
        const chatResponse = await client.chat(
            'Help me create a PowerShell backup script',
            'powershell'
        );
        console.log(`BK25: ${chatResponse.response}`);
        
        // Generate script
        const scriptResponse = await client.generateScript(
            'Create a PowerShell script to backup Documents folder',
            'powershell'
        );
        const script = scriptResponse.script;
        
        // Execute script
        const execution = await client.executeScript(
            script.content,
            'powershell'
        );
        const taskId = execution.task_id;
        
        // Monitor progress
        const checkStatus = async () => {
            const status = await client.getTaskStatus(taskId);
            if (status.task.status === 'completed') {
                console.log('Task completed:', status.task.output);
            } else if (status.task.status === 'failed') {
                console.error('Task failed:', status.task.error);
            } else {
                setTimeout(checkStatus, 2000);
            }
        };
        
        checkStatus();
        
    } catch (error) {
        console.error('Error:', error);
    }
}

automateBackup();
```

---

## 🚦 Rate Limiting

**Current Status**: No rate limiting implemented

**Future Implementation**:
- Rate limits per IP address
- Different limits for different endpoints
- Configurable limits via environment variables
- Rate limit headers in responses

### Rate Limit Headers (Future)
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640649600
```

---

## 🔗 Webhooks

**Current Status**: Webhooks not implemented

**Planned Features**:
- Script generation notifications
- Task completion alerts
- Error notifications
- Usage analytics events

### Webhook Configuration (Future)
```json
{
    "webhooks": [
        {
            "url": "https://your-app.com/webhooks/bk25",
            "events": ["script_generated", "task_completed"],
            "secret": "webhook_secret_key"
        }
    ]
}
```

---

## 📞 Support & Resources

### Documentation
- **User Manual**: [USER_MANUAL.md](./USER_MANUAL.md)
- **Migration Guide**: [PYTHON_MIGRATION_PLAN.md](./PYTHON_MIGRATION_PLAN.md)
- **Project Audit**: [PROJECT_AUDIT.md](./PROJECT_AUDIT.md)

### Community
- **GitHub Repository**: [github.com/actuallyrizzn/bk25](https://github.com/actuallyrizzn/bk25)
- **Issues**: Report bugs and request features
- **Discussions**: Community discussions and support

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

*This API reference is part of BK25 Python Edition - A love letter to the conversational AI community.*
