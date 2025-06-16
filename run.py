#!/usr/bin/env python3
"""
AFM Data Platform Backend - Development Runner
Run this file to start the Flask development server
For production, use index.py which is the UWSGI entry point
"""

from index import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')  # Changed from 0.0.0.0 to 127.0.0.1
    
    print("Starting AFM Data Platform Backend (Development Mode)...")
    print(f"Backend will be available at: http://{host}:{port}")
    print(f"API endpoints available at: http://{host}:{port}/api")
    print(f"Health check: http://{host}:{port}")
    print("Note: For production, UWSGI server will use index.py directly")
    print("If port 5000 is in use, try: PORT=5001 python run.py")
    
    try:
        app.run(debug=True, port=port, host=host)
    except OSError as e:
        if "Address already in use" in str(e) or "socket" in str(e).lower():
            print(f"Error: Port {port} is already in use or access denied.")
            print("Try running with a different port:")
            print(f"  PORT=5001 python run.py")
            print(f"  PORT=8000 python run.py")
        else:
            print(f"Error starting server: {e}")
            raise