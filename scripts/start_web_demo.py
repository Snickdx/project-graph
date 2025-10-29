#!/usr/bin/env python3
"""
Flask Web App Launcher
=======================
Launch the web demo for the RAG system
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Flask web app"""
    print("="*60)
    print("🌐 Starting Requirements Graph Web Demo")
    print("="*60)
    
    # Get the current directory
    current_dir = Path(__file__).parent.parent
    web_app_dir = current_dir / 'web_app'
    app_file = web_app_dir / 'app.py'
    
    if not app_file.exists():
        print(f"❌ Web app not found: {app_file}")
        return
    
    print(f"📁 Working Directory: {current_dir}")
    print(f"🚀 Starting Flask app: {app_file}")
    print("-"*60)
    print("🌐 Web Interface: http://localhost:5000")
    print("❌ Stop with: Ctrl+C")
    print("-"*60)
    
    try:
        # Change to web app directory and run
        os.chdir(web_app_dir)
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Web demo stopped by user")
    except Exception as e:
        print(f"❌ Error starting web app: {e}")

if __name__ == "__main__":
    main()