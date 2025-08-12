"""
AFM Data Platform Backend - Main Entry Point
Run with: python index.py
"""

from flask import Flask, send_from_directory, request, session, redirect
from flask_cors import CORS
import os
from api.routes import register_blueprints
# User activity logging removed - now handled in individual routes
from api.utils.app_logger_standard import get_system_logger, get_activity_logger, get_error_logger, cleanup_loggers
import atexit
import time

# SSO import for production mode
try:
    from hcputil.auth.sso import SSO
    SSO_AVAILABLE = True
except ImportError:
    SSO_AVAILABLE = False

def create_app():
    # Get logger instances
    system_logger = get_system_logger()
    activity_logger = get_activity_logger()
    error_logger = get_error_logger()
    
    # Determine if we're serving static files (production mode)
    static_folder = 'front-end' if os.path.exists('front-end') else None
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    
    # Configure session secret key for SSO (use environment variable in production)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Log application initialization
    system_logger.info("AFM Data Platform Backend starting", extra={
                      'mode': "production" if static_folder else "development",
                      'static_folder': static_folder})
    
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
    
    system_logger.info("CORS configured", extra={'allowed_origins_count': len(allowed_origins)})


    # Register all API blueprints
    register_blueprints(app)
    system_logger.info("API blueprints registered")
    
    # Add middleware for request logging and user activities
    @app.before_request
    def before_request():
        # Store request start time for response time logging
        request.start_time = time.time()
        
        # SSO authentication check for API routes in production
        if SSO_AVAILABLE and static_folder:
            # Allow login route and static assets without authentication
            if not (request.path.startswith('/login') or 
                    request.path.startswith('/assets') or 
                    request.path == '/favicon.ico'):
                # Check if user is authenticated for all other routes (including API)
                if session.get('logFlag') != True:
                    # Check for LASTUSER cookie to auto-authenticate
                    last_user = request.cookies.get('LASTUSER')
                    if last_user is not None:
                        # Auto-authenticate user based on LASTUSER cookie
                        session['logFlag'] = True
                        session['user_id'] = last_user
                        
                        activity_logger.info("User auto-authenticated via LASTUSER cookie", extra={
                            'user_id': last_user,
                            'path': request.path
                        })
                    else:
                        # No authentication available
                        # For API routes, return 401 Unauthorized
                        if request.path.startswith('/api/'):
                            return {'error': 'Unauthorized - Please login first'}, 401
                        # For other routes, redirect to login
                        else:
                            return redirect('/login')
        
        # Skip logging for static files and favicon
        if request.path.startswith('/assets') or request.path == '/favicon.ico':
            return
        
        # Debug: Log all cookies
        if app.debug:
            activity_logger.debug("Request cookies", extra={
                                 'path': request.path,
                                 'cookies': dict(request.cookies),
                                 'method': request.method})
        
        # User activity logging now handled in individual routes
    
    # Add after_request middleware for response logging
    @app.after_request
    def after_request(response):
        # Skip logging for static files
        if not (request.path.startswith('/assets') or request.path == '/favicon.ico'):
            # Calculate request duration
            duration = time.time() - getattr(request, 'start_time', time.time())
            
            activity_logger.info("Request completed", extra={
                                'method': request.method,
                                'path': request.path,
                                'status_code': response.status_code,
                                'duration_ms': round(duration * 1000, 2),
                                'remote_addr': request.remote_addr,
                                'user_agent': request.headers.get('User-Agent', 'Unknown')})
        
        return response
    
    # Add error handler
    @app.errorhandler(Exception)
    def handle_error(error):
        error_logger.exception("Unhandled exception occurred", extra={
                             'error_type': type(error).__name__,
                             'path': request.path,
                             'method': request.method})
        
        return {'error': 'Internal server error'}, 500
    
    # Serve Vue app in production
    if static_folder and os.path.exists('front-end'):
        system_logger.info("Serving Vue app from static folder")
        
        # Configure SSO if available in production mode
        if SSO_AVAILABLE:
            system_logger.info("SSO authentication enabled")
            
            # Route to get current user info (for frontend)
            @app.route('/api/current-user')
            def get_current_user():
                if session.get('logFlag') == True:
                    return {
                        'authenticated': True,
                        'user_id': session.get('user_id')
                    }
                else:
                    return {'authenticated': False}, 401
            
            # Logout route
            @app.route('/logout')
            def logout():
                user_id = session.get('user_id', 'Unknown')
                session.clear()
                
                activity_logger.info("User logged out", extra={'user_id': user_id})
                
                # Redirect to SSO logout if available, otherwise to login
                try:
                    sso = SSO(request)
                    if hasattr(sso, 'logout_url'):
                        return redirect(sso.logout_url)
                except:
                    pass
                
                return redirect('/login')
            
            # SSO login route
            @app.route('/login')
            @app.route('/login/<path:sub_path>')
            def login(sub_path=None):
                sso = SSO(request)
                # Redirect to the original path after login, or to root
                if sub_path is not None:
                    redirect_url = '/' + sub_path
                else:
                    redirect_url = '/'
                    
                # Check if user is already logged in
                if session.get('logFlag') != True:
                    cookie = request.headers.get('cookie')
                    # Check for LASTUSER cookie which contains user membership number
                    last_user = request.cookies.get('LASTUSER')
                    
                    if cookie is not None and last_user is not None:
                        session['logFlag'] = True
                        # Store user membership number from LASTUSER cookie
                        session['user_id'] = last_user
                        
                        activity_logger.info("User logged in via SSO", extra={
                            'user_id': last_user,
                            'user_agent': request.headers.get('User-Agent', 'Unknown')
                        })
                        
                        return redirect(redirect_url)
                    else:
                        # Redirect to SSO login page
                        return redirect(sso.login_url)
                else:
                    # Already logged in, redirect to requested page
                    return redirect(redirect_url)
            
            @app.route('/', defaults={'path': ''})
            @app.route('/<path:path>')
            def serve_vue_app(path):
                # Check if path is an API route
                if path.startswith('api/'):
                    return {'error': 'Not found'}, 404
                
                # Check if user is authenticated (except for login route)
                if not path.startswith('login') and session.get('logFlag') != True:
                    # User not authenticated, redirect to login page
                    if path:
                        return redirect(f'/login/{path}')
                    else:
                        return redirect('/login')
                
                # User is authenticated or accessing login route
                # Check if path is a static file
                if path and os.path.exists(os.path.join('front-end', path)):
                    return send_from_directory('front-end', path)
                
                # For all other routes, serve index.html (Vue Router will handle routing)
                return send_from_directory('front-end', 'index.html')
                
        else:
            # No SSO available (development mode or SSO package not installed)
            system_logger.warning("SSO not available - running without authentication")
            
            @app.route('/', defaults={'path': ''})
            @app.route('/<path:path>')
            def serve_vue_app(path):
                # Check if path is an API route
                if path.startswith('api/'):
                    return {'error': 'Not found'}, 404
                    
                # Check if path is a static file
                if path and os.path.exists(os.path.join('front-end', path)):
                    return send_from_directory('front-end', path)
                
                # For all other routes, serve index.html (Vue Router will handle routing)
                return send_from_directory('front-end', 'index.html')
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
atexit.register(cleanup_loggers)

if __name__ == '__main__':
    # This will run in development mode when called directly
    system_logger = get_system_logger()
    error_logger = get_error_logger()
    
    try:
        system_logger.info("Starting Flask development server", extra={
                          'host': "127.0.0.1",
                          'port': 5000,
                          'debug': True})
        
        app.run(debug=True)
        
    except OSError as e:
        error_logger.error("Failed to start server", extra={
                          'error': str(e),
                          'error_type': type(e).__name__})
        raise
    except KeyboardInterrupt:
        system_logger.info("Server shutdown by user")
    except Exception as e:
        error_logger.exception("Unexpected error during server startup")
        raise
    finally:
        cleanup_loggers()