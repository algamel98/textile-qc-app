# -*- coding: utf-8 -*-
"""
API Routes for Textile QC Web Application
"""
import os
import uuid
import json
import logging
from flask import (
    Blueprint, request, jsonify, send_file, render_template, 
    current_app, send_from_directory
)
from werkzeug.utils import secure_filename

from app.core.settings import QCSettings
from app.core.image_utils import read_rgb, to_same_size, validate_image_file
from app.pipeline.runner import run_analysis_pipeline

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route('/')
def index():
    """Render main application page"""
    return render_template('index.html')


@main_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '2.0.0'})


@main_bp.route('/api/upload', methods=['POST'])
def upload_images():
    """Handle image upload"""
    try:
        if 'reference' not in request.files or 'sample' not in request.files:
            return jsonify({'error': 'Both reference and sample images required'}), 400
        
        ref_file = request.files['reference']
        test_file = request.files['sample']
        
        if ref_file.filename == '' or test_file.filename == '':
            return jsonify({'error': 'No selected files'}), 400
        
        if not allowed_file(ref_file.filename) or not allowed_file(test_file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, TIFF, BMP'}), 400
        
        # Create session directory
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save files
        ref_filename = secure_filename(ref_file.filename)
        test_filename = secure_filename(test_file.filename)
        
        ref_path = os.path.join(session_dir, f'reference_{ref_filename}')
        test_path = os.path.join(session_dir, f'sample_{test_filename}')
        
        ref_file.save(ref_path)
        test_file.save(test_path)
        
        # Validate images
        validate_image_file(ref_path)
        validate_image_file(test_path)
        
        # Read images to get dimensions
        ref = read_rgb(ref_path)
        test = read_rgb(test_path)
        
        logger.info(f"Images uploaded: session={session_id}, ref={ref.shape}, test={test.shape}")
        
        return jsonify({
            'session_id': session_id,
            'reference': {
                'filename': ref_filename,
                'width': ref.shape[1],
                'height': ref.shape[0]
            },
            'sample': {
                'filename': test_filename,
                'width': test.shape[1],
                'height': test.shape[0]
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload images'}), 500


@main_bp.route('/api/image/<session_id>/<image_type>')
def get_image(session_id, image_type):
    """Serve uploaded image"""
    try:
        session_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
        
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session not found'}), 404
        
        # Find the image file
        prefix = 'reference_' if image_type == 'reference' else 'sample_'
        
        for filename in os.listdir(session_dir):
            if filename.startswith(prefix):
                return send_from_directory(session_dir, filename)
        
        return jsonify({'error': 'Image not found'}), 404
        
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        return jsonify({'error': 'Failed to serve image'}), 500


@main_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """Run analysis pipeline"""
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({'error': 'Session ID required'}), 400
        
        session_id = data['session_id']
        session_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
        
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session not found'}), 404
        
        # Find image files
        ref_path = None
        test_path = None
        
        for filename in os.listdir(session_dir):
            if filename.startswith('reference_'):
                ref_path = os.path.join(session_dir, filename)
            elif filename.startswith('sample_'):
                test_path = os.path.join(session_dir, filename)
        
        if not ref_path or not test_path:
            return jsonify({'error': 'Images not found'}), 404
        
        # Parse settings
        settings = QCSettings()
        if 'settings' in data:
            settings = QCSettings.from_dict(data['settings'])
        
        # Read images
        ref = read_rgb(ref_path)
        test = read_rgb(test_path)
        ref, test = to_same_size(ref, test)
        
        # Create output directory
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Run analysis
        logger.info(f"Starting analysis for session {session_id}")
        results = run_analysis_pipeline(ref_path, test_path, ref, test, settings, output_dir)
        
        # Prepare response
        response = {
            'session_id': session_id,
            'decision': results['decision'],
            'color_score': results['color_score'],
            'pattern_score': results['pattern_score'],
            'overall_score': results['overall_score'],
            'pdf_filename': os.path.basename(results['pdf_path']),
        }
        
        if 'color_metrics' in results:
            response['color_metrics'] = results['color_metrics']
        
        if 'pattern_metrics' in results:
            response['pattern_metrics'] = {
                k: v for k, v in results['pattern_metrics'].items() 
                if not isinstance(v, (list, dict)) or k == 'status'
            }
        
        if 'pattern_repetition' in results:
            rep = results['pattern_repetition']
            response['pattern_repetition'] = {
                'count_ref': rep['count_ref'],
                'count_test': rep['count_test'],
                'count_diff': rep['count_diff'],
                'status': rep['status']
            }
        
        logger.info(f"Analysis complete for session {session_id}: {results['decision']}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@main_bp.route('/api/download/<session_id>/<filename>')
def download_report(session_id, filename):
    """Download generated PDF report"""
    try:
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], session_id)
        
        if not os.path.exists(output_dir):
            return jsonify({'error': 'Session not found'}), 404
        
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500


@main_bp.route('/api/chart/<session_id>/<chart_name>')
def get_chart(session_id, chart_name):
    """Serve generated chart image"""
    try:
        charts_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], session_id, 'charts')
        
        if not os.path.exists(charts_dir):
            return jsonify({'error': 'Charts not found'}), 404
        
        return send_from_directory(charts_dir, f'{chart_name}.png')
        
    except Exception as e:
        logger.error(f"Chart error: {str(e)}")
        return jsonify({'error': 'Failed to serve chart'}), 500


@main_bp.route('/api/settings/default')
def get_default_settings():
    """Get default settings"""
    settings = QCSettings()
    return jsonify(settings.to_dict())

