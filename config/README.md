# BK25 Configuration

## ⚠️ SECURITY WARNING ⚠️

**NEVER commit API keys or sensitive configuration to git!**

This directory contains configuration files that may contain sensitive information like API keys. These files are automatically ignored by git to prevent accidental exposure.

## Setup Instructions

1. **Copy the example file:**
   ```bash
   cp bk25_config.json.example bk25_config.json
   ```

2. **Edit the config file with your actual API keys:**
   ```bash
   # Edit the file and replace placeholder values
   nano bk25_config.json  # or use your preferred editor
   ```

3. **Replace placeholder values:**
   - `YOUR_OPENAI_API_KEY_HERE` → Your actual OpenAI API key
   - `YOUR_ANTHROPIC_API_KEY_HERE` → Your actual Anthropic API key
   - `YOUR_GOOGLE_API_KEY_HERE` → Your actual Google API key
   - `CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_IN_PRODUCTION` → A random secret key

## Environment Variables (Alternative)

You can also use environment variables instead of the config file:

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_actual_key_here
export OPENAI_MODEL=gpt-4o
```

## File Structure

- `bk25_config.json.example` - Safe example file (safe to commit)
- `bk25_config.json` - Your actual config (ignored by git)
- `README.md` - This file

## What's Protected

The following files are automatically ignored by git:
- `config/bk25_config.json` (your actual config)
- `*.config.json` (any config files)
- `.env*` files (environment variables)

## If You Accidentally Committed Sensitive Data

If you accidentally committed API keys:

1. **Immediately rotate/revoke the exposed keys**
2. **Remove the file from git history:**
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch config/bk25_config.json' \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push to remove from remote:**
   ```bash
   git push origin --force --all
   ```

## Best Practices

- Use environment variables in production
- Never commit `.env` files
- Use the example file as a template
- Regularly rotate API keys
- Use different keys for development and production
