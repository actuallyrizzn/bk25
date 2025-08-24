from bk25.generators import PowerShellGenerator, AppleScriptGenerator, BashGenerator


def test_powershell_parse_generates_filename_and_docs():
    gen = PowerShellGenerator()
    text = """
```powershell
<#
.SYNOPSIS
    Example Synopsis
#>
Write-Host "hi"
```
"""
    parsed = gen.parse_generated_script(text)
    assert parsed["script"].startswith("# Run with:")
    assert parsed["filename"].endswith(".ps1")
    assert "Example Synopsis" in parsed["documentation"]


def test_applescript_parse_handles_comments_and_filename():
    gen = AppleScriptGenerator()
    text = """
```applescript
-- Script Name: Demo Name
display notification "hi"
```
"""
    parsed = gen.parse_generated_script(text)
    assert parsed["filename"].startswith("demo-name")
    assert "display notification" in parsed["script"]


def test_bash_parse_adds_shebang_and_exec_note():
    gen = BashGenerator()
    text = """
```bash
echo hi
```
"""
    parsed = gen.parse_generated_script(text)
    assert parsed["script"].startswith("#!/bin/bash")
    assert ".sh" in parsed["filename"]
