"""Test configuration for PSPlot."""

import os
import sys

# Add parent directory to path so tests can import main modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

# Configure logging for tests
config.setup_logging(log_level=20)  # INFO level
