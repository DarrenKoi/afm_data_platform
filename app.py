from flask import Flask
from flask_cors import CORS
import atexit
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

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)