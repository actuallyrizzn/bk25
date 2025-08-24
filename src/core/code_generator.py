"""
BK25 Code Generator

Main orchestrator for all script generation capabilities.
Integrates PowerShell, AppleScript, and Bash generators.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass

from ..logging_config import get_logger
from ..generators.powershell import PowerShellGenerator
from ..generators.applescript import AppleScriptGenerator
from ..generators.bash import BashGenerator

logger = get_logger("code_generator")

@dataclass
class GenerationRequest:
    """Script generation request"""
    description: str
    platform: str  # 'powershell', 'applescript', 'bash', 'auto'
    options: Optional[Dict[str, Any]] = None
    persona_id: Optional[str] = None
    channel: Optional[str] = None

@dataclass
class GenerationResult:
    """Script generation result"""
    success: bool
    script: Optional[str] = None
    filename: Optional[str] = None
    documentation: Optional[str] = None
    validation: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CodeGenerator:
    """Main code generation orchestrator"""
    
    def __init__(self):
        self.logger = get_logger("code_generator")
        
        # Initialize all generators
        self.generators = {
            'powershell': PowerShellGenerator(),
            'applescript': AppleScriptGenerator(),
            'bash': BashGenerator()
        }
        
        # Platform detection hints
        self.platform_hints = {
            'windows': 'powershell',
            'macos': 'applescript',
            'linux': 'bash',
            'unix': 'bash'
        }
        
        # Common automation patterns
        self.automation_patterns = {
            'file_processing': ['powershell', 'bash', 'applescript'],
            'system_monitoring': ['bash', 'powershell'],
            'backup_automation': ['bash', 'powershell'],
            'email_automation': ['powershell', 'bash'],
            'active_directory': ['powershell'],
            'mac_automation': ['applescript'],
            'linux_admin': ['bash'],
            'cross_platform': ['bash', 'powershell']
        }
        
        self.logger.info("[INIT] Code Generator initialized with all platforms")
    
    async def generate_script(self, request: GenerationRequest, llm_manager: Optional[Any] = None, prompt_engineer: Optional[Any] = None) -> GenerationResult:
        """Generate a script based on the request"""
        try:
            self.logger.info(f"[GENERATE] Generating {request.platform} script for: {request.description[:50]}...")
            
            # Determine platform if auto-detection is requested
            platform = await self._determine_platform(request)
            
            # Get the appropriate generator
            generator = self.generators.get(platform)
            if not generator:
                return GenerationResult(
                    success=False,
                    error=f"Unsupported platform: {platform}"
                )
            
            # Try LLM generation first if available
            if llm_manager and prompt_engineer:
                try:
                    result = await self._generate_with_llm(generator, request, llm_manager, prompt_engineer)
                    if result.success:
                        self.logger.info(f"[SUCCESS] LLM script generation completed for {platform}")
                        # Validate the generated script
                        validation = generator.validate_script(result.script)
                        result.validation = validation
                        return result
                except Exception as error:
                    self.logger.warning(f"LLM generation failed, falling back to template: {error}")
            
            # Fall back to template-based generation
            result = await self._generate_from_template(generator, request)
            
            # Validate the generated script
            if result.success and result.script:
                validation = generator.validate_script(result.script)
                result.validation = validation
                
                # Update success based on validation
                if not validation.is_valid:
                    result.success = False
                    result.error = f"Script validation failed: {', '.join(validation.issues)}"
            
            self.logger.info(f"[SUCCESS] Template-based script generation completed for {platform}")
            return result
            
        except Exception as error:
            self.logger.error(f"[ERROR] Script generation failed: {error}")
            return GenerationResult(
                success=False,
                error=f"Generation error: {str(error)}"
            )
    
    async def _determine_platform(self, request: GenerationRequest) -> str:
        """Determine the best platform for the request"""
        if request.platform != 'auto':
            return request.platform
        
        # Auto-detect based on description and context
        description_lower = request.description.lower()
        
        # Check for platform-specific keywords
        if any(keyword in description_lower for keyword in ['windows', 'active directory', 'powershell', 'exchange', 'office 365']):
            return 'powershell'
        
        if any(keyword in description_lower for keyword in ['mac', 'macos', 'finder', 'safari', 'system preferences']):
            return 'applescript'
        
        if any(keyword in description_lower for keyword in ['linux', 'unix', 'bash', 'systemctl', 'apt', 'yum']):
            return 'bash'
        
        # Check for automation patterns
        for pattern, platforms in self.automation_patterns.items():
            if pattern.replace('_', ' ') in description_lower:
                # Return the first platform that's most appropriate
                return platforms[0]
        
        # Default to bash for cross-platform compatibility
        return 'bash'
    
    async def _generate_from_template(self, generator: Any, request: GenerationRequest) -> GenerationResult:
        """Generate script from template (placeholder for LLM integration)"""
        try:
            # Get available templates
            templates = generator.get_templates()
            
            # Find the best matching template
            best_template = None
            best_score = 0
            
            for template_name, template_data in templates.items():
                score = self._calculate_template_match_score(request.description, template_data['description'])
                if score > best_score:
                    best_score = score
                    best_template = template_data
            
            if best_template and best_score > 0.3:  # Threshold for template matching
                # Use the template as a base
                script = best_template['template']
                
                # Parse the generated script
                parsed = generator.parse_generated_script(script)
                
                return GenerationResult(
                    success=True,
                    script=parsed['script'],
                    filename=parsed['filename'],
                    documentation=parsed['documentation'],
                    metadata={
                        'template_used': list(templates.keys())[list(templates.values()).index(best_template)],
                        'match_score': best_score,
                        'generator': generator.platform
                    }
                )
            else:
                # Create a basic script structure
                basic_script = self._create_basic_script(generator, request.description)
                parsed = generator.parse_generated_script(basic_script)
                
                return GenerationResult(
                    success=True,
                    script=parsed['script'],
                    filename=parsed['filename'],
                    documentation=parsed['documentation'],
                    metadata={
                        'template_used': 'basic_structure',
                        'match_score': 0,
                        'generator': generator.platform
                    }
                )
                
        except Exception as error:
            self.logger.error(f"Template generation failed: {error}")
            return GenerationResult(
                success=False,
                error=f"Template generation error: {str(error)}"
            )
    
    async def _generate_with_llm(self, generator: Any, request: GenerationRequest, llm_manager: Any, prompt_engineer: Any) -> GenerationResult:
        """Generate script using LLM with advanced prompt engineering"""
        try:
            # Create prompt context
            context = self._create_prompt_context(request)
            
            # Create structured prompt
            prompt = prompt_engineer.create_script_generation_prompt(
                description=request.description,
                platform=generator.platform,
                context=context,
                options=request.options
            )
            
            # Build the full prompt for LLM
            full_prompt = f"{prompt.system_message}\n\n{prompt.user_prompt}\n\n{prompt.output_format}"
            
            # Generate with LLM
            from ..core.llm_integration import LLMRequest
            
            llm_request = LLMRequest(
                prompt=full_prompt,
                model=llm_manager.config.get('model', 'default'),
                temperature=0.1,  # Low temperature for consistent code generation
                max_tokens=request.options.get('max_tokens', 2048) if request.options else 2048,
                system_message=prompt.system_message
            )
            
            self.logger.info(f"Generating {generator.platform} script with LLM...")
            llm_response = await llm_manager.generate(llm_request)
            
            if not llm_response.success:
                self.logger.warning(f"LLM generation failed, falling back to template: {llm_response.error}")
                return await self._generate_from_template(generator, request)
            
            # Parse the LLM-generated script
            script = llm_response.content
            parsed = generator.parse_generated_script(script)
            
            return GenerationResult(
                success=True,
                script=parsed['script'],
                filename=parsed['filename'],
                documentation=parsed['documentation'],
                metadata={
                    'generation_method': 'llm',
                    'provider': llm_response.metadata.get('provider', 'unknown'),
                    'model': llm_response.metadata.get('model', 'unknown'),
                    'usage': llm_response.usage,
                    'generator': generator.platform
                }
            )
            
        except Exception as error:
            self.logger.error(f"LLM generation failed: {error}")
            # Fall back to template generation
            return await self._generate_from_template(generator, request)
    
    def _create_prompt_context(self, request: GenerationRequest) -> Any:
        """Create prompt context from generation request"""
        from ..core.prompt_engineering import PromptContext
        
        # This would typically get real data from the BK25 system
        # For now, create a basic context
        return PromptContext(
            persona_id=request.persona_id or 'default',
            persona_name='Default Persona',
            persona_description='General automation expert',
            persona_capabilities=['script_generation', 'automation'],
            channel_id=request.channel or 'web',
            channel_name='Web Interface',
            conversation_history=[],
            user_preferences=request.options.get('preferences') if request.options else None
        )
    
    def _calculate_template_match_score(self, description: str, template_desc: str) -> float:
        """Calculate how well a template matches the description"""
        desc_words = set(description.lower().split())
        template_words = set(template_desc.lower().split())
        
        if not desc_words or not template_words:
            return 0.0
        
        intersection = desc_words.intersection(template_words)
        union = desc_words.union(template_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _create_basic_script(self, generator: Any, description: str) -> str:
        """Create a basic script structure when no template matches"""
        if generator.platform == 'powershell':
            return f'''# PowerShell: {description}
# Generated by BK25 - Enterprise automation without enterprise complexity

param(
    [Parameter(Mandatory=$false)]
    [string]$Verbose = $false
)

try {{
    Write-Host "Starting automation: {description}" -ForegroundColor Green
    
    # TODO: Implement automation logic here
    # {description}
    
    Write-Host "Automation completed successfully!" -ForegroundColor Green
    
}} catch {{
    Write-Error "Automation failed: $($_.Exception.Message)"
    exit 1
}}'''
        
        elif generator.platform == 'applescript':
            return f'''#!/usr/bin/osascript

-- AppleScript: {description}
-- Generated by BK25 - Enterprise automation without enterprise complexity

on run
    try
        display notification "Starting automation..." with title "BK25"
        
        -- TODO: Implement automation logic here
        -- {description}
        
        display notification "Automation completed successfully!" with title "BK25"
        
    on error errorMessage
        display dialog "Automation failed: " & errorMessage buttons {{"OK"}} default button "OK" with icon stop
        return false
    end try
    
    return true
end run'''
        
        else:  # bash
            return f'''#!/bin/bash

# Bash: {description}
# Generated by BK25 - Enterprise automation without enterprise complexity

set -e
set -u

# Colors for output
GREEN='\\033[0;32m'
RED='\\033[0;31m'
NC='\\033[0m'

print_status() {{
    echo -e "${{GREEN}}[INFO]${{NC}} $1"
}}

print_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

# Error handling
trap 'print_error "Error occurred. Cleaning up..."; exit 1' ERR

main() {{
    print_status "Starting automation: {description}"
    
    # TODO: Implement automation logic here
    # {description}
    
    print_status "Automation completed successfully!"
}}

main "$@"'''
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return list(self.generators.keys())
    
    def get_platform_info(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific platform"""
        generator = self.generators.get(platform)
        if not generator:
            return None
        
        return {
            'platform': generator.platform,
            'file_extension': generator.file_extension,
            'templates': list(generator.get_templates().keys()),
            'common_commands': getattr(generator, 'get_common_cmdlets', lambda: {})(),
            'common_applications': getattr(generator, 'get_common_applications', lambda: {})(),
            'common_commands_bash': getattr(generator, 'get_common_commands', lambda: {})()
        }
    
    def get_automation_suggestions(self, description: str) -> List[Dict[str, Any]]:
        """Get automation suggestions based on description"""
        suggestions = []
        
        # Check for common automation patterns
        for pattern, platforms in self.automation_patterns.items():
            if pattern.replace('_', ' ') in description.lower():
                suggestions.append({
                    'pattern': pattern,
                    'platforms': platforms,
                    'description': f"Detected {pattern.replace('_', ' ')} pattern",
                    'recommended_platform': platforms[0]
                })
        
        # Add platform-specific suggestions
        if 'windows' in description.lower() or 'active directory' in description.lower():
            suggestions.append({
                'pattern': 'windows_enterprise',
                'platforms': ['powershell'],
                'description': 'Windows enterprise environment detected',
                'recommended_platform': 'powershell'
            })
        
        if 'mac' in description.lower() or 'macos' in description.lower():
            suggestions.append({
                'pattern': 'mac_automation',
                'platforms': ['applescript'],
                'description': 'macOS automation detected',
                'recommended_platform': 'applescript'
            })
        
        if 'linux' in description.lower() or 'unix' in description.lower():
            suggestions.append({
                'pattern': 'linux_unix',
                'platforms': ['bash'],
                'description': 'Linux/Unix environment detected',
                'recommended_platform': 'bash'
            })
        
        return suggestions
    
    async def batch_generate(self, requests: List[GenerationRequest]) -> List[GenerationResult]:
        """Generate multiple scripts in batch"""
        self.logger.info(f"[BATCH] Starting batch generation of {len(requests)} scripts")
        
        tasks = [self.generate_script(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(GenerationResult(
                    success=False,
                    error=f"Batch generation error for request {i}: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        self.logger.info(f"[SUCCESS] Batch generation completed: {len([r for r in processed_results if r.success])}/{len(requests)} successful")
        return processed_results
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about code generation capabilities"""
        stats = {
            'total_platforms': len(self.generators),
            'platforms': {},
            'total_templates': 0,
            'automation_patterns': len(self.automation_patterns)
        }
        
        for platform, generator in self.generators.items():
            templates = generator.get_templates()
            stats['platforms'][platform] = {
                'templates': len(templates),
                'file_extension': generator.file_extension,
                'template_names': list(templates.keys())
            }
            stats['total_templates'] += len(templates)
        
        return stats
