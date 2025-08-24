"""
Web Channel Module

Provides web-specific artifact generation using HTML/CSS/JS.
Handles web interface components and interactive elements.
"""

from typing import Dict, List, Optional, Any, Union
from .base import BaseChannel, ArtifactRequest, ArtifactResult

class WebChannel(BaseChannel):
    """Web channel with HTML/CSS/JS support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            config = {}
        
        super().__init__({
            'name': 'Web Interface',
            'id': 'web',
            'capabilities': ['rich_text', 'file_upload', 'real_time', 'custom_ui'],
            'artifact_types': ['html', 'css', 'javascript', 'json'],
            'metadata': {'color': '#007bff', 'icon': '🌐'}
        })
    
    def generate_artifact(self, request: ArtifactRequest) -> ArtifactResult:
        """Generate web-specific artifacts"""
        try:
            if request.type == 'html':
                return self._generate_html(request.content, request.options)
            elif request.type == 'css':
                return self._generate_css(request.content, request.options)
            elif request.type == 'javascript':
                return self._generate_javascript(request.content, request.options)
            elif request.type == 'json':
                return self._generate_json(request.content, request.options)
            else:
                return ArtifactResult(
                    success=False,
                    error=f"Unsupported artifact type: {request.type}"
                )
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"Artifact generation failed: {str(e)}"
            )
    
    def _generate_html(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate HTML content"""
        try:
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.get('title', 'BK25 Response')}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{content.get('title', 'BK25 Response')}</h1>
        </header>
        <main>
            <div class="content">
                {content.get('text', '')}
            </div>
            {self._generate_html_code_block(content)}
            {self._generate_html_actions(content)}
        </main>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
            
            return ArtifactResult(
                success=True,
                artifact=html,
                formatted_content=html,
                metadata={'platform': 'web', 'type': 'html'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"HTML generation failed: {str(e)}"
            )
    
    def _generate_html_code_block(self, content: Any) -> str:
        """Generate HTML code block"""
        if not content.get('code'):
            return ""
        
        language = content.get('language', 'text')
        return f"""
            <div class="code-block">
                <h3>Generated Code:</h3>
                <pre><code class="language-{language}">{content['code']}</code></pre>
            </div>"""
    
    def _generate_html_actions(self, content: Any) -> str:
        """Generate HTML action buttons"""
        if not content.get('actions'):
            return ""
        
        buttons = ""
        for action in content['actions']:
            buttons += f'<button class="btn btn-primary" onclick="{action.get("onclick", "")}">{action.get("label", "Action")}</button>'
        
        return f"""
            <div class="actions">
                {buttons}
            </div>"""
    
    def _generate_css(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate CSS content"""
        try:
            css = f"""/* BK25 Generated Styles */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

header {{
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #007bff;
}}

.content {{
    line-height: 1.6;
    margin-bottom: 30px;
}}

.code-block {{
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 5px;
    padding: 20px;
    margin: 20px 0;
}}

.code-block pre {{
    margin: 0;
    overflow-x: auto;
}}

.actions {{
    text-align: center;
    margin-top: 30px;
}}

.btn {{
    display: inline-block;
    padding: 10px 20px;
    margin: 0 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
    font-size: 16px;
}}

.btn-primary {{
    background-color: #007bff;
    color: white;
}}

.btn-primary:hover {{
    background-color: #0056b3;
}}"""
            
            return ArtifactResult(
                success=True,
                artifact=css,
                formatted_content=css,
                metadata={'platform': 'web', 'type': 'css'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"CSS generation failed: {str(e)}"
            )
    
    def _generate_javascript(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate JavaScript content"""
        try:
            js = f"""// BK25 Generated JavaScript
document.addEventListener('DOMContentLoaded', function() {{
    console.log('BK25 Web Interface loaded');
    
    // Initialize interactive elements
    initializeActions();
    
    // Add any custom functionality
    {content.get('custom_js', '')}
}});

function initializeActions() {{
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {{
        button.addEventListener('click', function(e) {{
            console.log('Button clicked:', e.target.textContent);
            // Add custom button handling here
        }});
    }});
}}

// Utility functions
function showMessage(message, type = 'info') {{
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${{type}}`;
    messageDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    setTimeout(() => {{
        messageDiv.remove();
    }}, 5000);
}}"""
            
            return ArtifactResult(
                success=True,
                artifact=js,
                formatted_content=js,
                metadata={'platform': 'web', 'type': 'javascript'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"JavaScript generation failed: {str(e)}"
            )
    
    def _generate_json(self, content: Any, options: Optional[Dict[str, Any]] = None) -> ArtifactResult:
        """Generate JSON content"""
        try:
            import json
            json_content = {
                'title': content.get('title', 'BK25 Response'),
                'text': content.get('text', ''),
                'code': content.get('code'),
                'actions': content.get('actions', []),
                'metadata': {
                    'platform': 'web',
                    'generated_by': 'BK25',
                    'timestamp': content.get('timestamp', '')
                }
            }
            
            formatted_json = json.dumps(json_content, indent=2)
            
            return ArtifactResult(
                success=True,
                artifact=json_content,
                formatted_content=formatted_json,
                metadata={'platform': 'web', 'type': 'json'}
            )
            
        except Exception as e:
            return ArtifactResult(
                success=False,
                error=f"JSON generation failed: {str(e)}"
            )
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against web constraints"""
        constraints = self.get_constraints()
        
        # Web has no practical character limit
        max_length = 100000
        is_valid = len(message) <= max_length
        
        return {
            'valid': is_valid,
            'length': len(message),
            'max_length': max_length,
            'truncated': message[:max_length] if not is_valid else message,
            'constraints': constraints
        }
    
    def format_response(self, response: Any) -> str:
        """Format response for web"""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            if 'title' in response:
                return f"Web Response: {response['title']}"
            else:
                return str(response)
        
        return str(response)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get web-specific constraints"""
        return {
            'max_message_length': 100000,
            'supports_rich_text': True,
            'supports_media': True,
            'supports_interactive': True,
            'supports_html': True,
            'supports_css': True,
            'supports_javascript': True,
            'supports_custom_ui': True
        }
