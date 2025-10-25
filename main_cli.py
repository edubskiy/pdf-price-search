#!/usr/bin/env python3
"""
Main entry point for the CLI application.

This script provides the command-line interface for PDF Price Search.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.presentation.cli import main

if __name__ == '__main__':
    sys.exit(main())
