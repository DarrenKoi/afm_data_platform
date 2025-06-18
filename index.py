"""
AFM Data Platform Backend - Main Entry Point
Run with: python index.py
"""

from flask import Flask
from flask_cors import CORS
import atexit
import os
from api.routes import api_bp
from api.scheduler import init_scheduler

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for frontend communication
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize APScheduler
    scheduler = init_scheduler(app)
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    @app.route('/')
    def health_check():
        return {'status': 'AFM Data Platform Backend is running', 'version': '1.0.0'}
    
    return app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # This will run in development mode when called directly
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
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