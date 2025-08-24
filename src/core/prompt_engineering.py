"""
BK25 Prompt Engineering

Advanced prompt engineering for intelligent script generation.
Creates context-aware, persona-specific prompts for better script quality.
"""

import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

from ..logging_config import get_logger

logger = get_logger("prompt_engineering")

@dataclass
class PromptContext:
    """Context information for prompt engineering"""
    persona_id: str
    persona_name: str
    persona_description: str
    persona_capabilities: List[str]
    channel_id: str
    channel_name: str
    conversation_history: List[Dict[str, Any]]
    user_preferences: Optional[Dict[str, Any]] = None
    system_context: Optional[str] = None

@dataclass
class ScriptGenerationPrompt:
    """Structured prompt for script generation"""
    system_message: str
    user_prompt: str
    context: str
    examples: List[str]
    constraints: List[str]
    output_format: str

class PromptEngineer:
    """Advanced prompt engineering for script generation"""
    
    def __init__(self):
        self.logger = get_logger("prompt_engineer")
        
        # Base system messages for different platforms
        self.base_system_messages = {
            'powershell': """You are an expert PowerShell automation engineer. You create production-ready, enterprise-grade PowerShell scripts that follow Microsoft best practices.

Key Requirements:
- Always include proper error handling with try/catch blocks
- Use parameter validation and help documentation
- Follow PowerShell naming conventions and style guidelines
- Include Write-Host for user feedback and progress indication
- Make scripts robust and suitable for production environments
- Handle edge cases and provide meaningful error messages
- Use approved PowerShell cmdlets and avoid deprecated commands""",
            
            'applescript': """You are an expert AppleScript automation engineer. You create production-ready, user-friendly AppleScripts that follow Apple's best practices.

Key Requirements:
- Always include proper error handling with try/on error blocks
- Use display notification and display dialog for user feedback
- Check application availability before controlling them
- Follow AppleScript naming conventions and style guidelines
- Make scripts robust and suitable for production use
- Handle edge cases gracefully with user-friendly messages
- Use modern AppleScript syntax and avoid deprecated commands""",
            
            'bash': """You are an expert Bash automation engineer. You create production-ready, portable Bash scripts that follow Unix/Linux best practices.

Key Requirements:
- Always include proper error handling with set -e and trap
- Use parameter validation and help functions
- Follow Bash naming conventions and style guidelines
- Include echo statements for user feedback and progress
- Make scripts robust and suitable for production use
- Handle edge cases and provide meaningful error messages
- Use portable commands and avoid system-specific features"""
        }
        
        # Script quality constraints
        self.quality_constraints = {
            'powershell': [
                'Must include parameter validation',
                'Must use try/catch error handling',
                'Must include Write-Host for user feedback',
                'Must follow PowerShell naming conventions',
                'Must be suitable for enterprise environments'
            ],
            'applescript': [
                'Must include error handling with try/on error',
                'Must check application availability',
                'Must use display notification for feedback',
                'Must follow AppleScript conventions',
                'Must be user-friendly and robust'
            ],
            'bash': [
                'Must include set -e and trap for error handling',
                'Must validate parameters and provide help',
                'Must use echo for user feedback',
                'Must follow Bash conventions',
                'Must be portable and robust'
            ]
        }
        
        # Output format specifications
        self.output_formats = {
            'powershell': """Generate only the PowerShell script code. Do not include markdown formatting, explanations, or additional text. The output should be a complete, executable PowerShell script that can be saved directly to a .ps1 file.""",
            'applescript': """Generate only the AppleScript code. Do not include markdown formatting, explanations, or additional text. The output should be a complete, executable AppleScript that can be saved directly to a .scpt file.""",
            'bash': """Generate only the Bash script code. Do not include markdown formatting, explanations, or additional text. The output should be a complete, executable Bash script that can be saved directly to a .sh file."""
        }
    
    def create_script_generation_prompt(
        self,
        description: str,
        platform: str,
        context: PromptContext,
        options: Optional[Dict[str, Any]] = None
    ) -> ScriptGenerationPrompt:
        """Create a comprehensive prompt for script generation"""
        
        # Get base system message for the platform
        system_message = self.base_system_messages.get(platform, self.base_system_messages['bash'])
        
        # Build context-aware system message
        enhanced_system_message = self._enhance_system_message(system_message, context, platform)
        
        # Build user prompt with requirements
        user_prompt = self._build_user_prompt(description, platform, options)
        
        # Build context information
        context_info = self._build_context_info(context, platform)
        
        # Get relevant examples
        examples = self._get_relevant_examples(description, platform)
        
        # Get quality constraints
        constraints = self.quality_constraints.get(platform, [])
        
        # Get output format specification
        output_format = self.output_formats.get(platform, self.output_formats['bash'])
        
        return ScriptGenerationPrompt(
            system_message=enhanced_system_message,
            user_prompt=user_prompt,
            context=context_info,
            examples=examples,
            constraints=constraints,
            output_format=output_format
        )
    
    def _enhance_system_message(self, base_message: str, context: PromptContext, platform: str) -> str:
        """Enhance system message with persona and context information"""
        enhancements = []
        
        # Add persona-specific enhancements
        if context.persona_capabilities:
            capabilities = ', '.join(context.persona_capabilities)
            enhancements.append(f"Persona: {context.persona_name} - {context.persona_description}")
            enhancements.append(f"Capabilities: {capabilities}")
        
        # Add channel-specific enhancements
        if context.channel_id != 'web':
            enhancements.append(f"Channel: {context.channel_name} - Adapt output for {context.channel_id} communication")
        
        # Add conversation context if available
        if context.conversation_history:
            recent_messages = context.conversation_history[-3:]  # Last 3 messages
            context_summary = self._summarize_conversation_context(recent_messages)
            if context_summary:
                enhancements.append(f"Conversation Context: {context_summary}")
        
        # Add user preferences if available
        if context.user_preferences:
            prefs = []
            if context.user_preferences.get('verbose'):
                prefs.append("prefer verbose output with detailed comments")
            if context.user_preferences.get('minimal'):
                prefs.append("prefer minimal, concise code")
            if context.user_preferences.get('enterprise'):
                prefs.append("focus on enterprise-grade security and compliance")
            
            if prefs:
                enhancements.append(f"User Preferences: {', '.join(prefs)}")
        
        # Combine base message with enhancements
        if enhancements:
            enhanced_message = base_message + "\n\nAdditional Context:\n" + "\n".join(f"- {enh}" for enh in enhancements)
        else:
            enhanced_message = base_message
        
        return enhanced_message
    
    def _build_user_prompt(self, description: str, platform: str, options: Optional[Dict[str, Any]]) -> str:
        """Build the user prompt with specific requirements"""
        prompt_parts = [f"Create a {platform} script for: {description}"]
        
        # Add specific requirements based on options
        if options:
            if options.get('include_tests'):
                prompt_parts.append("Include unit tests or validation checks")
            
            if options.get('include_documentation'):
                prompt_parts.append("Include comprehensive inline documentation")
            
            if options.get('include_logging'):
                prompt_parts.append("Include logging and audit trail functionality")
            
            if options.get('include_error_handling'):
                prompt_parts.append("Include robust error handling and recovery")
            
            if options.get('include_parameter_validation'):
                prompt_parts.append("Include comprehensive parameter validation")
            
            if options.get('include_help'):
                prompt_parts.append("Include detailed help and usage information")
            
            if options.get('include_examples'):
                prompt_parts.append("Include usage examples in comments")
        
        # Add platform-specific requirements
        if platform == 'powershell':
            prompt_parts.append("Ensure the script follows PowerShell execution policy best practices")
        elif platform == 'applescript':
            prompt_parts.append("Ensure the script provides clear user feedback and handles errors gracefully")
        elif platform == 'bash':
            prompt_parts.append("Ensure the script is portable and handles different Unix/Linux environments")
        
        return "\n".join(prompt_parts)
    
    def _build_context_info(self, context: PromptContext, platform: str) -> str:
        """Build context information for the prompt"""
        context_parts = []
        
        # Add persona information
        context_parts.append(f"Persona: {context.persona_name}")
        context_parts.append(f"Description: {context.persona_description}")
        
        # Add channel information
        context_parts.append(f"Channel: {context.channel_name}")
        
        # Add system context if available
        if context.system_context:
            context_parts.append(f"System Context: {context.system_context}")
        
        # Add conversation context if available
        if context.conversation_history:
            context_parts.append(f"Recent Conversation: {len(context.conversation_history)} messages available")
        
        return "\n".join(context_parts)
    
    def _get_relevant_examples(self, description: str, platform: str) -> List[str]:
        """Get relevant examples based on description and platform"""
        # This could be expanded to include actual example scripts
        # For now, return general guidance
        examples = []
        
        if 'file' in description.lower() and 'process' in description.lower():
            examples.append("File processing examples available for reference")
        
        if 'system' in description.lower() and 'monitor' in description.lower():
            examples.append("System monitoring examples available for reference")
        
        if 'backup' in description.lower():
            examples.append("Backup automation examples available for reference")
        
        if 'email' in description.lower():
            examples.append("Email automation examples available for reference")
        
        return examples
    
    def _summarize_conversation_context(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize conversation context for prompt enhancement"""
        if not messages:
            return ""
        
        # Extract key information from recent messages
        summary_parts = []
        
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # First 100 chars
            
            if role == 'user':
                summary_parts.append(f"User requested: {content}...")
            elif role == 'assistant':
                summary_parts.append(f"Assistant provided: {content}...")
        
        return " | ".join(summary_parts)
    
    def create_iterative_improvement_prompt(
        self,
        original_script: str,
        feedback: str,
        platform: str,
        context: PromptContext
    ) -> ScriptGenerationPrompt:
        """Create a prompt for iterative script improvement"""
        
        system_message = f"""You are an expert {platform} automation engineer tasked with improving an existing script based on user feedback.

Your task is to:
1. Analyze the existing script
2. Understand the user's feedback and requirements
3. Improve the script while maintaining its core functionality
4. Ensure all improvements follow {platform} best practices
5. Provide a complete, improved version of the script

Focus on addressing the specific feedback while maintaining or improving code quality."""
        
        user_prompt = f"""Improve the following {platform} script based on this feedback:

FEEDBACK: {feedback}

ORIGINAL SCRIPT:
{original_script}

Please provide an improved version that addresses the feedback while maintaining the script's core functionality."""
        
        context_info = self._build_context_info(context, platform)
        
        return ScriptGenerationPrompt(
            system_message=system_message,
            user_prompt=user_prompt,
            context=context_info,
            examples=[],
            constraints=self.quality_constraints.get(platform, []),
            output_format=self.output_formats.get(platform, self.output_formats['bash'])
        )
    
    def create_validation_prompt(
        self,
        script: str,
        platform: str,
        context: PromptContext
    ) -> ScriptGenerationPrompt:
        """Create a prompt for script validation and improvement suggestions"""
        
        system_message = f"""You are an expert {platform} code reviewer and automation engineer. Your task is to analyze the provided script and provide:

1. A validation score (1-10)
2. Specific issues found
3. Improvement suggestions
4. Security considerations
5. Best practice recommendations

Be thorough but constructive in your feedback."""
        
        user_prompt = f"""Please review and validate this {platform} script:

{script}

Provide a comprehensive analysis including validation score, issues, improvements, and recommendations."""
        
        context_info = self._build_context_info(context, platform)
        
        return ScriptGenerationPrompt(
            system_message=system_message,
            user_prompt=user_prompt,
            context=context_info,
            examples=[],
            constraints=[],
            output_format="Provide your analysis in a structured format with clear sections for each aspect of the review."
        )
