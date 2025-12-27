#!/bin/bash
# Autonomous Claude Installation Script

set -e

echo "=================================="
echo "Autonomous Claude Setup"
echo "=================================="
echo ""

# Create directories
echo "Creating directories..."
mkdir -p /autonomous-claude/data/memory
mkdir -p /autonomous-claude/data/screenshots
mkdir -p ~/.claude/skills
echo "✓ Directories created"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -q -r /autonomous-claude/requirements.txt
    echo "✓ Python dependencies installed"
else
    echo "⚠ pip3 not found. Please install manually:"
    echo "  pip install -r /autonomous-claude/requirements.txt"
fi
echo ""

# Initialize memory database
echo "Initializing memory system..."
python3 /autonomous-claude/setup_memory.py
echo ""

# Check for Qdrant
echo "Checking Qdrant status..."
if curl -s http://localhost:6333/health &> /dev/null; then
    echo "✓ Qdrant is running"
else
    echo "⚠ Qdrant is not running"
    echo ""
    echo "To start Qdrant with Docker:"
    echo "  docker run -d -p 6333:6333 -v \$(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant"
    echo ""
    echo "Or install Qdrant locally:"
    echo "  https://qdrant.tech/documentation/install/"
fi
echo ""

# Test installation
echo "Testing installation..."
python3 /autonomous-claude/decision_loop.py &> /tmp/test_output.txt
if [ $? -eq 0 ]; then
    echo "✓ Decision loop test passed"
else
    echo "⚠ Decision loop test failed. Check /tmp/test_output.txt"
fi
echo ""

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start Qdrant (if not already running)"
echo "2. Read the documentation: /autonomous-claude/README.md"
echo "3. Run a test: python3 /autonomous-claude/decision_loop.py"
echo ""
