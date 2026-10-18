"""
Vercel Serverless Function Handler for DataMind API
Dispatches /api/* endpoints (query, config, health, mutate, telemetry)
"""

import os
import sys

# Add project root to sys.path so src.* and server.* can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import DataMindAPIHandler

class handler(DataMindAPIHandler):
    """Vercel Python serverless entry point."""
    pass
