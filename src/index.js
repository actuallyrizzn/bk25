#!/usr/bin/env node

/**
 * BK25: Generate enterprise automation without enterprise complexity
 * 
 * A love letter to the conversational AI community
 * From Peter Swimm (original Botkit PM) and the Toilville team
 * 
 * "Agents for whomst?" - For humans who need automation that works.
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { BK25Core } from './core/bk25.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize BK25 core
const bk25 = new BK25Core({
  ollamaUrl: process.env.OLLAMA_URL || 'http://localhost:11434',
  model: process.env.BK25_MODEL || 'llama3.1:8b',
  port: process.env.PORT || 3000
});

// Initialize BK25 (load personas, etc.)
await bk25.initialize();

// Express app for web interface and API
const app = express();

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, '../web')));

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    version: '1.0.0',
    tagline: 'Agents for whomst? For humans who need automation that works.',
    ollama: bk25.isOllamaConnected() ? 'connected' : 'disconnected'
  });
});

// Main conversation endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, context = {} } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    const response = await bk25.processMessage(message, context);
    res.json(response);
    
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'BK25 encountered an issue processing your request'
    });
  }
});

// Generate automation script endpoint
app.post('/api/generate', async (req, res) => {
  try {
    const { description, platform = 'powershell', options = {} } = req.body;
    
    if (!description) {
      return res.status(400).json({ error: 'Description is required' });
    }

    const automation = await bk25.generateAutomation(description, platform, options);
    res.json(automation);
    
  } catch (error) {
    console.error('Generation error:', error);
    res.status(500).json({ 
      error: 'Generation failed',
      message: 'Could not generate automation script'
    });
  }
});

// Persona management endpoints
app.get('/api/personas', (req, res) => {
  try {
    const channel = req.query.channel || 'web';
    const personas = bk25.personaManager.getPersonasForChannel(channel);
    res.json(personas);
  } catch (error) {
    console.error('Personas error:', error);
    res.status(500).json({ error: 'Failed to get personas' });
  }
});

app.get('/api/personas/current', (req, res) => {
  try {
    const metadata = bk25.personaManager.getPersonaMetadata();
    res.json(metadata);
  } catch (error) {
    console.error('Current persona error:', error);
    res.status(500).json({ error: 'Failed to get current persona' });
  }
});

app.post('/api/personas/switch', (req, res) => {
  try {
    const { personaId } = req.body;
    
    if (!personaId) {
      return res.status(400).json({ error: 'Persona ID is required' });
    }

    const persona = bk25.personaManager.switchPersona(personaId);
    if (persona) {
      res.json({ 
        success: true, 
        persona: bk25.personaManager.getPersonaMetadata() 
      });
    } else {
      res.status(404).json({ error: 'Persona not found' });
    }
  } catch (error) {
    console.error('Switch persona error:', error);
    res.status(500).json({ error: 'Failed to switch persona' });
  }
});

// Channel management endpoints
app.get('/api/channels', (req, res) => {
  try {
    const channels = bk25.channelManager.getAllChannels();
    res.json(channels);
  } catch (error) {
    console.error('Channels error:', error);
    res.status(500).json({ error: 'Failed to get channels' });
  }
});

app.get('/api/channels/current', (req, res) => {
  try {
    const currentChannel = bk25.channelManager.getCurrentChannel();
    res.json(currentChannel);
  } catch (error) {
    console.error('Current channel error:', error);
    res.status(500).json({ error: 'Failed to get current channel' });
  }
});

app.post('/api/channels/switch', (req, res) => {
  try {
    const { channelId } = req.body;
    
    if (!channelId) {
      return res.status(400).json({ error: 'Channel ID is required' });
    }

    const channel = bk25.channelManager.switchChannel(channelId);
    if (channel) {
      res.json({ 
        success: true, 
        channel: channel,
        artifacts: bk25.channelManager.getAvailableArtifacts(),
        capabilities: bk25.channelManager.getChannelCapabilities()
      });
    } else {
      res.status(404).json({ error: 'Channel not found' });
    }
  } catch (error) {
    console.error('Switch channel error:', error);
    res.status(500).json({ error: 'Failed to switch channel' });
  }
});

app.post('/api/channels/generate-artifact', async (req, res) => {
  try {
    const { artifactType, description, options = {} } = req.body;
    
    if (!artifactType || !description) {
      return res.status(400).json({ error: 'Artifact type and description are required' });
    }

    const artifact = await bk25.channelManager.generateChannelArtifact(artifactType, description, options);
    res.json(artifact);
    
  } catch (error) {
    console.error('Generate artifact error:', error);
    res.status(500).json({ 
      error: 'Failed to generate artifact',
      message: error.message
    });
  }
});

// Add persona creation endpoint
app.post('/api/personas/create', async (req, res) => {
  try {
    const { name, description, systemPrompt, channels = ['web'] } = req.body;
    
    if (!name || !systemPrompt) {
      return res.status(400).json({ error: 'Name and system prompt are required' });
    }

    // Create persona ID from name
    const personaId = name.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-');
    
    const newPersona = {
      id: personaId,
      name: name,
      description: description || `Custom persona: ${name}`,
      greeting: `Hello! I'm ${name}. How can I help you today?`,
      capabilities: ['Custom assistance based on provided instructions'],
      personality: {
        tone: 'helpful and adaptive',
        approach: 'follows custom instructions',
        philosophy: 'user-defined behavior',
        motto: 'customized for your needs'
      },
      systemPrompt: systemPrompt,
      examples: ['Ask me anything within my custom instructions'],
      channels: channels,
      custom: true
    };

    // Add to persona manager (in memory)
    bk25.personaManager.personas.set(personaId, newPersona);
    
    res.json({ 
      success: true, 
      persona: newPersona 
    });
  } catch (error) {
    console.error('Create persona error:', error);
    res.status(500).json({ error: 'Failed to create persona' });
  }
});

// Start server
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`
🤖 BK25: Generate enterprise automation without enterprise complexity

Server running on http://localhost:${PORT}
Web interface: http://localhost:${PORT}
API endpoint: http://localhost:${PORT}/api/chat

"Agents for whomst?" - For humans who need automation that works.

Checking Ollama connection...
`);
  
  // Check Ollama connection on startup
  bk25.checkOllamaConnection().then(connected => {
    if (connected) {
      console.log('✅ Ollama connected successfully');
      console.log(`📝 Using model: ${bk25.config.model}`);
    } else {
      console.log('❌ Ollama not connected');
      console.log('💡 Start Ollama with: ollama serve');
      console.log('💡 Pull model with: ollama pull llama3.1:8b');
    }
  });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 BK25 shutting down gracefully...');
  process.exit(0);
});
