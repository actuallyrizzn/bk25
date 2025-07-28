/**
 * BK25 Persona Manager
 * 
 * Handles loading and switching between different AI personas
 * Enables multi-modal experiences across web, Slack, voice, etc.
 */

import { promises as fs } from 'fs';
import path from 'path';

export class PersonaManager {
  constructor() {
    this.personas = new Map();
    this.currentPersona = null;
    this.personasPath = './personas';
  }

  /**
   * Initialize persona manager by loading all personas
   */
  async initialize() {
    try {
      await this.loadAllPersonas();
      // Set default persona
      this.currentPersona = this.personas.get('vanilla') || this.personas.get('default') || this.personas.values().next().value;
      console.log(`🎭 Persona Manager initialized with ${this.personas.size} personas`);
      console.log(`📝 Current persona: ${this.currentPersona?.name || 'None'}`);
    } catch (error) {
      console.error('Persona Manager initialization error:', error);
      // Create a fallback persona if loading fails
      this.createFallbackPersona();
    }
  }

  /**
   * Load all persona files from the personas directory
   */
  async loadAllPersonas() {
    try {
      const files = await fs.readdir(this.personasPath);
      const personaFiles = files.filter(file => file.endsWith('.json'));

      for (const file of personaFiles) {
        const filePath = path.join(this.personasPath, file);
        const personaData = await fs.readFile(filePath, 'utf8');
        const persona = JSON.parse(personaData);
        
        // Validate persona structure
        if (this.validatePersona(persona)) {
          this.personas.set(persona.id, persona);
          console.log(`✅ Loaded persona: ${persona.name} (${persona.id})`);
        } else {
          console.warn(`⚠️ Invalid persona file: ${file}`);
        }
      }
    } catch (error) {
      console.error('Error loading personas:', error);
      throw error;
    }
  }

  /**
   * Validate persona structure
   */
  validatePersona(persona) {
    const requiredFields = ['id', 'name', 'description', 'greeting', 'systemPrompt'];
    return requiredFields.every(field => persona[field]);
  }

  /**
   * Create a fallback persona if loading fails
   */
  createFallbackPersona() {
    const fallbackPersona = {
      id: 'fallback',
      name: 'BK25 Assistant',
      description: 'Default assistant persona',
      greeting: '👋 Hello! I\'m BK25, your helpful AI assistant.',
      capabilities: ['General conversation', 'Automation scripting'],
      systemPrompt: 'You are BK25, a helpful AI assistant that can generate automation scripts and provide conversational assistance.',
      examples: ['Create a PowerShell script', 'Help with automation'],
      channels: ['web']
    };
    
    this.personas.set('fallback', fallbackPersona);
    this.currentPersona = fallbackPersona;
    console.log('🔄 Using fallback persona');
  }

  /**
   * Get all available personas
   */
  getAllPersonas() {
    return Array.from(this.personas.values());
  }

  /**
   * Get personas available for a specific channel
   */
  getPersonasForChannel(channel) {
    return Array.from(this.personas.values()).filter(persona => 
      !persona.channels || persona.channels.includes(channel)
    );
  }

  /**
   * Get current persona
   */
  getCurrentPersona() {
    return this.currentPersona;
  }

  /**
   * Switch to a different persona
   */
  switchPersona(personaId) {
    const persona = this.personas.get(personaId);
    if (persona) {
      this.currentPersona = persona;
      console.log(`🎭 Switched to persona: ${persona.name} (${persona.id})`);
      return persona;
    } else {
      console.warn(`⚠️ Persona not found: ${personaId}`);
      return null;
    }
  }

  /**
   * Get persona by ID
   */
  getPersona(personaId) {
    return this.personas.get(personaId);
  }

  /**
   * Build conversation prompt using current persona
   */
  buildPersonaPrompt(message, conversationHistory = []) {
    const persona = this.currentPersona;
    if (!persona) {
      return `User: ${message}\nAssistant:`;
    }

    let prompt = persona.systemPrompt + '\n\nConversation history:\n';
    
    // Add conversation history
    conversationHistory.forEach(msg => {
      prompt += `${msg.role}: ${msg.content}\n`;
    });
    
    prompt += `\nUser: ${message}\nAssistant:`;
    
    return prompt;
  }

  /**
   * Get persona-specific greeting
   */
  getGreeting() {
    return this.currentPersona?.greeting || 'Hello! How can I help you today?';
  }

  /**
   * Get persona-specific capabilities
   */
  getCapabilities() {
    return this.currentPersona?.capabilities || ['General assistance'];
  }

  /**
   * Get persona-specific examples
   */
  getExamples() {
    return this.currentPersona?.examples || [];
  }

  /**
   * Get persona metadata for UI
   */
  getPersonaMetadata() {
    if (!this.currentPersona) return null;

    return {
      id: this.currentPersona.id,
      name: this.currentPersona.name,
      description: this.currentPersona.description,
      greeting: this.currentPersona.greeting,
      capabilities: this.currentPersona.capabilities,
      examples: this.currentPersona.examples,
      personality: this.currentPersona.personality
    };
  }

  /**
   * Reload personas from disk (useful for development)
   */
  async reloadPersonas() {
    this.personas.clear();
    await this.loadAllPersonas();
    
    // Try to maintain current persona, fallback to default
    const currentId = this.currentPersona?.id;
    if (currentId && this.personas.has(currentId)) {
      this.currentPersona = this.personas.get(currentId);
    } else {
      this.currentPersona = this.personas.get('default') || this.personas.values().next().value;
    }
    
    console.log('🔄 Personas reloaded');
  }
}
