#!/bin/bash
# Autonomous Claude Web Interface Startup Script

echo "================================="
echo "🤖 Autonomous Claude Web Interface"
echo "================================="
echo ""

# Check if TypeScript is available
if command -v tsc &> /dev/null; then
    echo "📦 Compiling TypeScript..."
    cd /home/user/mich3333/autonomous-claude
    tsc
    echo "✅ TypeScript compiled!"
    echo ""
else
    echo "⚠️  TypeScript not found - using pre-compiled JavaScript"
    echo "   To enable TypeScript: npm install -g typescript"
    echo ""
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo "   ChatGPT features will be unavailable"
    echo "   Set it with: export OPENAI_API_KEY='your-key'"
    echo ""
else
    echo "✅ OPENAI_API_KEY is set"
    echo ""
fi

# Start Flask server
echo "🌐 Starting Flask web server..."
echo ""
python3 /home/user/mich3333/autonomous-claude/web_app.py
