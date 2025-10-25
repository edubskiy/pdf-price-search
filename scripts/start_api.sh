#!/bin/bash
# Start API server script

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Set default environment variables
export API_HOST="${API_HOST:-0.0.0.0}"
export API_PORT="${API_PORT:-8000}"
export API_RELOAD="${API_RELOAD:-true}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo "Starting PDF Price Search API..."
echo "Host: $API_HOST"
echo "Port: $API_PORT"
echo "Reload: $API_RELOAD"
echo ""

# Run the API server
python3 main_api.py
