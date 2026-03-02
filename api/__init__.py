"""
AFM Data Platform Backend package initialization.
"""

import atexit
import os
import time

from flask import Flask, request, send_from_directory
from flask_cors import CORS

from api.routes import register_blueprints
from api.utils.app_logger_standard import (
    cleanup_loggers,
    get_activity_logger,
    get_error_logger,
    get_system_logger,
)


def create_app():
    # Get logger instances
    system_logger = get_system_logger()
    activity_logger = get_activity_logger()
    error_logger = get_error_logger()

    # Determine if we're serving static files (production mode)
    static_folder = "front-end" if os.path.exists("front-end") else None
    app = Flask(__name__, static_folder=static_folder, static_url_path="")

    # Log application initialization
    system_logger.info(
        "AFM Data Platform Backend starting",
        extra={
            "mode": "production" if static_folder else "development",
            "static_folder": static_folder,
        },
    )

    # Keep CORS simple with a single frontend origin.
    allowed_origins = ["http://localhost:5173"]

    # Configure CORS
    CORS(
        app,
        origins=allowed_origins,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        supports_credentials=True,
    )

    system_logger.info("CORS configured", extra={"allowed_origins_count": len(allowed_origins)})

    # Register all API blueprints
    register_blueprints(app)
    system_logger.info("API blueprints registered")

    # Add middleware for request logging and user activities
    @app.before_request
    def before_request():
        # Store request start time for response time logging
        request.start_time = time.time()

        # Skip logging for static files and favicon
        if request.path.startswith("/assets") or request.path == "/favicon.ico":
            return

        # Debug: Log all cookies (including LASTUSER for user activity tracking)
        if app.debug:
            activity_logger.debug(
                "Request cookies",
                extra={
                    "path": request.path,
                    "cookies": dict(request.cookies),
                    "method": request.method,
                },
            )

        # User activity logging now handled in individual routes

    # Add after_request middleware for response logging
    @app.after_request
    def after_request(response):
        # Skip logging for static files
        if not (request.path.startswith("/assets") or request.path == "/favicon.ico"):
            # Calculate request duration
            duration = time.time() - getattr(request, "start_time", time.time())

            activity_logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", "Unknown"),
                },
            )

        return response

    # Add error handler
    @app.errorhandler(Exception)
    def handle_error(error):
        error_logger.exception(
            "Unhandled exception occurred",
            extra={
                "error_type": type(error).__name__,
                "path": request.path,
                "method": request.method,
            },
        )

        return {"error": "Internal server error"}, 500

    # Serve Vue app in production
    if static_folder and os.path.exists("front-end"):
        system_logger.info("Serving Vue app from static folder")

        # Route to get current user info from LASTUSER cookie (for frontend)
        @app.route("/api/current-user")
        def get_current_user():
            last_user = request.cookies.get("LASTUSER")
            if last_user:
                return {"authenticated": True, "user_id": last_user}
            return {"authenticated": False, "user_id": None}

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_vue_app(path):
            # Check if path is an API route
            if path.startswith("api/"):
                return {"error": "Not found"}, 404

            # Check if path is a static file
            if path and os.path.exists(os.path.join("front-end", path)):
                return send_from_directory("front-end", path)

            # For all other routes, serve index.html (Vue Router will handle routing)
            return send_from_directory("front-end", "index.html")
    else:
        # Development mode - just API health check
        @app.route("/")
        def health_check():
            activity_logger.debug("Health check endpoint accessed")
            return {"status": "AFM Data Platform Backend is running", "version": "1.0.0"}

    return app


def run_dev_server():
    system_logger = get_system_logger()
    error_logger = get_error_logger()

    try:
        system_logger.info(
            "Starting Flask development server",
            extra={"host": "127.0.0.1", "port": 5000, "debug": True},
        )
        application.run(debug=True)
    except OSError as error:
        error_logger.error(
            "Failed to start server",
            extra={"error": str(error), "error_type": type(error).__name__},
        )
        raise
    except KeyboardInterrupt:
        system_logger.info("Server shutdown by user")
    except Exception:
        error_logger.exception("Unexpected error during server startup")
        raise
    finally:
        cleanup_loggers()


# Create the Flask application instance
application = create_app()

# Register cleanup function
atexit.register(cleanup_loggers)
