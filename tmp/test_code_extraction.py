#!/usr/bin/env python3
"""
Test script to debug code block extraction from BK25 server responses.
This will help us get the regex working perfectly before implementing it in the frontend.
"""

import requests
import json
import re
import time

# Server configuration (from your screenshot)
SERVER_URL = "http://localhost:3003"
API_KEY = "sk-..."  # Your OpenAI API key from the screenshot

def test_code_extraction():
    """Test the code block extraction regex with real server responses."""
    
    print("🔧 Testing Code Block Extraction")
    print("=" * 50)
    
    # Test message that should generate code
    test_message = "Write a PowerShell script that lists all running Windows services and saves the output to a CSV file. Include the service name, display name, status, and startup type."
    
    print(f"📝 Test message: {test_message}")
    print(f"🌐 Server: {SERVER_URL}")
    print()
    
    try:
        # Send request to the chat endpoint
        print("📤 Sending request to /api/chat...")
        
        response = requests.post(
            f"{SERVER_URL}/api/chat",
            json={
                "message": test_message,
                "conversation_id": "test_conversation",
                "persona_id": "technical-expert",
                "channel_id": "web",
                "context": {
                    "platform": "powershell"
                }
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Server error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        print("✅ Response received successfully!")
        print()
        
        # Check if we have extracted_code from backend
        if "extracted_code" in data and data["extracted_code"] is not None:
            print("🎯 Backend already extracted code blocks:")
            print(f"   Language: {data['extracted_code'].get('language', 'unknown')}")
            print(f"   Code length: {len(data['extracted_code'].get('code', ''))}")
            print(f"   Filename: {data['extracted_code'].get('filename', 'unknown')}")
            print()
        else:
            print("ℹ️ No extracted_code from backend")
            print()
        
        # Get the full response text
        response_text = data.get("response", data.get("message", ""))
        print(f"📄 Full response length: {len(response_text)} characters")
        print(f"📄 Response preview: {response_text[:200]}...")
        print()
        
        # Test our regex patterns
        test_regex_patterns(response_text)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_regex_patterns(text):
    """Test different regex patterns to find the best one for code block extraction."""
    
    print("🔍 Testing Regex Patterns")
    print("-" * 30)
    
    # Pattern 1: Basic code block detection
    pattern1 = r'```(\w+)?\n([\s\S]*?)```'
    print(f"Pattern 1: {pattern1}")
    matches1 = re.findall(pattern1, text)
    print(f"   Matches found: {len(matches1)}")
    for i, (lang, code) in enumerate(matches1):
        print(f"   Match {i+1}: language='{lang or 'none'}', code_length={len(code)}")
        print(f"   Code preview: {code[:100]}...")
    print()
    
    # Pattern 2: More flexible language detection
    pattern2 = r'```(?:(\w+)\s*\n)?([\s\S]*?)```'
    print(f"Pattern 2: {pattern2}")
    matches2 = re.findall(pattern2, text)
    print(f"   Matches found: {len(matches2)}")
    for i, (lang, code) in enumerate(matches2):
        print(f"   Match {i+1}: language='{lang or 'none'}', code_length={len(code)}")
        print(f"   Code preview: {code[:100]}...")
    print()
    
    # Pattern 3: Handle edge cases
    pattern3 = r'```(?:(\w+)\s*\n)?([\s\S]*?)```'
    print(f"Pattern 3: {pattern3}")
    matches3 = re.findall(pattern3, text)
    print(f"   Matches found: {len(matches3)}")
    for i, (lang, code) in enumerate(matches3):
        print(f"   Match {i+1}: language='{lang or 'none'}', code_length={len(code)}")
        print(f"   Code preview: {code[:100]}...")
    print()
    
    # Test replacement
    print("🔄 Testing Replacement")
    print("-" * 20)
    
    # Use the best pattern (pattern2) for replacement
    replacement_text = re.sub(pattern2, create_replacement_indicator, text)
    
    print(f"Original length: {len(text)}")
    print(f"Replaced length: {len(replacement_text)}")
    print(f"Replacement preview: {replacement_text[:300]}...")
    
    # Count code blocks in original
    code_block_count = text.count('```') // 2
    print(f"Code blocks in original: {code_block_count}")
    
    # Count indicators in replaced text
    indicator_count = replacement_text.count('script generated!')
    print(f"Indicators in replaced: {indicator_count}")
    
    if code_block_count == indicator_count:
        print("✅ SUCCESS: All code blocks replaced correctly!")
    else:
        print(f"❌ MISMATCH: Expected {code_block_count} replacements, got {indicator_count}")

def create_replacement_indicator(match):
    """Create the replacement indicator for code blocks."""
    language = match.group(1) or 'script'
    return f'<div class="mt-2 p-2 bg-info bg-opacity-10 rounded border border-info"><div class="d-flex align-items-center text-info"><i class="bi bi-code-slash me-2"></i><span class="small">→ <strong>{language.upper()}</strong> script generated! Check the output panel to the right.</span></div></div>'

def test_manual_extraction(text):
    """Test manual string replacement as a fallback."""
    
    print("\n🔧 Testing Manual String Replacement")
    print("-" * 40)
    
    # Simple manual replacement
    manual_text = text
    replacement_count = 0
    
    while '```' in manual_text:
        start_idx = manual_text.find('```')
        end_idx = manual_text.find('```', start_idx + 3)
        
        if end_idx == -1:
            break
            
        # Extract the code section
        code_section = manual_text[start_idx:end_idx + 3]
        
        # Try to extract language from first line
        lines = code_section.split('\n')
        if len(lines) > 1:
            first_line = lines[1].strip()
            language = first_line if first_line and first_line.isalpha() else 'script'
        else:
            language = 'script'
        
        # Create replacement
        replacement = f'<div class="mt-2 p-2 bg-info bg-opacity-10 rounded border border-info"><div class="d-flex align-items-center text-info"><i class="bi bi-code-slash me-2"></i><span class="small">→ <strong>{language.upper()}</strong> script generated! Check the output panel to the right.</span></div></div>'
        
        # Replace
        manual_text = manual_text[:start_idx] + replacement + manual_text[end_idx + 3:]
        replacement_count += 1
    
    print(f"Manual replacements: {replacement_count}")
    print(f"Final text length: {len(manual_text)}")
    print(f"Final text preview: {manual_text[:300]}...")

if __name__ == "__main__":
    print("🚀 BK25 Code Block Extraction Test")
    print("=" * 50)
    print()
    
    # Test the server
    test_code_extraction()
    
    print("\n" + "=" * 50)
    print("�� Test completed!")
