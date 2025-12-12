# -*- coding: utf-8 -*-
"""
Main PDF report builder
"""
import os
import tempfile
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image as RLImage, Table, TableStyle,
    Spacer, PageBreak, KeepTogether
)

from app.core.constants import (
    PAGE_SIZE, MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B,
    BLUE1, BLUE2, GREEN, RED, ORANGE, NEUTRAL, NEUTRAL_L, NEUTRAL_DARK,
    SOFTWARE_VERSION, COMPANY_NAME, REPORT_TITLE, PRIMARY_LOGO
)
from app.report.styles import get_paragraph_styles
from app.report.components import make_table, badge, fmt_pct, fmt2, fmt1


def get_local_time(timezone_offset=None):
    """Get local time with timezone offset"""
    if timezone_offset is None:
        timezone_offset = 0
    return datetime.utcnow() + timedelta(hours=timezone_offset)


def make_header_footer(report_timestamp=None, analysis_id=None):
    """Create header/footer function for PDF"""
    
    def header_footer(canvas, doc):
        canvas.saveState()
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(NEUTRAL)
        
        # Left: Company name
        canvas.drawString(MARGIN_L, 25, COMPANY_NAME)
        
        # Center: Page number
        page_num = f"Page {doc.page}"
        canvas.drawCentredString(PAGE_SIZE[0] / 2, 25, page_num)
        
        # Right: Version
        canvas.drawRightString(PAGE_SIZE[0] - MARGIN_R, 25, f"v{SOFTWARE_VERSION}")
        
        # Header line
        canvas.setStrokeColor(NEUTRAL_L)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_L, PAGE_SIZE[1] - MARGIN_T + 10, 
                   PAGE_SIZE[0] - MARGIN_R, PAGE_SIZE[1] - MARGIN_T + 10)
        
        canvas.restoreState()
    
    return header_footer


