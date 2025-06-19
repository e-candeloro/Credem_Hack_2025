#!/bin/bash
set -e

echo "🚀 Setting up AI HR System development environment..."

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="/root/.cargo/bin:$PATH"
fi

# Install project dependencies
echo "📦 Installing project dependencies..."
uv pip sync

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Development environment variables
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=sqlite:///./app.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
EOF
fi

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Start the backend: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "  2. Start the frontend: streamlit run frontend/Home.py --server.port 8501 --server.address 0.0.0.0"
echo "  3. Run tests: pytest"
echo "  4. Run pre-commit: pre-commit run --all-files"
