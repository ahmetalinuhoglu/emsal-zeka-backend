#!/usr/bin/env python3
"""
Railway startup script to handle PORT environment variable properly
"""

import os
import subprocess
import sys

def main():
    # Get PORT from environment, default to 8000
    port = os.getenv("PORT", "8000")
    
    print(f"🚀 Starting Emsal Zeka Backend on port {port}")
    print(f"📍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    # Start uvicorn with proper port
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", str(port)
    ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    
    try:
        # Execute uvicorn
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 