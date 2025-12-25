# -*- coding: utf-8 -*-
"""
API Routes for Textile QC Web Application
Robust version with improved error handling
"""
import os
import uuid
import json
import logging
import traceback
from flask import (
    Blueprint, request, jsonify, send_file, render_template, 
    current_app, send_from_directory, Response
)
from werkzeug.utils import secure_filename

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
        
        # Validate and get dimensions
        from app.core.image_utils import read_rgb, validate_image_file
        
        try:
            validate_image_file(ref_path)
            validate_image_file(test_path)
        except Exception as e:
            return jsonify({'error': f'Invalid image: {str(e)}'}), 400
        
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
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to upload images: {str(e)}'}), 500


@main_bp.route('/api/image/<session_id>/<image_type>')
def get_image(session_id, image_type):
    """Serve uploaded image"""
    try:
        session_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], session_id)
        
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session not found'}), 404
        
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
    """Run analysis pipeline with robust error handling"""
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
        from app.core.settings import QCSettings
        settings = QCSettings()
        if 'settings' in data:
            try:
                settings = QCSettings.from_dict(data['settings'])
            except Exception as e:
                logger.warning(f"Settings parsing error: {e}, using defaults")
        
        # Read images
        from app.core.image_utils import read_rgb, to_same_size
        ref = read_rgb(ref_path)
        test = read_rgb(test_path)
        ref, test = to_same_size(ref, test)
        
        # Create output directory
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Run analysis with error handling
        logger.info(f"Starting analysis for session {session_id}")
        
        results = None
        try:
            from app.pipeline.runner import run_analysis_pipeline
            results = run_analysis_pipeline(ref_path, test_path, ref, test, settings, output_dir)
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            logger.error(traceback.format_exc())
            # Create minimal results
            results = {
                'decision': 'ERROR',
                'color_score': 0,
                'pattern_score': 0,
                'overall_score': 0,
                'error': str(e)
            }
        
        # Ensure we have valid results
        if results is None:
            results = {
                'decision': 'ERROR',
                'color_score': 0,
                'pattern_score': 0,
                'overall_score': 0,
                'error': 'Analysis returned no results'
            }
        
        # Check for errors
        if results.get('decision') == 'ERROR':
            logger.error(f"Analysis error: {results.get('error', 'Unknown error')}")
            # Still try to return a valid response
            response = {
                'session_id': session_id,
                'decision': 'ERROR',
                'color_score': float(results.get('color_score', 0)),
                'pattern_score': float(results.get('pattern_score', 0)),
                'overall_score': float(results.get('overall_score', 0)),
                'error': str(results.get('error', 'Analysis failed')),
                'pdf_filename': ''
            }
            return jsonify(response), 200  # Return 200 to prevent JSON parse error
        
        # Ensure PDF path exists
        pdf_path = results.get('pdf_path', '')
        pdf_filename = os.path.basename(pdf_path) if pdf_path else ''
        
        # If no PDF was created, try to create one
        if not pdf_filename or not os.path.exists(pdf_path):
            logger.warning("PDF not found, attempting to create fallback")
            try:
                from app.report.pdf_builder import create_fallback_pdf
                pdf_path = create_fallback_pdf(results, settings, output_dir)
                pdf_filename = os.path.basename(pdf_path)
                logger.info(f"Fallback PDF created: {pdf_filename}")
            except Exception as e:
                logger.error(f"Fallback PDF failed: {e}")
                pdf_filename = 'report_unavailable.pdf'
        
        # Prepare response - ensure all values are JSON serializable
        response = {
            'session_id': session_id,
            'decision': str(results.get('decision', 'N/A')),
            'color_score': float(results.get('color_score', 0)),
            'pattern_score': float(results.get('pattern_score', 0)),
            'overall_score': float(results.get('overall_score', 0)),
            'pdf_filename': pdf_filename,
        }
        
        # Add metrics if available (only serializable values)
        if 'color_metrics' in results:
            response['color_metrics'] = {}
            for k, v in results['color_metrics'].items():
                if isinstance(v, (int, float, str, bool)):
                    response['color_metrics'][k] = v
        
        if 'pattern_metrics' in results:
            response['pattern_metrics'] = {}
            for k, v in results['pattern_metrics'].items():
                if isinstance(v, (int, float, str, bool)):
                    response['pattern_metrics'][k] = v
        
        if 'pattern_repetition' in results:
            response['pattern_repetition'] = {}
            for k, v in results['pattern_repetition'].items():
                if isinstance(v, (int, float, str, bool)):
                    response['pattern_repetition'][k] = v
        
        logger.info(f"Analysis complete for session {session_id}: {results.get('decision')}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}")
        logger.error(traceback.format_exc())
        # Always return valid JSON
        return jsonify({
            'session_id': data.get('session_id', '') if data else '',
            'decision': 'ERROR',
            'color_score': 0,
            'pattern_score': 0,
            'overall_score': 0,
            'error': f'Analysis failed: {str(e)}',
            'pdf_filename': ''
        }), 200  # Return 200 to prevent JSON parse error on client


