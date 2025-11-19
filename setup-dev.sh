#!/bin/bash
# Development environment setup script for Voicebook

set -e

echo "🚀 Setting up Voicebook development environment..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "❌ Error: Python 3.9 or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --quiet --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📥 Installing production dependencies..."
pip install --quiet -r requirements.txt
echo "✅ Production dependencies installed"
echo ""

echo "📥 Installing development dependencies..."
pip install --quiet -r requirements-dev.txt
echo "✅ Development dependencies installed"
echo ""

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install
echo "✅ Pre-commit hooks installed"
echo ""

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
pytest tests/ -q --tb=short
echo "✅ Tests passed"
echo ""

# Generate coverage report
echo "📊 Generating coverage report..."
pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing -q
echo "✅ Coverage report generated (see htmlcov/index.html)"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Remember to add your OPENAI_API_KEY to .env file"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Summary
echo "✅ Development environment setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Add your OpenAI API key to .env file"
echo "   3. Run the app: streamlit run src/ui/app.py"
echo "   4. Run tests: pytest tests/"
echo "   5. Check code quality: pre-commit run --all-files"
echo ""
echo "📖 Documentation:"
echo "   - README.md - Getting started guide"
echo "   - CONTRIBUTING.md - Contribution guidelines"
echo "   - tests/README.md - Testing guide"
echo "   - .github/CI_CD_SETUP.md - CI/CD documentation"
echo ""
echo "Happy coding! 🎉"
