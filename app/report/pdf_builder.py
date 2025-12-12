# -*- coding: utf-8 -*-
"""
Comprehensive PDF Report Builder - Robust Version
Generates professional textile QC reports with proper error handling
"""
import os
import math
import logging
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image as RLImage, Table, TableStyle,
    Spacer, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

logger = logging.getLogger(__name__)

# Import constants with fallbacks
try:
    from app.core.constants import (
        PAGE_SIZE, MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B,
        BLUE1, BLUE2, GREEN, RED, ORANGE, NEUTRAL, NEUTRAL_L, NEUTRAL_DARK,
        SOFTWARE_VERSION, COMPANY_NAME, COMPANY_SUBTITLE, REPORT_TITLE,
        PRIMARY_LOGO, FALLBACK_LOGOS, FRAME_MARGIN
    )
except ImportError:
    PAGE_SIZE = A4
    MARGIN_L = MARGIN_R = MARGIN_T = MARGIN_B = 50
    BLUE1 = colors.HexColor("#2980B9")
    BLUE2 = colors.HexColor("#3498DB")
    GREEN = colors.HexColor("#27AE60")
    RED = colors.HexColor("#E74C3C")
    ORANGE = colors.HexColor("#F39C12")
    NEUTRAL = colors.HexColor("#7F8C8D")
    NEUTRAL_L = colors.HexColor("#BDC3C7")
    NEUTRAL_DARK = colors.HexColor("#2C3E50")
    SOFTWARE_VERSION = "2.0.0"
    COMPANY_NAME = "Textile Engineering Solutions"
    COMPANY_SUBTITLE = "Professional Color Analysis Solutions"
    REPORT_TITLE = "Color Analysis Report"
    PRIMARY_LOGO = "logo_square_with_name_1024x1024.png"
    FALLBACK_LOGOS = []
    FRAME_MARGIN = 9

try:
    from app.report.styles import get_paragraph_styles
except ImportError:
    def get_paragraph_styles():
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()
        return {
            'Title': styles['Title'],
            'H1': styles['Heading1'],
            'H2': styles['Heading2'],
            'H3': styles['Heading3'],
            'Body': styles['BodyText'],
            'Small': styles['BodyText'],
            'Subtitle': styles['BodyText']
        }

try:
    from app.report.components import make_table, fmt_pct, fmt2, fmt1
except ImportError:
    def make_table(data, colWidths=None):
        t = Table(data, colWidths=colWidths)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#BDC3C7")),
        ]))
        return t
    def fmt_pct(x): return f"{x:.1f}%"
    def fmt2(x): return f"{x:.2f}"
    def fmt1(x): return f"{x:.1f}"


def get_local_time(timezone_offset=None):
    """Get local time with timezone offset"""
    if timezone_offset is None:
        timezone_offset = 0
    return datetime.utcnow() + timedelta(hours=timezone_offset)