@main_bp.route('/api/download/<session_id>/<filename>')
def download_report(session_id, filename):
    """Download generated PDF report"""
    try:
        output_dir = os.path.join(current_app.config['OUTPUT_FOLDER'], session_id)
        
        if not os.path.exists(output_dir):
            return jsonify({'error': 'Session not found'}), 404
        
        # Look for any PDF file
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            # Try to find any PDF in the directory
            for f in os.listdir(output_dir):
                if f.endswith('.pdf'):
                    file_path = os.path.join(output_dir, f)
                    break
        
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
    from app.core.settings import QCSettings
    settings = QCSettings()
    return jsonify(settings.to_dict())


@main_bp.route('/api/source/<file_type>')
def download_source(file_type):
    """Download source code files"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # For development modal, always use TextileQC_Analysis.py from root
        if file_type == 'py':
            file_path = os.path.join(project_root, 'TextileQC_Analysis.py')
            download_name = 'TextileQC_Analysis.py'
            mime_type = 'text/x-python'
        else:
            # For other requests (like help dialog), use SOURCEDOWN folder
            source_dir = os.path.join(project_root, 'SOURCEDOWN')
            if not os.path.exists(source_dir):
                return jsonify({'error': 'Source folder not found'}), 404
            
            file_mapping = {
                'ipynb': ('TEXCOLAB.ipynb', 'TextileQC_Analysis.ipynb')
            }
            
            if file_type not in file_mapping:
                return jsonify({'error': 'Invalid file type'}), 400
            
            source_file, download_name = file_mapping[file_type]
            file_path = os.path.join(source_dir, source_file)
            mime_type = 'application/x-ipynb+json'
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found'}), 404
        
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"Source download error: {str(e)}")
        return jsonify({'error': 'Failed to download source file'}), 500

@main_bp.route('/api/source/textileqc/raw')
def get_textileqc_source_raw():
    """Get TextileQC_Analysis.py content as text"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, 'TextileQC_Analysis.py')
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return Response(content, mimetype='text/plain; charset=utf-8')
        
    except Exception as e:
        logger.error(f"Source read error: {str(e)}")
        return jsonify({'error': 'Failed to read source file'}), 500


