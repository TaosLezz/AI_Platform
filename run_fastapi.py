#!/usr/bin/env python3
"""
FastAPI server launcher for AI Portfolio Platform
"""

import sys
import os
import subprocess

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    """Launch the FastAPI server"""
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        
        # Run the FastAPI server with uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ], cwd=backend_dir, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 FastAPI server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running FastAPI server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()