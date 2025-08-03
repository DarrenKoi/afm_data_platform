"""
AFM Data Platform Backend - Main Entry Point
Run with: python index.py
"""

from flask import Flask, send_from_directory, request
from flask_cors import CORS
import os
from api.routes import register_blueprints
from api.user_activity import log_user_activity
from api.utils.app_logger import get_system_logger, get_activity_logger, get_error_logger, cleanup_logger
import atexit
import time

def create_app():
    # Get logger instances
    system_logger = get_system_logger()
    activity_logger = get_activity_logger()
    error_logger = get_error_logger()
    
    # Determine if we're serving static files (production mode)
    static_folder = 'front-end/dist' if os.path.exists('front-end/dist') else None
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    
    # Log application initialization
    system_logger.info("AFM Data Platform Backend starting", 
                      mode="production" if static_folder else "development",
                      static_folder=static_folder)
    
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
    
    system_logger.info("CORS configured", allowed_origins_count=len(allowed_origins))


    # Register all API blueprints
    register_blueprints(app)
    system_logger.info("API blueprints registered")
    
    # Add middleware for request logging and user activities
    @app.before_request
    def before_request():
        # Store request start time for response time logging
        request.start_time = time.time()
        # Skip logging for static files and favicon
        if request.path.startswith('/assets') or request.path == '/favicon.ico':
            return
        
        # Debug: Log all cookies
        if app.debug:
            activity_logger.debug("Request cookies", 
                                 path=request.path,
                                 cookies=dict(request.cookies),
                                 method=request.method)
        
        # Log user activity
        log_user_activity()
    
    # Add after_request middleware for response logging
    @app.after_request
    def after_request(response):
        # Skip logging for static files
        if not (request.path.startswith('/assets') or request.path == '/favicon.ico'):
            # Calculate request duration
            duration = time.time() - getattr(request, 'start_time', time.time())
            
            activity_logger.info("Request completed",
                                method=request.method,
                                path=request.path,
                                status_code=response.status_code,
                                duration_ms=round(duration * 1000, 2),
                                remote_addr=request.remote_addr,
                                user_agent=request.headers.get('User-Agent', 'Unknown'))
        
        return response
    
    # Add error handler
    @app.errorhandler(Exception)
    def handle_error(error):
        error_logger.exception("Unhandled exception occurred",
                             error_type=type(error).__name__,
                             path=request.path,
                             method=request.method)
        
        return {'error': 'Internal server error'}, 500
    
    # Serve Vue app in production
    if static_folder and os.path.exists('front-end/dist'):
        system_logger.info("Serving Vue app from static folder")
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
            activity_logger.debug("Health check endpoint accessed")
            return {'status': 'AFM Data Platform Backend is running', 'version': '1.0.0'}
    
    return app

# Create the Flask application instance
app = create_app()

# Register cleanup function
atexit.register(cleanup_logger)

if __name__ == '__main__':
    # This will run in development mode when called directly
    system_logger = get_system_logger()
    error_logger = get_error_logger()
    
    try:
        system_logger.info("Starting Flask development server",
                          host="127.0.0.1",
                          port=5000,
                          debug=True)
        
        app.run(debug=True)
        
    except OSError as e:
        error_logger.error("Failed to start server",
                          error=str(e),
                          error_type=type(e).__name__)
        raise
    except KeyboardInterrupt:
        system_logger.info("Server shutdown by user")
    except Exception as e:
        error_logger.exception("Unexpected error during server startup")
        raise
    finally:
        cleanup_logger()