def build_main_report(analysis_results, settings, output_dir):
    """
    Build the main PDF report.
    
    Args:
        analysis_results: Dictionary containing all analysis results
        settings: QCSettings object
        output_dir: Output directory for the PDF
        
    Returns:
        str: Path to generated PDF
    """
    # Generate filename
    timestamp = get_local_time(settings.timezone_offset_hours)
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    analysis_id = f"TQC-{timestamp_str}"
    
    pdf_filename = f"TextileQC_Report_{timestamp_str}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    # Create document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=MARGIN_T,
        bottomMargin=MARGIN_B
    )
    
    # Get styles
    styles = get_paragraph_styles()
    
    # Build elements
    elements = []
    
    # === COVER PAGE ===
    elements.append(Spacer(1, 50))
    elements.append(Paragraph(f"<b>{REPORT_TITLE}</b>", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(COMPANY_NAME, styles['Subtitle']))
    elements.append(Spacer(1, 30))
    
    # Analysis info
    info_data = [
        ["Analysis ID", analysis_id],
        ["Date/Time", timestamp.strftime("%Y-%m-%d %H:%M:%S")],
        ["Operator", settings.operator_name],
        ["Reference", os.path.basename(analysis_results.get('ref_path', 'N/A'))],
        ["Sample", os.path.basename(analysis_results.get('test_path', 'N/A'))],
    ]
    info_table = make_table(info_data, colWidths=[1.5*inch, 4*inch])
    elements.append(info_table)
    elements.append(Spacer(1, 30))
    
    # Executive summary
    elements.append(Paragraph("<b>Executive Summary</b>", styles['H1']))
    elements.append(Spacer(1, 10))
    
    # Decision badge
    decision = analysis_results.get('decision', 'N/A')
    decision_color = GREEN if decision == 'ACCEPT' else (ORANGE if 'CONDITIONAL' in decision else RED)
    
    summary_data = [
        ["Metric", "Value", "Status"],
        ["Color Score", fmt1(analysis_results.get('color_score', 0)), 
         "PASS" if analysis_results.get('color_score', 0) >= 70 else "FAIL"],
        ["Pattern Score", fmt1(analysis_results.get('pattern_score', 0)),
         "PASS" if analysis_results.get('pattern_score', 0) >= 90 else "FAIL"],
        ["Overall Score", fmt1(analysis_results.get('overall_score', 0)), ""],
        ["Decision", decision, decision],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 1.5*inch])
    summary_style = [
        ('BACKGROUND', (0, 0), (-1, 0), BLUE2),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, NEUTRAL_L),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    
    # Color status cells
    for i, row in enumerate(summary_data[1:], 1):
        status = row[2]
        if status == 'PASS' or status == 'ACCEPT':
            summary_style.append(('BACKGROUND', (2, i), (2, i), GREEN))
            summary_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
        elif status == 'FAIL' or status == 'REJECT':
            summary_style.append(('BACKGROUND', (2, i), (2, i), RED))
            summary_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
        elif 'CONDITIONAL' in status:
            summary_style.append(('BACKGROUND', (2, i), (2, i), ORANGE))
            summary_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
    
    summary_table.setStyle(TableStyle(summary_style))
    elements.append(summary_table)
    elements.append(PageBreak())
    
    # === COLOR UNIT ===
    if settings.enable_color_unit:
        elements.append(Paragraph("<b>Color Analysis Unit</b>", styles['H1']))
        elements.append(Spacer(1, 10))
        
        # Color metrics
        color_metrics = analysis_results.get('color_metrics', {})
        
        if settings.enable_color_measurements:
            elements.append(Paragraph("Color Difference Summary", styles['H2']))
            
            de_data = [
                ["Metric", "Mean", "Std", "Min", "Max"],
                ["ΔE76", fmt2(color_metrics.get('mean_de76', 0)), 
                 fmt2(color_metrics.get('std_de76', 0)),
                 fmt2(color_metrics.get('min_de76', 0)),
                 fmt2(color_metrics.get('max_de76', 0))],
                ["ΔE94", fmt2(color_metrics.get('mean_de94', 0)),
                 fmt2(color_metrics.get('std_de94', 0)),
                 fmt2(color_metrics.get('min_de94', 0)),
                 fmt2(color_metrics.get('max_de94', 0))],
                ["ΔE2000", fmt2(color_metrics.get('mean_de2000', 0)),
                 fmt2(color_metrics.get('std_de2000', 0)),
                 fmt2(color_metrics.get('min_de2000', 0)),
                 fmt2(color_metrics.get('max_de2000', 0))],
            ]
            
            de_table = make_table(de_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            elements.append(de_table)
            elements.append(Spacer(1, 15))
        
        # Add images if available
        if 'charts' in analysis_results:
            charts = analysis_results['charts']
            
            if 'de_heatmap' in charts and os.path.exists(charts['de_heatmap']):
                elements.append(Paragraph("ΔE Heatmap", styles['H3']))
                elements.append(RLImage(charts['de_heatmap'], width=4*inch, height=3*inch))
                elements.append(Spacer(1, 10))
            
            if 'ab_scatter' in charts and os.path.exists(charts['ab_scatter']):
                elements.append(Paragraph("a*b* Chromaticity", styles['H3']))
                elements.append(RLImage(charts['ab_scatter'], width=3.5*inch, height=3.5*inch))
                elements.append(Spacer(1, 10))
        
        elements.append(PageBreak())
    
    # === PATTERN UNIT ===
    if settings.enable_pattern_unit:
        elements.append(Paragraph("<b>Pattern Analysis Unit</b>", styles['H1']))
        elements.append(Spacer(1, 10))
        
        pattern_metrics = analysis_results.get('pattern_metrics', {})
        
        pattern_data = [
            ["Metric", "Value", "Status"],
            ["SSIM", fmt_pct(pattern_metrics.get('ssim', 0) * 100),
             "PASS" if pattern_metrics.get('ssim', 0) >= 0.95 else "CONDITIONAL"],
            ["Symmetry", fmt_pct(pattern_metrics.get('symmetry', 0)), ""],
            ["Edge Definition", fmt1(pattern_metrics.get('edge_definition', 0)), ""],
        ]
        
        pattern_table = make_table(pattern_data, colWidths=[2*inch, 2*inch, 1.5*inch])
        elements.append(pattern_table)
        elements.append(Spacer(1, 15))
        
        elements.append(PageBreak())
    
    # === PATTERN REPETITION UNIT ===
    if settings.enable_pattern_repetition:
        repetition = analysis_results.get('pattern_repetition', {})
        
        if repetition:
            elements.append(Paragraph("<b>Pattern Repetition Analysis</b>", styles['H1']))
            elements.append(Spacer(1, 10))
            
            rep_data = [
                ["Metric", "Reference", "Sample", "Difference"],
                ["Pattern Count", 
                 str(repetition.get('count_ref', 0)),
                 str(repetition.get('count_test', 0)),
                 str(repetition.get('count_diff', 0))],
                ["Mean Area", 
                 fmt1(repetition.get('mean_area_ref', 0)),
                 fmt1(repetition.get('mean_area_test', 0)),
                 ""],
            ]
            
            rep_table = make_table(rep_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
            elements.append(rep_table)
            elements.append(Spacer(1, 15))
            
            elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements, onFirstPage=make_header_footer(timestamp, analysis_id),
              onLaterPages=make_header_footer(timestamp, analysis_id))
    
    return pdf_path

