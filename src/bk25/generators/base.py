"""
Base Generator Class

Abstract base class for all code generators in BK25.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import re


class BaseGenerator(ABC):
    """Abstract base class for code generators"""
    
    def __init__(self, platform: str, file_extension: str):
        self.platform = platform
        self.file_extension = file_extension
    
    @abstractmethod
    def build_generation_prompt(self, description: str, options: Dict[str, Any] = None) -> str:
        """Build generation prompt for the specific platform"""
        pass
    
    @abstractmethod
    def parse_generated_script(self, generated_text: str) -> Dict[str, Any]:
        """Parse generated script and extract components"""
        pass
    
    @abstractmethod
    def cleanup_script(self, script: str) -> str:
        """Clean up generated script"""
        pass
    
    @abstractmethod
    def extract_documentation(self, script: str) -> str:
        """Extract documentation from script"""
        pass
    
    def generate_filename(self, script: str) -> str:
        """Generate appropriate filename for the script"""
        # Try to extract script name from comments
        lines = script.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['script name:', 'name:', 'title:']):
                # Extract name after the keyword
                name_match = re.search(r'(?:script name|name|title):\s*([^#\n]+)', line, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    # Clean up name for filename
                    name = re.sub(r'[^\w\s-]', '', name)
                    name = re.sub(r'\s+', '_', name)
                    if name:
                        return f"{name.lower()}{self.file_extension}"
        
        # Fallback to platform-specific default
        return f"{self.platform}_automation{self.file_extension}"
    
    def extract_code_block(self, text: str, language: str = None) -> str:
        """Extract code block from markdown-style text"""
        if language:
            pattern = f"```{language}\\s*([\\s\\S]*?)```"
        else:
            pattern = r"```(?:\w+)?\s*([\s\S]*?)```"
        
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else text.strip()
    
    def clean_line_endings(self, script: str) -> str:
        """Normalize line endings"""
        return script.replace('\r\n', '\n').replace('\r', '\n')
    
    def validate_script_syntax(self, script: str) -> bool:
        """Basic syntax validation (to be overridden by specific generators)"""
        return len(script.strip()) > 0