"""
AFM Data Platform Backend - Main Entry Point
Run with: python index.py
"""

from flask import Flask
from flask_cors import CORS
import os
from api.routes import api_bp

def create_app():
    app = Flask(__name__)
    
    # Configure CORS with flexible settings for development
    # Get custom origins from environment variable
    custom_origins = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else []
    
    # Default allowed origins for local development
    default_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://localhost:3002',
        'http://localhost:5173',  # Vite default
        'http://localhost:8080',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001',
        'http://127.0.0.1:3002',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:8080',
    ]
    
    # Combine and deduplicate origins
    allowed_origins = list(set(default_origins + [origin.strip() for origin in custom_origins if origin.strip()]))
    
    # Configure CORS
    CORS(app, 
         origins=allowed_origins,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         supports_credentials=True
    )

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    
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