# Textile QC System - Web Application

Professional Color & Pattern Analysis System for Textile Quality Control.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

- **Color Analysis**: Multiple ΔE formulas (ΔE76, ΔE94, ΔE2000, CMC)
- **Pattern Analysis**: SSIM, FFT, Gabor, GLCM, LBP, Wavelet analysis
- **Pattern Repetition**: Blob detection, keypoint matching, autocorrelation
- **Interactive UI**: Split-screen image viewer with synchronized circle overlay
- **PDF Reports**: Professional A4 reports with comprehensive analysis
- **Configurable**: Advanced settings for all analysis parameters

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   cd textile_qc_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## Deployment on Render.com

### Step 1: Prepare Repository

1. Create a new GitHub repository
2. Push all files to the repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/textile-qc-app.git
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `textile-qc-app`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Click **"Create Web Service"**
6. Wait for deployment (5-10 minutes)
7. Access your app at `https://textile-qc-app.onrender.com`

### Environment Variables (Optional)

Set these in Render dashboard if needed:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `FLASK_DEBUG` | Debug mode | `false` |

## Project Structure

```
textile_qc_app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py             # API endpoints
│   ├── core/                 # Core utilities
│   ├── analysis/             # Analysis modules
│   │   ├── color/            # Color analysis
│   │   ├── pattern/          # Pattern analysis
│   │   └── repetition/       # Repetition analysis
│   ├── visualization/        # Chart generation
│   ├── report/               # PDF generation
│   └── pipeline/             # Main pipeline
├── static/
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript
│   └── images/               # Logos
├── templates/                # HTML templates
├── uploads/                  # Uploaded images
├── outputs/                  # Generated reports
├── run.py                    # Entry point
├── requirements.txt          # Dependencies
└── render.yaml               # Render config
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/api/health` | GET | Health check |
| `/api/upload` | POST | Upload images |
| `/api/analyze` | POST | Run analysis |
| `/api/download/<id>/<file>` | GET | Download report |
| `/api/settings/default` | GET | Get default settings |

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Analysis**: NumPy, OpenCV, scikit-image, PyWavelets
- **PDF**: ReportLab
- **Charts**: Matplotlib
- **Deployment**: Gunicorn, Render.com

## Author

Textile Engineering Solutions

## License

MIT License - See LICENSE file for details.

