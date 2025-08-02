"""
AFM Data Platform Backend - Main Entry Point
Run with: python index.py
"""

from flask import Flask, send_from_directory, request
from flask_cors import CORS
import os
from api.routes import register_blueprints
from api.user_activity import log_user_activity

def create_app():
    # Determine if we're serving static files (production mode)
    static_folder = 'front-end/dist' if os.path.exists('front-end/dist') else None
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    
    # Configure CORS with hardcoded origins for development and production
    allowed_origins = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://localhost:5173',  # Vite default
        'http://localhost:8080',
        'http://localhost:5000',  # Flask default
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:8080',
        'http://127.0.0.1:5000',  # Flask default
        # Add your production URL here
        # 'https://your-production-domain.com',
        # 'https://afm-platform.skhynix.com',  # Example
    ]
    
    # Configure CORS
    CORS(app, 
         origins=allowed_origins,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         supports_credentials=True
    )


    # Register all API blueprints
    register_blueprints(app)
    
    # Add middleware to log user activities
    @app.before_request
    def before_request():
        # Skip logging for static files and favicon
        if request.path.startswith('/assets') or request.path == '/favicon.ico':
            return
        
        # Debug: Print all cookies (remove in production)
        if app.debug:
            print(f"\n=== COOKIES for {request.path} ===")
            for cookie_name, cookie_value in request.cookies.items():
                print(f"  {cookie_name}: {cookie_value}")
            print("=== END COOKIES ===\n")
        
        # Log user activity
        log_user_activity()
    
    # Serve Vue app in production
    if static_folder and os.path.exists('front-end/dist'):
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_vue_app(path):
            # Check if path is an API route
            if path.startswith('api/'):
                return {'error': 'Not found'}, 404
                
            # Check if path is a static file
            if path and os.path.exists(os.path.join('front-end/dist', path)):
                return send_from_directory('front-end/dist', path)
            
            # For all other routes, serve index.html (Vue Router will handle routing)
            return send_from_directory('front-end/dist', 'index.html')
    else:
        # Development mode - just API health check
        @app.route('/')
        def health_check():
            return {'status': 'AFM Data Platform Backend is running', 'version': '1.0.0'}
    
    return app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # This will run in development mode when called directly
    try:
        app.run(debug=True)
    except OSError as e:

        print(f"Error starting server: {e}")
        raise