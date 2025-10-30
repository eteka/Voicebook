#!/usr/bin/env python3
"""
Voicebook - Quick launch script

This script makes it easy to run the Voicebook application.
Simply run: python run.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit application."""
    # Path to the main app
    app_path = Path(__file__).parent / "src" / "ui" / "app.py"

    if not app_path.exists():
        print("❌ Error: Application file not found!")
        print(f"Expected location: {app_path}")
        sys.exit(1)

    print("🚀 Starting Voicebook...")
    print("📖 Opening in your browser...\n")

    try:
        # Run streamlit
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.headless=false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Voicebook...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
