/**
 * BK25 Core: The heart of automation generation
 * 
 * This is where the magic happens - converting natural language
 * into working PowerShell, AppleScript, and Bash automation.
 * 
 * Philosophy: Simple, focused, and actually works.
 */

import fetch from 'node-fetch';
import { PowerShellGenerator } from '../generators/powershell.js';
import { AppleScriptGenerator } from '../generators/applescript.js';
import { BashGenerator } from '../generators/bash.js';
import { ConversationMemory } from './memory.js';
import { PersonaManager } from './persona-manager.js';
import { ChannelManager } from './channel-manager.js';

export class BK25Core {
  constructor(config = {}) {
    this.config = {
      ollamaUrl: config.ollamaUrl || 'http://localhost:11434',
      model: config.model || 'llama3.1:8b',
      temperature: config.temperature || 0.1, // Low temperature for consistent code generation
      maxTokens: config.maxTokens || 2048,
      ...config
    };

    // Initialize generators
    this.generators = {
      powershell: new PowerShellGenerator(),
      applescript: new AppleScriptGenerator(),
      bash: new BashGenerator()
    };

    // Initialize conversation memory
    this.memory = new ConversationMemory();

    // Initialize persona manager
    this.personaManager = new PersonaManager();

    // Initialize channel manager
    this.channelManager = new ChannelManager();

    // Connection status
    this.ollamaConnected = false;
  }

  /**
   * Initialize BK25 (call this after construction)
   */
  async initialize() {
    await this.personaManager.initialize();
  }

  /**
   * Check if Ollama is running and accessible
   */
  async checkOllamaConnection() {
    try {
      const response = await fetch(`${this.config.ollamaUrl}/api/tags`);
      this.ollamaConnected = response.ok;
      return this.ollamaConnected;
    } catch (error) {
      this.ollamaConnected = false;
      return false;
    }
  }

  /**
   * Get connection status
   */
  isOllamaConnected() {
    return this.ollamaConnected;
  }

  /**
   * Generate completion using Ollama
   */
  async generateCompletion(prompt, options = {}) {
    if (!this.ollamaConnected) {
      await this.checkOllamaConnection();
    }

    if (!this.ollamaConnected) {
      throw new Error('Ollama is not connected. Please start Ollama and ensure the model is available.');
    }

    try {
      const response = await fetch(`${this.config.ollamaUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.config.model,
          prompt: prompt,
          stream: false,
          options: {
            temperature: options.temperature || this.config.temperature,
            num_predict: options.maxTokens || this.config.maxTokens,
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Ollama generation error:', error);
      throw error;
    }
  }

  /**
   * Process a conversational message
   */
  async processMessage(message, context = {}) {
    try {
      // Store message in memory
      await this.memory.addMessage('user', message, context);

      // Determine if this is an automation request
      const isAutomationRequest = await this.detectAutomationIntent(message);

      let response;
      if (isAutomationRequest.isAutomation) {
        // Generate automation script
        const automation = await this.generateAutomation(
          message, 
          isAutomationRequest.platform || 'powershell',
          context
        );
        
        response = {
          type: 'automation',
          message: `I've generated a ${isAutomationRequest.platform || 'PowerShell'} script for your automation:`,
          automation: automation,
          conversational: true
        };
      } else {
        // Regular conversation using current persona
        const conversationHistory = await this.memory.getRecentMessages(5);
        const conversationPrompt = this.personaManager.buildPersonaPrompt(message, conversationHistory);
        
        const aiResponse = await this.generateCompletion(conversationPrompt);
        
        response = {
          type: 'conversation',
          message: aiResponse,
          conversational: true
        };
      }

      // Store response in memory
      await this.memory.addMessage('assistant', response.message, { type: response.type });

      return response;
    } catch (error) {
      console.error('Message processing error:', error);
      return {
        type: 'error',
        message: 'I encountered an issue processing your request. Please try again.',
        error: error.message
      };
    }
  }

  /**
   * Detect if a message is requesting automation
   */
  async detectAutomationIntent(message) {
    const explicitAutomationKeywords = [
      'create a script', 'generate a script', 'write a script',
      'create automation', 'generate automation', 'write automation',
      'create a powershell', 'generate a powershell', 'write a powershell',
      'create an applescript', 'generate an applescript', 'write an applescript',
      'create a bash', 'generate a bash', 'write a bash'
    ];

    const platformKeywords = {
      powershell: ['powershell', 'windows', 'ps1', '.ps1'],
      applescript: ['applescript', 'macos', 'mac', 'apple script', 'automator'],
      bash: ['bash script', 'shell script', 'linux script', 'unix script', '.sh']
    };

    const lowerMessage = message.toLowerCase();
    
    // Only trigger automation for explicit script requests
    const isAutomation = explicitAutomationKeywords.some(keyword => 
      lowerMessage.includes(keyword)
    );

    // Detect platform
    let platform = 'powershell'; // default
    for (const [platformName, keywords] of Object.entries(platformKeywords)) {
      if (keywords.some(keyword => lowerMessage.includes(keyword))) {
        platform = platformName;
        break;
      }
    }

    return { isAutomation, platform };
  }

  /**
   * Generate automation script
   */
  async generateAutomation(description, platform = 'powershell', options = {}) {
    const generator = this.generators[platform];
    if (!generator) {
      throw new Error(`Unsupported platform: ${platform}`);
    }

    // Build prompt for script generation
    const prompt = generator.buildGenerationPrompt(description, options);
    
    // Generate script using LLM
    const generatedScript = await this.generateCompletion(prompt, {
      temperature: 0.1, // Very low temperature for consistent code
      maxTokens: 4096   // More tokens for longer scripts
    });

    // Parse and validate the generated script
    const parsedScript = generator.parseGeneratedScript(generatedScript);
    
    // Add metadata
    const automation = {
      platform: platform,
      description: description,
      script: parsedScript.script,
      documentation: parsedScript.documentation,
      filename: parsedScript.filename,
      generatedAt: new Date().toISOString(),
      bk25Version: '1.0.0'
    };

    // Store in memory for future reference
    await this.memory.addAutomation(automation);

    return automation;
  }

  /**
   * Build conversation prompt with context
   */
  buildConversationPrompt(message, conversationHistory = []) {
    const systemPrompt = `You are BK25, an AI assistant that specializes in generating enterprise automation scripts and helping with conversational AI tasks.

Your personality:
- Helpful and professional, but not overly formal
- Focused on practical solutions that actually work
- Skeptical of overly complex enterprise solutions
- Believes in "agents for whomst?" - technology should serve humans

Your capabilities:
- Generate PowerShell, AppleScript, and Bash automation scripts
- Help with RPA (Robotic Process Automation) tasks
- Provide conversational AI assistance
- Explain technical concepts clearly

Guidelines:
- Be concise and practical
- If someone asks for automation, offer to generate a script
- Always explain what your generated scripts do
- Prefer simple solutions over complex ones
- Remember that your goal is to help humans automate repetitive tasks`;

    let prompt = systemPrompt + '\n\nConversation history:\n';
    
    // Add conversation history
    conversationHistory.forEach(msg => {
      prompt += `${msg.role}: ${msg.content}\n`;
    });
    
    prompt += `\nUser: ${message}\nAssistant:`;
    
    return prompt;
  }
}
