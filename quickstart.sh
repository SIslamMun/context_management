#!/bin/bash
# Quick start script for context management research project

set -e

echo "========================================"
echo "Context Management Research Project"
echo "Quick Start Script"
echo "========================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv is not installed."
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Or with pip: pip install uv"
    exit 1
fi

echo "✅ uv is installed"
echo ""

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv pip install -e . --quiet || {
    echo "⚠️  Failed to install from pyproject.toml, trying requirements.txt..."
    uv pip install -r requirements.txt --quiet || {
        echo "❌ Failed to install dependencies"
        exit 1
    }
}

echo "✅ Dependencies installed"
echo ""

# Run demonstrations
echo "========================================"
echo "Running Task A: Decompilation Explorer"
echo "========================================"
echo ""
uv run task_a_decompilation_explorer.py

echo ""
echo ""
echo "========================================"
echo "Running Task B: Call Interceptor"
echo "========================================"
echo ""
uv run task_b_call_interceptor.py

echo ""
echo ""
echo "========================================"
echo "Task C: Haiku Agent"
echo "========================================"
echo ""
echo "ℹ️  Task C requires Claude Code CLI and API access."
echo "   Skipping automatic run. To run manually:"
echo "   $ uv run task_c_haiku_agent.py"
echo ""

echo "========================================"
echo "✅ Quick start complete!"
echo "========================================"
echo ""
echo "📁 Check the following directories for outputs:"
echo "   - analysis_results/"
echo "   - interception_logs/"
echo "   - haiku_agent_logs/"
echo ""
echo "📖 See README.md for detailed documentation"
