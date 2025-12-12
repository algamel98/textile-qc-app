# -*- coding: utf-8 -*-
"""
Textile QC Web Application Factory
"""
import os
import logging
from flask import Flask
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def create_app(config_name='production'):
    """Create and configure the Flask application."""
    
    # Get the absolute path to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(app_dir)
    
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'textile-qc-secret-key-2024')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')
    app.config['OUTPUT_FOLDER'] = os.path.join(base_dir, 'outputs')
    
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Enable CORS
    CORS(app)
    
    # Register routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