# ==========================================
# Sample Tests Routes
# ==========================================
@main_bp.route('/api/samples/image/<image_name>')
def get_sample_image(image_name):
    """Serve sample images from Samples/images folder"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        samples_dir = os.path.join(project_root, 'Samples', 'images')
        
        if not os.path.exists(samples_dir):
            return jsonify({'error': 'Samples folder not found'}), 404
        
        # Add .png extension if not present
        if not image_name.endswith('.png'):
            image_name = f'{image_name}.png'
        
        file_path = os.path.join(samples_dir, image_name)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Sample image not found'}), 404
        
        return send_from_directory(samples_dir, image_name)
        
    except Exception as e:
        logger.error(f"Sample image error: {str(e)}")
        return jsonify({'error': 'Failed to serve sample image'}), 500


@main_bp.route('/api/samples/report/<int:sample_num>')
def download_sample_report(sample_num):
    """Download pre-generated sample reports with language selection"""
    try:
        # Get language parameter (default to 'en')
        language = request.args.get('lang', 'en')
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(project_root, 'Samples', 'REPORTS')
        
        if not os.path.exists(reports_dir):
            return jsonify({'error': 'Reports folder not found'}), 404
        
        # Map sample number to report file based on language
        if language == 'tr':
            report_filename = f'REPORTtr{sample_num}.pdf'
            download_name = f'TextileQC_Sample{sample_num}_Report_Turkish.pdf'
        else:
            report_filename = f'REPORT{sample_num}.pdf'
            download_name = f'TextileQC_Sample{sample_num}_Report.pdf'
        
        file_path = os.path.join(reports_dir, report_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'Report {sample_num} in {language} not found'}), 404
        
        logger.info(f"Downloading sample report: {report_filename}")
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"Sample report download error: {str(e)}")
        return jsonify({'error': 'Failed to download sample report'}), 500


@main_bp.route('/api/download/logo/<logo_name>')
def download_logo(logo_name):
    """Download logo images"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        images_dir = os.path.join(project_root, 'static', 'images')
        
        # Allowed logo filenames
        allowed_logos = [
            'logo_square_with_name_1024x1024.png',
            'logo_vertical_512x256.png',
            'logo_square_no_name_1024x1024.png'
        ]
        
        # Add .png extension if not present
        if not logo_name.endswith('.png'):
            logo_name = f'{logo_name}.png'
        
        if logo_name not in allowed_logos:
            return jsonify({'error': 'Invalid logo name'}), 400
        
        file_path = os.path.join(images_dir, logo_name)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Logo not found'}), 404
        
        logger.info(f"Downloading logo: {logo_name}")
        
        return send_file(
            file_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=logo_name
        )
        
    except Exception as e:
        logger.error(f"Logo download error: {str(e)}")
        return jsonify({'error': 'Failed to download logo'}), 500


@main_bp.route('/api/download/datasheet/<lang>')
def download_datasheet(lang):
    """Download datasheet PDF files"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        datasheets_dir = os.path.join(project_root, 'DataSheets')
        
        if not os.path.exists(datasheets_dir):
            return jsonify({'error': 'DataSheets folder not found'}), 404
        
        # Map language to filename
        if lang == 'en':
            filename = 'Datasheet EN.pdf'
            download_name = 'TextileQC_Datasheet_EN.pdf'
        elif lang == 'tr':
            filename = 'Datasheet TR.pdf'
            download_name = 'TextileQC_Datasheet_TR.pdf'
        else:
            return jsonify({'error': 'Invalid language'}), 400
        
        file_path = os.path.join(datasheets_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'Datasheet {lang} not found'}), 404
        
        logger.info(f"Downloading datasheet: {filename}")
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"Datasheet download error: {str(e)}")
        return jsonify({'error': 'Failed to download datasheet'}), 500


@main_bp.route('/api/samples/list')
def get_samples_list():
    """Get list of available sample tests"""
    samples = [
        {
            'id': 1,
            'name': 'Sample 1',
            'reference': '0011',
            'sample': '0012',
            'report': 'REPORT1.pdf'
        },
        {
            'id': 2,
            'name': 'Sample 2',
            'reference': '0021',
            'sample': '0022',
            'report': 'REPORT2.pdf'
        },
        {
            'id': 3,
            'name': 'Sample 3',
            'reference': '0031',
            'sample': '0032',
            'report': 'REPORT3.pdf'
        }
    ]
    return jsonify(samples)