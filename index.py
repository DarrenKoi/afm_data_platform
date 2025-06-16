"""
AFM Data Platform Backend - Production Entry Point
This file is used by UWSGI server in production mode
"""

from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # This will run in development mode when called directly
    import os
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')  # Changed from 0.0.0.0 to 127.0.0.1
    
    print("Starting AFM Data Platform Backend...")
    print(f"Backend will be available at: http://{host}:{port}")
    print(f"API endpoints available at: http://{host}:{port}/api")
    print("If port 5000 is in use, try: PORT=5001 python index.py")
    
    try:
        app.run(debug=True, port=port, host=host)
    except OSError as e:
        if "Address already in use" in str(e) or "socket" in str(e).lower():
            print(f"Error: Port {port} is already in use or access denied.")
            print("Try running with a different port:")
            print(f"  PORT=5001 python index.py")
            print(f"  PORT=8000 python index.py")
        else:
            print(f"Error starting server: {e}")
            raise