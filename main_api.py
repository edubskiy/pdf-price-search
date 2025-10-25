#!/usr/bin/env python3
"""
Main entry point for the API server.

This script starts the FastAPI application using Uvicorn.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn


def main():
    """Start the API server."""
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() in ("true", "1", "yes")
    workers = int(os.getenv("API_WORKERS", "1"))

    # Run uvicorn
    uvicorn.run(
        "src.presentation.api.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,  # Workers don't work with reload
        log_level="info"
    )


if __name__ == '__main__':
    main()