def pick_logo():
    """Find and return available logo path"""
    search_paths = [
        os.path.join('static', 'images', PRIMARY_LOGO),
        os.path.join('static', 'images', 'logo_square_with_name_1024x1024.png'),
        os.path.join('static', 'images', 'logo_square_no_name_1024x1024.png'),
        os.path.join('static', 'images', 'logo_vertical_512x256.png'),
        PRIMARY_LOGO,
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    return None


def safe_image(path, width, height):
    """Safely load an image, returning None if it fails"""
    try:
        if path and os.path.exists(path):
            return RLImage(path, width=width, height=height)
    except Exception as e:
        logger.warning(f"Failed to load image {path}: {e}")
    return None


def make_header_footer(report_timestamp=None, analysis_id=None):
    """Create header/footer function"""
    
    def header_footer(canvas, doc):
        try:
            canvas.saveState()
            width, height = PAGE_SIZE
            
            # Frame
            canvas.setStrokeColor(colors.HexColor("#E0E0E0"))
            canvas.setLineWidth(0.8)
            canvas.rect(FRAME_MARGIN, FRAME_MARGIN, 
                       width - 2*FRAME_MARGIN, height - 2*FRAME_MARGIN, 
                       stroke=1, fill=0)
            
            # Header
            y = height - 40
            canvas.setStrokeColor(NEUTRAL_L)
            canvas.setLineWidth(0.6)
            canvas.line(MARGIN_L, y, width - MARGIN_R, y)
            
            canvas.setFillColor(BLUE1)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(MARGIN_L, y + 10, COMPANY_NAME)
            
            # Footer
            fy = 35
            canvas.setStrokeColor(NEUTRAL_L)
            canvas.line(MARGIN_L, fy + 10, width - MARGIN_R, fy + 10)
            
            page_num = canvas.getPageNumber()
            if page_num >= 2:
                canvas.setFillColor(NEUTRAL)
                canvas.setFont("Helvetica", 9)
                canvas.drawRightString(width - MARGIN_R, fy - 2, f"Page {page_num}")
            
            canvas.restoreState()
        except Exception as e:
            logger.warning(f"Header/footer error: {e}")
    
    return header_footer


def build_comprehensive_report(analysis_results, settings, output_dir):
    """
    Build comprehensive PDF report with robust error handling.
    """
    logger.info("Starting PDF generation...")
    
    try:
        # Generate filename
        timestamp = get_local_time(getattr(settings, 'timezone_offset_hours', 0))
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        analysis_id = f"TQC-{timestamp_str}"
        
        pdf_filename = f"TextileQC_Report_{timestamp_str}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        logger.info(f"Creating PDF: {pdf_path}")
        
        # Create document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=PAGE_SIZE,
            leftMargin=MARGIN_L,
            rightMargin=MARGIN_R,
            topMargin=MARGIN_T,
            bottomMargin=MARGIN_B
        )
        
        styles = get_paragraph_styles()
        elements = []
        
        # ==================== COVER PAGE ====================
        logger.info("Building cover page...")
        try:
            build_cover_page(elements, analysis_results, settings, timestamp, analysis_id, styles)
        except Exception as e:
            logger.error(f"Cover page error: {e}")
            elements.append(Paragraph("<b>Textile QC Report</b>", styles['Title']))
            elements.append(PageBreak())
        
        # ==================== COLOR UNIT ====================
        if getattr(settings, 'enable_color_unit', True):
            logger.info("Building color unit...")
            try:
                build_color_unit(elements, analysis_results, settings, styles)
            except Exception as e:
                logger.error(f"Color unit error: {e}")
                elements.append(Paragraph("<b>Color Analysis</b>", styles['H1']))
                elements.append(Paragraph("Error generating color analysis section.", styles['Body']))
                elements.append(PageBreak())
        
        # ==================== PATTERN UNIT ====================
        if getattr(settings, 'enable_pattern_unit', True):
            logger.info("Building pattern unit...")
            try:
                build_pattern_unit(elements, analysis_results, settings, styles)
            except Exception as e:
                logger.error(f"Pattern unit error: {e}")
                elements.append(Paragraph("<b>Pattern Analysis</b>", styles['H1']))
                elements.append(Paragraph("Error generating pattern analysis section.", styles['Body']))
                elements.append(PageBreak())
        
        # ==================== PATTERN REPETITION ====================
        if getattr(settings, 'enable_pattern_repetition', True) and 'pattern_repetition' in analysis_results:
            logger.info("Building repetition unit...")
            try:
                build_repetition_unit(elements, analysis_results, settings, styles)
            except Exception as e:
                logger.error(f"Repetition unit error: {e}")
        
        # ==================== SPECTROPHOTOMETER ====================
        if getattr(settings, 'enable_spectrophotometer', True) and 'spectrophotometer' in analysis_results:
            logger.info("Building spectrophotometer unit...")
            try:
                build_spectrophotometer_unit(elements, analysis_results, settings, styles)
            except Exception as e:
                logger.error(f"Spectrophotometer unit error: {e}")
        
        # Build PDF
        logger.info("Finalizing PDF document...")
        doc.build(
            elements,
            onFirstPage=make_header_footer(timestamp, analysis_id),
            onLaterPages=make_header_footer(timestamp, analysis_id)
        )
        
        logger.info(f"PDF created successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        # Create a minimal fallback PDF
        return create_fallback_pdf(analysis_results, settings, output_dir)


def create_fallback_pdf(results, settings, output_dir):
    """Create a minimal PDF if main generation fails"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"TextileQC_Report_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = get_paragraph_styles()
        
        elements = [
            Spacer(1, 100),
            Paragraph("<b>Textile Quality Control Report</b>", styles['Title']),
            Spacer(1, 30),
            Paragraph(f"<b>Decision:</b> {results.get('decision', 'N/A')}", styles['Body']),
            Spacer(1, 10),
            Paragraph(f"<b>Color Score:</b> {results.get('color_score', 0):.1f}/100", styles['Body']),
            Paragraph(f"<b>Pattern Score:</b> {results.get('pattern_score', 0):.1f}/100", styles['Body']),
            Paragraph(f"<b>Overall Score:</b> {results.get('overall_score', 0):.1f}/100", styles['Body']),
            Spacer(1, 30),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Body']),
        ]
        
        doc.build(elements)
        logger.info(f"Fallback PDF created: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Fallback PDF failed: {e}")
        # Return a path even if it doesn't exist
        return os.path.join(output_dir, f"TextileQC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")


def build_cover_page(elements, results, settings, timestamp, analysis_id, styles):
    """Build cover page with executive summary"""
    
    # Logo
    logo_path = pick_logo()
    if logo_path:
        img = safe_image(logo_path, 1.5*inch, 1.5*inch)
        if img:
            elements.append(img)
            elements.append(Spacer(1, 15))
    
    # Title
    elements.append(Paragraph(f"<font color='#2980B9'><b>{COMPANY_NAME}</b></font>", styles['Title']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"<b>{REPORT_TITLE}</b>", styles['H1']))
    elements.append(Spacer(1, 20))
    
    # Metadata
    nice_date = timestamp.strftime("%B %d, %Y at %I:%M %p")
    meta_data = [
        ["Report Information", ""],
        ["Date", nice_date],
        ["Analysis ID", analysis_id],
        ["Operator", getattr(settings, 'operator_name', 'Operator')],
        ["Version", SOFTWARE_VERSION],
    ]
    
    meta_table = make_table(meta_data, colWidths=[1.8*inch, 4*inch])
    elements.append(meta_table)
    elements.append(Spacer(1, 25))
    
    # Executive Summary
    decision = results.get('decision', 'N/A')
    color_score = results.get('color_score', 0)
    pattern_score = results.get('pattern_score', 0)
    overall_score = results.get('overall_score', 0)
    
    # Determine colors
    decision_color = GREEN if decision == 'ACCEPT' else (ORANGE if 'CONDITIONAL' in decision else RED)
    
    elements.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", styles['H2']))
    elements.append(Spacer(1, 10))
    
    # Summary table
    summary_data = [
        ["Metric", "Score", "Status"],
        ["Color Score", f"{color_score:.1f}/100", "PASS" if color_score >= 70 else "FAIL"],
        ["Pattern Score", f"{pattern_score:.1f}/100", "PASS" if pattern_score >= 90 else "FAIL"],
        ["Overall Score", f"{overall_score:.1f}/100", decision],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    summary_style = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE2),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, NEUTRAL_L),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]
    
    # Color code status cells
    for i in range(1, len(summary_data)):
        status = summary_data[i][2]
        if "PASS" in status or "ACCEPT" in status:
            summary_style.append(("BACKGROUND", (2, i), (2, i), GREEN))
            summary_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
        elif "CONDITIONAL" in status:
            summary_style.append(("BACKGROUND", (2, i), (2, i), ORANGE))
            summary_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
        elif "FAIL" in status or "REJECT" in status:
            summary_style.append(("BACKGROUND", (2, i), (2, i), RED))
            summary_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
    
    summary_table.setStyle(TableStyle(summary_style))
    elements.append(summary_table)
    elements.append(PageBreak())


def build_color_unit(elements, results, settings, styles):
    """Build color analysis section"""
    elements.append(Paragraph("<b>Color Analysis Unit</b>", styles['H1']))
    elements.append(Spacer(1, 10))
    
    color_metrics = results.get('color_metrics', {})
    charts = results.get('charts', {})
    regional_samples = results.get('regional_samples', [])
    
    # Color Difference Summary
    elements.append(Paragraph("Color Difference Summary", styles['H2']))
    elements.append(Spacer(1, 5))
    
    de_data = [
        ["Metric", "Mean", "Std Dev", "Min", "Max"],
        ["ΔE76", fmt2(color_metrics.get('mean_de76', 0)), 
         fmt2(color_metrics.get('std_de76', 0)),
         fmt2(color_metrics.get('min_de76', 0)),
         fmt2(color_metrics.get('max_de76', 0))],
        ["ΔE2000", fmt2(color_metrics.get('mean_de2000', 0)),
         fmt2(color_metrics.get('std_de2000', 0)),
         fmt2(color_metrics.get('min_de2000', 0)),
         fmt2(color_metrics.get('max_de2000', 0))],
    ]
    
    de_table = make_table(de_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    elements.append(de_table)
    elements.append(Spacer(1, 15))
    
    # Interpretation
    mean_de = color_metrics.get('mean_de2000', 0)
    if mean_de < 1.0:
        interp = "Not perceptible difference"
    elif mean_de < 2.0:
        interp = "Perceptible through close observation"
    elif mean_de < 3.5:
        interp = "Perceptible at a glance"
    else:
        interp = "Significant color difference"
    
    elements.append(Paragraph(f"<i>Interpretation: {interp}</i>", styles['Body']))
    elements.append(Spacer(1, 15))
    
    # Regional Samples
    if regional_samples:
        elements.append(Paragraph("Regional Color Analysis", styles['H2']))
        elements.append(Spacer(1, 5))
        
        sample_data = [["Region", "Position", "ΔE76", "ΔE2000", "Status"]]
        for sample in regional_samples[:5]:
            de00 = sample.get('de00', 0)
            status = "PASS" if de00 < 2.0 else ("CONDITIONAL" if de00 <= 3.5 else "FAIL")
            sample_data.append([
                str(sample.get('region', 0)),
                f"({sample.get('x', 0)}, {sample.get('y', 0)})",
                fmt2(sample.get('de76', 0)),
                fmt2(de00),
                status
            ])
        
        sample_table = make_table(sample_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
        elements.append(sample_table)
        elements.append(Spacer(1, 15))
    
    # Charts
    if 'de_heatmap' in charts:
        img = safe_image(charts['de_heatmap'], 4*inch, 3*inch)
        if img:
            elements.append(Paragraph("ΔE Heatmap", styles['H3']))
            elements.append(img)
            elements.append(Spacer(1, 10))
    
    if 'ab_scatter' in charts:
        img = safe_image(charts['ab_scatter'], 3*inch, 3*inch)
        if img:
            elements.append(Paragraph("a*b* Chromaticity Diagram", styles['H3']))
            elements.append(img)
            elements.append(Spacer(1, 10))
    
    elements.append(PageBreak())


def build_pattern_unit(elements, results, settings, styles):
    """Build pattern analysis section"""
    elements.append(Paragraph("<b>Pattern Analysis Unit</b>", styles['H1']))
    elements.append(Spacer(1, 10))
    
    pattern_metrics = results.get('pattern_metrics', {})
    charts = results.get('charts', {})
    
    # Pattern Metrics
    ssim_val = pattern_metrics.get('ssim', 0)
    ssim_status = "PASS" if ssim_val >= 0.95 else ("CONDITIONAL" if ssim_val >= 0.90 else "FAIL")
    
    pattern_data = [
        ["Metric", "Value", "Status"],
        ["SSIM Score", fmt_pct(ssim_val * 100), ssim_status],
        ["Symmetry", fmt_pct(pattern_metrics.get('symmetry', 0)), ""],
        ["Edge Definition", fmt1(pattern_metrics.get('edge_definition', 0)), ""],
    ]
    
    pattern_table = make_table(pattern_data, colWidths=[2*inch, 2*inch, 1.5*inch])
    elements.append(pattern_table)
    elements.append(Spacer(1, 15))
    
    # Charts
    for chart_name, chart_title in [
        ('fft_spectrum', 'FFT Power Spectrum'),
        ('glcm_radar', 'GLCM Texture Features'),
        ('lbp_map', 'Local Binary Patterns'),
    ]:
        if chart_name in charts:
            img = safe_image(charts[chart_name], 4*inch, 3*inch)
            if img:
                elements.append(Paragraph(chart_title, styles['H3']))
                elements.append(img)
                elements.append(Spacer(1, 10))
    
    elements.append(PageBreak())


def build_repetition_unit(elements, results, settings, styles):
    """Build pattern repetition section"""
    elements.append(Paragraph("<b>Pattern Repetition Analysis</b>", styles['H1']))
    elements.append(Spacer(1, 10))
    
    rep = results.get('pattern_repetition', {})
    charts = results.get('charts', {})
    
    # Summary
    rep_data = [
        ["Metric", "Reference", "Sample", "Difference"],
        ["Pattern Count", str(rep.get('count_ref', 0)), str(rep.get('count_test', 0)), 
         str(rep.get('count_diff', 0))],
        ["Mean Area (px²)", fmt1(rep.get('mean_area_ref', 0)), fmt1(rep.get('mean_area_test', 0)), ""],
    ]
    
    rep_table = make_table(rep_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    elements.append(rep_table)
    elements.append(Spacer(1, 15))
    
    # Charts
    if 'pattern_count' in charts:
        img = safe_image(charts['pattern_count'], 4*inch, 3*inch)
        if img:
            elements.append(img)
            elements.append(Spacer(1, 10))
    
    elements.append(PageBreak())


def build_spectrophotometer_unit(elements, results, settings, styles):
    """Build spectrophotometer section"""
    elements.append(Paragraph("<b>Spectrophotometer Analysis</b>", styles['H1']))
    elements.append(Spacer(1, 10))
    
    spectro = results.get('spectrophotometer', {})
    charts = results.get('charts', {})
    
    # Whiteness/Yellowness
    white_data = [
        ["Index", "Reference", "Sample"],
        ["Whiteness", fmt2(spectro.get('whiteness_ref', 0)), fmt2(spectro.get('whiteness_test', 0))],
        ["Yellowness", fmt2(spectro.get('yellowness_ref', 0)), fmt2(spectro.get('yellowness_test', 0))],
    ]
    
    white_table = make_table(white_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    elements.append(white_table)
    elements.append(Spacer(1, 15))
    
    # Metamerism
    if spectro.get('metamerism'):
        elements.append(Paragraph("Metamerism Analysis", styles['H2']))
        elements.append(Spacer(1, 5))
        
        meta_data = [["Illuminant", "ΔE2000", "Status"]]
        for m in spectro['metamerism']:
            de = m.get('delta_e', 0)
            status = "PASS" if de < 2.0 else ("CONDITIONAL" if de <= 3.5 else "FAIL")
            meta_data.append([m.get('illuminant', ''), fmt2(de), status])
        
        meta_table = make_table(meta_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        elements.append(meta_table)
        
        if 'metamerism' in charts:
            img = safe_image(charts['metamerism'], 4*inch, 3*inch)
            if img:
                elements.append(Spacer(1, 10))
                elements.append(img)


# Backwards compatibility
build_main_report = build_comprehensive_report
