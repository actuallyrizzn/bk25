# Channel Modules

This directory contains channel-specific modules for BK25's multi-channel simulation system.

## Overview

Each channel module provides:
- **Artifact Generation**: Platform-specific components and formatting
- **Simulation Environment**: Channel-specific UI constraints and capabilities
- **Context Awareness**: Understanding of platform limitations and features
- **Native Integration**: Hooks for future webhook/API connections

## Channel Structure

Each channel module should implement:

```javascript
class ChannelModule {
  constructor(config) {
    this.name = config.name;
    this.capabilities = config.capabilities;
  }

  // Generate platform-specific artifacts
  generateArtifact(type, content) {
    // Return formatted artifact for this channel
  }

  // Simulate channel constraints
  validateMessage(message) {
    // Check message against channel limitations
  }

  // Format response for channel
  formatResponse(response) {
    // Apply channel-specific formatting
  }
}
```

## Supported Channels

### Web (Default)
- **File**: `web.js`
- **Artifacts**: HTML components, CSS styling, JavaScript widgets
- **Capabilities**: Rich formatting, interactive elements, media support

### Apple Business Chat
- **File**: `apple-business-chat.js`
- **Artifacts**: Rich interactive messages, payment requests, scheduling
- **Capabilities**: Business integrations, secure messaging, Apple Pay

### Discord
- **File**: `discord.js`
- **Artifacts**: Embeds, slash commands, bot interactions
- **Capabilities**: Rich embeds, reactions, thread support

### Microsoft Teams
- **File**: `teams.js`
- **Artifacts**: Adaptive Cards, task modules, bot framework
- **Capabilities**: Enterprise integration, meeting bots, workflows

### Slack
- **File**: `slack.js`
- **Artifacts**: Block Kit UI, workflows, app integrations
- **Capabilities**: Interactive components, modals, shortcuts

### Twitch
- **File**: `twitch.js`
- **Artifacts**: Chat commands, extensions, stream integration
- **Capabilities**: Real-time chat, subscriber features, bits

### WhatsApp
- **File**: `whatsapp.js`
- **Artifacts**: Message templates, quick replies, media sharing
- **Capabilities**: Business messaging, media support, location

## Adding New Channels

1. **Create Module File**: Add new channel module in this directory
2. **Implement Interface**: Follow the channel module structure above
3. **Register Channel**: Add to channel manager configuration
4. **Update UI**: Add channel option to web interface
5. **Create Documentation**: Document channel-specific features

## Example Channel Module

```javascript
// src/core/channels/example.js
class ExampleChannel {
  constructor() {
    this.name = 'example';
    this.capabilities = ['text', 'images', 'buttons'];
  }

  generateArtifact(type, content) {
    switch (type) {
      case 'message':
        return this.formatMessage(content);
      case 'button':
        return this.formatButton(content);
      default:
        return content;
    }
  }

  formatMessage(content) {
    return {
      type: 'message',
      text: content,
      platform: 'example'
    };
  }

  formatButton(content) {
    return {
      type: 'button',
      label: content.label,
      action: content.action,
      platform: 'example'
    };
  }
}

module.exports = ExampleChannel;
```

## Integration Points

Channels integrate with:
- **Persona Manager**: Persona-specific channel capabilities
- **Code Generators**: Platform-aware automation scripts
- **Memory System**: Channel-specific conversation history
- **Web Interface**: Dynamic UI based on selected channel
