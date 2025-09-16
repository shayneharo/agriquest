#!/usr/bin/env python3
"""
AgriQuest - Main Application Entry Point
Agricultural Learning Platform
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import and create the Flask app
from backend import create_app

# Create the application
app = create_app()

if __name__ == '__main__':
    # Print startup information
    print("Current Working Directory:", os.getcwd())
    print("Files in Directory:", os.listdir())
    
    # Run the application
    app.run(debug=True)
