# -*- coding: utf-8 -*-
"""
Comprehensive PDF Report Builder
Generates professional textile QC reports matching PDFSAMPLE.py format
"""
import os
import math
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image as RLImage, Table, TableStyle,
    Spacer, PageBreak, KeepTogether, Flowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from app.core.constants import (
    PAGE_SIZE, MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B,
    BLUE1, BLUE2, GREEN, RED, ORANGE, NEUTRAL, NEUTRAL_L, NEUTRAL_DARK,
    SOFTWARE_VERSION, COMPANY_NAME, COMPANY_SUBTITLE, REPORT_TITLE,
    PRIMARY_LOGO, FALLBACK_LOGOS, FRAME_MARGIN
)
from app.report.styles import get_paragraph_styles
from app.report.components import make_table, badge, fmt_pct, fmt2, fmt1


def get_local_time(timezone_offset=None):
    """Get local time with timezone offset"""
    if timezone_offset is None:
        timezone_offset = 0
    return datetime.utcnow() + timedelta(hours=timezone_offset)


def pick_logo():
    """Find and return available logo path"""
    # Check in static/images first
    static_paths = [
        os.path.join('static', 'images', PRIMARY_LOGO),
        os.path.join('static', 'images', 'logo_square_with_name_1024x1024.png'),
        os.path.join('static', 'images', 'logo_square_no_name_1024x1024.png'),
    ]
    
    for path in static_paths:
        if os.path.exists(path):
            return path
    
    # Check current directory
    if os.path.exists(PRIMARY_LOGO):
        return PRIMARY_LOGO
    
    for logo in FALLBACK_LOGOS:
        if os.path.exists(logo):
            return logo
    
    return None


def make_header_footer(report_timestamp=None, analysis_id=None):
    """Create header/footer function with professional styling"""
    
    def header_footer(canvas, doc):
        canvas.saveState()
        width, height = PAGE_SIZE
        
        # Frame around page
        canvas.setStrokeColor(colors.HexColor("#E0E0E0"))
        canvas.setLineWidth(0.8)
        canvas.rect(FRAME_MARGIN, FRAME_MARGIN, 
                   width - 2*FRAME_MARGIN, height - 2*FRAME_MARGIN, 
                   stroke=1, fill=0)
        
        # Header line
        y = height - 40
        canvas.setStrokeColor(NEUTRAL_L)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN_L, y, width - MARGIN_R, y)
        
        # Company name (blue, bold)
        canvas.setFillColor(BLUE1)
        canvas.setFont("Helvetica-Bold", 10.5)
        canvas.drawString(MARGIN_L, y + 10, COMPANY_NAME)
        
        # Pipe separator
        company_width = canvas.stringWidth(COMPANY_NAME, "Helvetica-Bold", 10.5)
        canvas.setFillColor(colors.black)
        canvas.drawString(MARGIN_L + company_width + 5, y + 10, " | ")
        
        # Subtitle (gray, smaller)
        pipe_width = canvas.stringWidth(" | ", "Helvetica-Bold", 10.5)
        canvas.setFillColor(NEUTRAL)
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(MARGIN_L + company_width + pipe_width + 5, y + 10, COMPANY_SUBTITLE)
        
        # Timestamp on right
        if report_timestamp:
            timestamp_str = report_timestamp.strftime("%Y-%m-%d %H:%M")
            canvas.setFillColor(NEUTRAL)
            canvas.setFont("Helvetica", 7)
            canvas.drawRightString(width - MARGIN_R, y + 10, f"Generated: {timestamp_str}")
        
        # Footer
        fy = 35
        canvas.setStrokeColor(NEUTRAL_L)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN_L, fy + 10, width - MARGIN_R, fy + 10)
        
        # Page number
        page_num = canvas.getPageNumber()
        if page_num >= 2:
            canvas.setFillColor(NEUTRAL)
            canvas.setFont("Helvetica", 9)
            page_text = f"Page {page_num}"
            if analysis_id:
                page_text = f"{analysis_id} | {page_text}"
            canvas.drawRightString(width - MARGIN_R, fy - 2, page_text)
        
        canvas.restoreState()
    
    return header_footer


def build_comprehensive_report(analysis_results, settings, output_dir):
    """
    Build comprehensive PDF report matching PDFSAMPLE.py format.
    
    Args:
        analysis_results: Complete analysis results dictionary
        settings: QCSettings object
        output_dir: Output directory
        
    Returns:
        str: Path to generated PDF
    """
    # Generate filename with timestamp
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
    
    # ==================== COVER PAGE ====================
    build_cover_page(elements, analysis_results, settings, timestamp, analysis_id, styles)
    
    # ==================== COLOR UNIT ====================
    if settings.enable_color_unit:
        build_color_unit(elements, analysis_results, settings, styles)
    
    # ==================== PATTERN UNIT ====================
    if settings.enable_pattern_unit:
        build_pattern_unit(elements, analysis_results, settings, styles)
    
    # ==================== PATTERN REPETITION UNIT ====================
    if settings.enable_pattern_repetition and 'pattern_repetition' in analysis_results:
        build_repetition_unit(elements, analysis_results, settings, styles)
    
    # ==================== SPECTROPHOTOMETER UNIT ====================
    if settings.enable_spectrophotometer and 'spectrophotometer' in analysis_results:
        build_spectrophotometer_unit(elements, analysis_results, settings, styles)
    
    # Build PDF
    doc.build(
        elements,
        onFirstPage=make_header_footer(timestamp, analysis_id),
        onLaterPages=make_header_footer(timestamp, analysis_id)
    )
    
    return pdf_path


def build_cover_page(elements, results, settings, timestamp, analysis_id, styles):
    """Build the cover page with executive summary"""
    
    # Logo
    logo_path = pick_logo()
    if logo_path and os.path.exists(logo_path):
        try:
            elements.append(RLImage(logo_path, width=1.8*inch, height=1.8*inch))
            elements.append(Spacer(1, 15))
        except:
            pass
    
    # Title
    elements.append(Paragraph(f"<font color='{BLUE1}'><b>{COMPANY_NAME}</b></font>", styles['Title']))
    elements.append(Paragraph(COMPANY_SUBTITLE, styles['Small']))
    elements.append(Spacer(1, 18))
    elements.append(Paragraph(f"<font color='{NEUTRAL_DARK}'><b>{REPORT_TITLE}</b></font>", 
                             ParagraphStyle("rt", parent=styles['Title'], fontSize=24)))
    elements.append(Spacer(1, 10))
    
    # Report metadata table
    nice_date = timestamp.strftime("%B %d, %Y at %I:%M %p")
    meta_data = [
        ["Report Metadata", ""],
        ["Report Date", nice_date],
        ["Operator", settings.operator_name],
        ["Analysis ID", analysis_id],
        ["Software Version", SOFTWARE_VERSION],
        ["Reference Image", os.path.basename(results.get('ref_path', 'N/A'))],
        ["Sample Image", os.path.basename(results.get('test_path', 'N/A'))],
    ]
    meta_table = make_table(meta_data, colWidths=[1.8*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 0), (1, 0), BLUE2),
        ("TEXTCOLOR", (0, 0), (1, 0), colors.white),
        ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (1, 0), "LEFT"),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # Executive Summary
    decision = results.get('decision', 'N/A')
    decision_color = GREEN if decision == 'ACCEPT' else (ORANGE if 'CONDITIONAL' in decision else RED)
    
    color_score = results.get('color_score', 0)
    pattern_score = results.get('pattern_score', 0)
    overall_score = results.get('overall_score', 0)
    
    # Status determination
    color_status = "PASS" if color_score >= settings.color_score_threshold else (
        "CONDITIONAL" if color_score >= settings.color_score_threshold * 0.8 else "FAIL")
    pattern_status = "PASS" if pattern_score >= settings.pattern_score_threshold else (
        "CONDITIONAL" if pattern_score >= settings.pattern_score_threshold * 0.8 else "FAIL")
    
    # Executive summary header
    exec_header = Paragraph(f"<b>📊 EXECUTIVE SUMMARY: {decision}</b>", 
                           ParagraphStyle("ExecHeader", fontSize=12, textColor=colors.white, alignment=TA_CENTER))
    
    exec_data = [
        ["Metric", "Score", "Status"],
        ["Color Score", f"{color_score:.1f}/100", color_status],
        ["Pattern Score (SSIM)", f"{pattern_score:.1f}/100", pattern_status],
    ]
    
    # Add color difference
    if 'color_metrics' in results:
        de2000 = results['color_metrics'].get('mean_de2000', 0)
        de_status = results['color_metrics'].get('status', 'N/A')
        exec_data.append(["ΔE2000 (Mean)", fmt2(de2000), de_status])
    
    # Add pattern repetition if enabled
    if settings.enable_pattern_repetition and 'pattern_repetition' in results:
        rep_status = results['pattern_repetition'].get('status', 'N/A')
        integrity = results['pattern_repetition'].get('integrity', {}).get('overall_integrity', 0)
        exec_data.append(["Pattern Repetition", f"{integrity:.1f}%", rep_status])
    
    exec_data.append(["Overall Score", f"{overall_score:.1f}/100", decision.split()[0]])
    
    exec_table = Table(exec_data, colWidths=[2.2*inch, 1.5*inch, 1.5*inch])
    exec_style = [
        ("BACKGROUND", (0, 0), (-1, 0), NEUTRAL_L),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    
    # Color-code status column
    for i in range(1, len(exec_data)):
        status_val = exec_data[i][2]
        if "PASS" in status_val or "ACCEPT" in status_val:
            exec_style.append(("BACKGROUND", (2, i), (2, i), GREEN))
            exec_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
        elif "CONDITIONAL" in status_val:
            exec_style.append(("BACKGROUND", (2, i), (2, i), ORANGE))
            exec_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
        elif "FAIL" in status_val or "REJECT" in status_val:
            exec_style.append(("BACKGROUND", (2, i), (2, i), RED))
            exec_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
    
    exec_table.setStyle(TableStyle(exec_style))
    
    # Wrap in colored box
    summary_wrapper = Table(
        [[exec_header], [Spacer(1, 6)], [exec_table]],
        colWidths=[5.5*inch]
    )
    summary_wrapper.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), decision_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(summary_wrapper)
    elements.append(PageBreak())


def build_color_unit(elements, results, settings, styles):
    """Build the Color Analysis Unit section"""
    elements.append(Paragraph("<b>Color Unit</b>", styles['H1']))
    elements.append(Spacer(1, 6))
    
    charts = results.get('charts', {})
    color_metrics = results.get('color_metrics', {})
    regional_samples = results.get('regional_samples', [])
    
    # A. Input Images
    if settings.enable_color_input_images:
        input_section = []
        input_section.append(Paragraph("Input Images", styles['H2']))
        
        # Try to add overlay images
        if 'overlay_ref' in charts and 'overlay_test' in charts:
            try:
                img_row = [[
                    RLImage(charts['overlay_ref'], width=2.5*inch, height=2*inch),
                    RLImage(charts['overlay_test'], width=2.5*inch, height=2*inch)
                ]]
                t_imgs = Table(img_row, colWidths=[2.7*inch, 2.7*inch])
                input_section.append(t_imgs)
            except:
                pass
        
        input_section.append(Spacer(1, 10))
        elements.append(KeepTogether(input_section))
    
    # B. Color Measurements (Regional Samples)
    if settings.enable_color_measurements and regional_samples:
        elements.append(Paragraph("Color Measurements", styles['H2']))
        elements.append(Paragraph("5-point regional analysis with Reference vs Sample comparison", styles['Small']))
        elements.append(Spacer(1, 4))
        
        # RGB Values Table
        rgb_section = []
        rgb_section.append(Paragraph("<b>RGB Color Values</b>", styles['Body']))
        
        rgb_data = [["Region", "Position", "Ref R", "Test R", "Ref G", "Test G", "Ref B", "Test B"]]
        for sample in regional_samples:
            rgb_data.append([
                str(sample['region']),
                f"({sample['x']}, {sample['y']})",
                str(int(sample['ref_rgb'][0])),
                str(int(sample['test_rgb'][0])),
                str(int(sample['ref_rgb'][1])),
                str(int(sample['test_rgb'][1])),
                str(int(sample['ref_rgb'][2])),
                str(int(sample['test_rgb'][2])),
            ])
        
        rgb_table = Table(rgb_data, colWidths=[0.6*inch, 0.9*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch])
        rgb_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE2),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, NEUTRAL_L),
            ("BACKGROUND", (2, 1), (3, -1), colors.HexColor("#FFE6E6")),
            ("BACKGROUND", (4, 1), (5, -1), colors.HexColor("#E6FFE6")),
            ("BACKGROUND", (6, 1), (7, -1), colors.HexColor("#E6E6FF")),
        ]))
        rgb_section.append(rgb_table)
        rgb_section.append(Spacer(1, 8))
        elements.append(KeepTogether(rgb_section))
        
        # LAB Values Table
        lab_section = []
        lab_section.append(Paragraph("<b>LAB* Color Space Values</b>", styles['Body']))
        
        lab_data = [["Region", "Ref L*", "Test L*", "Ref a*", "Test a*", "Ref b*", "Test b*"]]
        for sample in regional_samples:
            lab_data.append([
                str(sample['region']),
                fmt2(sample['ref_lab'][0]),
                fmt2(sample['test_lab'][0]),
                fmt2(sample['ref_lab'][1]),
                fmt2(sample['test_lab'][1]),
                fmt2(sample['ref_lab'][2]),
                fmt2(sample['test_lab'][2]),
            ])
        
        lab_table = Table(lab_data, colWidths=[0.6*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        lab_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE2),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, NEUTRAL_L),
        ]))
        lab_section.append(lab_table)
        lab_section.append(Spacer(1, 8))
        elements.append(KeepTogether(lab_section))
        
        # Delta E Table
        de_section = []
        de_section.append(Paragraph("<b>Color Difference Metrics</b>", styles['Body']))
        
        de_data = [["Region", "ΔE76", "ΔE94", "ΔE2000", "Status"]]
        for sample in regional_samples:
            de00 = sample['de00']
            status = "PASS" if de00 < 2.0 else ("CONDITIONAL" if de00 <= 3.5 else "FAIL")
            de_data.append([
                str(sample['region']),
                fmt2(sample['de76']),
                fmt2(sample['de94']),
                fmt2(sample['de00']),
                status
            ])
        
        de_table = Table(de_data, colWidths=[0.6*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        de_style = [
            ("BACKGROUND", (0, 0), (-1, 0), BLUE2),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, NEUTRAL_L),
        ]
        # Color status
        for i in range(1, len(de_data)):
            status = de_data[i][4]
            if status == "PASS":
                de_style.append(("BACKGROUND", (4, i), (4, i), GREEN))
                de_style.append(("TEXTCOLOR", (4, i), (4, i), colors.white))
            elif status == "CONDITIONAL":
                de_style.append(("BACKGROUND", (4, i), (4, i), ORANGE))
                de_style.append(("TEXTCOLOR", (4, i), (4, i), colors.white))
            else:
                de_style.append(("BACKGROUND", (4, i), (4, i), RED))
                de_style.append(("TEXTCOLOR", (4, i), (4, i), colors.white))
        
        de_table.setStyle(TableStyle(de_style))
        de_section.append(de_table)
        de_section.append(Spacer(1, 8))
        elements.append(KeepTogether(de_section))
    
    # C. Delta E Summary Statistics
    if color_metrics:
        summary_section = []
        summary_section.append(Paragraph("<b>ΔE Summary Statistics</b>", styles['Body']))
        
        de_overall_status = color_metrics.get('status', 'N/A')
        de_summary = [
            ["Metric", "Mean", "Std Dev", "Min", "Max", "Status"],
            ["ΔE76", fmt2(color_metrics.get('mean_de76', 0)), 
             fmt2(color_metrics.get('std_de76', 0)),
             fmt2(color_metrics.get('min_de76', 0)),
             fmt2(color_metrics.get('max_de76', 0)), ""],
            ["ΔE94", fmt2(color_metrics.get('mean_de94', 0)),
             fmt2(color_metrics.get('std_de94', 0)),
             fmt2(color_metrics.get('min_de94', 0)),
             fmt2(color_metrics.get('max_de94', 0)), ""],
            ["ΔE2000", fmt2(color_metrics.get('mean_de2000', 0)),
             fmt2(color_metrics.get('std_de2000', 0)),
             fmt2(color_metrics.get('min_de2000', 0)),
             fmt2(color_metrics.get('max_de2000', 0)), de_overall_status],
        ]
        
        summary_table = Table(de_summary, colWidths=[0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.2*inch])
        summary_style = [
            ("BACKGROUND", (0, 0), (-1, 0), NEUTRAL_L),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, NEUTRAL_L),
        ]
        # Color status cell
        if de_overall_status == "PASS":
            summary_style.append(("BACKGROUND", (5, 3), (5, 3), GREEN))
            summary_style.append(("TEXTCOLOR", (5, 3), (5, 3), colors.white))
        elif de_overall_status == "CONDITIONAL":
            summary_style.append(("BACKGROUND", (5, 3), (5, 3), ORANGE))
            summary_style.append(("TEXTCOLOR", (5, 3), (5, 3), colors.white))
        elif de_overall_status == "FAIL":
            summary_style.append(("BACKGROUND", (5, 3), (5, 3), RED))
            summary_style.append(("TEXTCOLOR", (5, 3), (5, 3), colors.white))
        
        summary_table.setStyle(TableStyle(summary_style))
        summary_section.append(summary_table)
        
        # Interpretation
        mean_de = color_metrics.get('mean_de2000', 0)
        interp = ("Not perceptible" if mean_de < 1.0 else
                 "Perceptible (close observation)" if mean_de < 2.0 else
                 "Perceptible at a glance" if mean_de < 3.5 else
                 "Clear difference" if mean_de < 5.0 else
                 "More different than similar")
        summary_section.append(Paragraph(f"<i>Interpretation: {interp}</i>", styles['Small']))
        summary_section.append(Spacer(1, 10))
        elements.append(KeepTogether(summary_section))
    
    # D. Visual Difference Analysis (Heatmap)
    if settings.enable_color_visual_diff and 'de_heatmap' in charts:
        visual_section = []
        visual_section.append(Paragraph("Visual Difference Analysis", styles['H2']))
        try:
            visual_section.append(RLImage(charts['de_heatmap'], width=4.5*inch, height=3*inch))
        except:
            pass
        visual_section.append(Spacer(1, 10))
        elements.append(KeepTogether(visual_section))
    
    # E. LAB Detailed Analysis
    if settings.enable_color_lab_detailed and color_metrics:
        dL = color_metrics.get('dL', 0)
        da = color_metrics.get('da', 0)
        db = color_metrics.get('db', 0)
        
        lab_section = []
        lab_section.append(Paragraph("Detailed Lab* Color Space Analysis", styles['H2']))
        
        lab_detail = [
            ["Component", "Difference", "Interpretation"],
            ["ΔL* (Lightness)", fmt2(dL), 
             "No significant change" if abs(dL) < 1.0 else ("Lighter" if dL > 0 else "Darker")],
            ["Δa* (Green-Red)", fmt2(da),
             "No significant shift" if abs(da) < 1.0 else ("More Red" if da > 0 else "More Green")],
            ["Δb* (Blue-Yellow)", fmt2(db),
             "No significant shift" if abs(db) < 1.0 else ("More Yellow" if db > 0 else "More Blue")],
        ]
        lab_section.append(make_table(lab_detail, colWidths=[1.6*inch, 1.2*inch, 2.5*inch]))
        lab_section.append(Spacer(1, 10))
        elements.append(KeepTogether(lab_section))
    
    # F. Lab Visualizations
    if settings.enable_color_lab_viz:
        viz_section = []
        viz_section.append(Paragraph("Lab* Visualizations", styles['H2']))
        
        viz_row = []
        if 'ab_scatter' in charts:
            try:
                viz_row.append(RLImage(charts['ab_scatter'], width=2.5*inch, height=2.5*inch))
            except:
                pass
        if 'lab_bars' in charts:
            try:
                viz_row.append(RLImage(charts['lab_bars'], width=3*inch, height=2*inch))
            except:
                pass
        
        if viz_row:
            viz_section.append(Table([viz_row], colWidths=[2.7*inch, 3.3*inch]))
        viz_section.append(Spacer(1, 10))
        elements.append(KeepTogether(viz_section))
    
    # G. Spectral Proxy
    if settings.enable_color_spectral_proxy and 'spectral_proxy' in charts:
        spectral_section = []
        spectral_section.append(Paragraph("Spectral Analysis (Proxy)", styles['H2']))
        spectral_section.append(Paragraph("The chart approximates spectral behavior from RGB averages.", styles['Small']))
        try:
            spectral_section.append(RLImage(charts['spectral_proxy'], width=5*inch, height=2.5*inch))
        except:
            pass
        spectral_section.append(Spacer(1, 10))
        elements.append(KeepTogether(spectral_section))
    
    # RGB Histograms
    if 'hist_ref' in charts and 'hist_test' in charts:
        hist_section = []
        hist_section.append(Paragraph("RGB Histograms", styles['H2']))
        try:
            hist_row = [[
                RLImage(charts['hist_ref'], width=2.8*inch, height=1.4*inch),
                RLImage(charts['hist_test'], width=2.8*inch, height=1.4*inch)
            ]]
            hist_section.append(Table(hist_row, colWidths=[3*inch, 3*inch]))
        except:
            pass
        hist_section.append(Spacer(1, 10))
        elements.append(KeepTogether(hist_section))
    
    elements.append(PageBreak())


def build_pattern_unit(elements, results, settings, styles):
    """Build the Pattern Analysis Unit section"""
    elements.append(Paragraph("<b>Pattern Unit</b>", styles['H1']))
    elements.append(Spacer(1, 6))
    
    pattern_metrics = results.get('pattern_metrics', {})
    charts = results.get('charts', {})
    
    # Pattern Metrics Summary
    if settings.enable_pattern_ssim:
        metrics_section = []
        metrics_section.append(Paragraph("Pattern Metrics", styles['H2']))
        
        ssim_val = pattern_metrics.get('ssim', 0)
        ssim_status = "PASS" if ssim_val >= settings.ssim_pass_threshold else (
            "CONDITIONAL" if ssim_val >= settings.ssim_conditional_threshold else "FAIL")
        
        patt_data = [
            ["Metric", "Value", "Status"],
            ["SSIM", fmt_pct(ssim_val * 100), ssim_status],
            ["Symmetry", fmt_pct(pattern_metrics.get('symmetry', 0)), ""],
            ["Edge Definition", fmt1(pattern_metrics.get('edge_definition', 0)) + "/100", ""],
            ["Repeat Period", f"H: {pattern_metrics.get('repeat_period_x', 0)}px, V: {pattern_metrics.get('repeat_period_y', 0)}px", ""],
        ]
        
        patt_table = make_table(patt_data, colWidths=[2*inch, 2*inch, 1.5*inch])
        # Color SSIM status
        if ssim_status == "PASS":
            patt_table.setStyle(TableStyle([("BACKGROUND", (2, 1), (2, 1), GREEN), ("TEXTCOLOR", (2, 1), (2, 1), colors.white)]))
        elif ssim_status == "CONDITIONAL":
            patt_table.setStyle(TableStyle([("BACKGROUND", (2, 1), (2, 1), ORANGE), ("TEXTCOLOR", (2, 1), (2, 1), colors.white)]))
        else:
            patt_table.setStyle(TableStyle([("BACKGROUND", (2, 1), (2, 1), RED), ("TEXTCOLOR", (2, 1), (2, 1), colors.white)]))
        
        metrics_section.append(patt_table)
        metrics_section.append(Spacer(1, 10))
        elements.append(KeepTogether(metrics_section))
    
    # Advanced Texture Analysis
    if settings.enable_pattern_advanced:
        elements.append(PageBreak())
        elements.append(Paragraph("<b>Advanced Texture Analysis</b>", styles['H1']))
        elements.append(Spacer(1, 6))
        
        # FFT Analysis
        if 'fft_spectrum' in charts:
            fft_section = []
            fft_section.append(Paragraph("Fourier Domain Analysis", styles['H2']))
            fft_section.append(Paragraph("2D FFT reveals periodic structures and directional patterns.", styles['Small']))
            try:
                fft_section.append(RLImage(charts['fft_spectrum'], width=4.5*inch, height=3*inch))
            except:
                pass
            fft_section.append(Spacer(1, 10))
            elements.append(KeepTogether(fft_section))
        
        # Gabor Analysis
        if 'gabor_montage' in charts:
            gabor_section = []
            gabor_section.append(Paragraph("Gabor Filter Bank Analysis", styles['H2']))
            gabor_section.append(Paragraph("Multi-scale orientation responses capture texture features.", styles['Small']))
            try:
                gabor_section.append(RLImage(charts['gabor_montage'], width=6*inch, height=2.5*inch))
            except:
                pass
            gabor_section.append(Spacer(1, 10))
            elements.append(KeepTogether(gabor_section))
        
        # GLCM Radar
        if 'glcm_radar' in charts:
            glcm_section = []
            glcm_section.append(Paragraph("GLCM Texture Features", styles['H2']))
            glcm_section.append(Paragraph("Gray Level Co-occurrence Matrix quantifies spatial relationships.", styles['Small']))
            try:
                glcm_section.append(RLImage(charts['glcm_radar'], width=4*inch, height=4*inch))
            except:
                pass
            glcm_section.append(Spacer(1, 10))
            elements.append(KeepTogether(glcm_section))
        
        # LBP
        if 'lbp_map' in charts:
            lbp_section = []
            lbp_section.append(Paragraph("Local Binary Patterns (LBP)", styles['H2']))
            try:
                lbp_section.append(RLImage(charts['lbp_map'], width=6*inch, height=2.5*inch))
            except:
                pass
            lbp_section.append(Spacer(1, 10))
            elements.append(KeepTogether(lbp_section))
        
        # Wavelet
        if 'wavelet_energy' in charts:
            wavelet_section = []
            wavelet_section.append(Paragraph("Wavelet Decomposition", styles['H2']))
            try:
                wavelet_section.append(RLImage(charts['wavelet_energy'], width=5.5*inch, height=3.5*inch))
            except:
                pass
            wavelet_section.append(Spacer(1, 10))
            elements.append(KeepTogether(wavelet_section))
        
        # Defect Detection
        if 'defect_saliency' in charts:
            defect_section = []
            defect_section.append(Paragraph("Defect Detection & Saliency", styles['H2']))
            try:
                defect_section.append(RLImage(charts['defect_saliency'], width=5.5*inch, height=2.5*inch))
            except:
                pass
            defect_section.append(Spacer(1, 10))
            elements.append(KeepTogether(defect_section))
    
    elements.append(PageBreak())


def build_repetition_unit(elements, results, settings, styles):
    """Build the Pattern Repetition Analysis Unit"""
    elements.append(Paragraph("<b>Pattern Repetition Unit</b>", styles['H1']))
    elements.append(Paragraph("Analysis of pattern count, distribution, and integrity.", styles['Small']))
    elements.append(Spacer(1, 8))
    
    rep = results.get('pattern_repetition', {})
    charts = results.get('charts', {})
    
    # Summary Table
    if settings.enable_pattern_rep_summary:
        summary_section = []
        summary_section.append(Paragraph("Pattern Detection Summary", styles['H2']))
        
        summary_data = [
            ["Metric", "Reference", "Sample", "Δ", "Status"],
            ["Pattern Count", str(rep.get('count_ref', 0)), str(rep.get('count_test', 0)),
             f"{rep.get('count_diff', 0):+d}", rep.get('status', 'N/A')],
            ["Mean Area (px²)", fmt2(rep.get('mean_area_ref', 0)), fmt2(rep.get('mean_area_test', 0)), "", ""],
        ]
        
        # Add integrity if available
        integrity = rep.get('integrity', {})
        if integrity:
            summary_data.append(["Pattern Integrity (%)", "100.0", 
                               fmt2(integrity.get('overall_integrity', 0)), "", ""])
        
        summary_table = make_table(summary_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 0.8*inch, 1*inch])
        summary_section.append(summary_table)
        summary_section.append(Spacer(1, 10))
        elements.append(KeepTogether(summary_section))
    
    # Pattern Detection Maps
    if settings.enable_pattern_rep_count:
        if 'pattern_detection_ref' in charts and 'pattern_detection_test' in charts:
            det_section = []
            det_section.append(Paragraph("Pattern Detection", styles['H2']))
            try:
                det_row = [[
                    RLImage(charts['pattern_detection_ref'], width=2.8*inch, height=2*inch),
                    RLImage(charts['pattern_detection_test'], width=2.8*inch, height=2*inch)
                ]]
                det_section.append(Table(det_row, colWidths=[3*inch, 3*inch]))
            except:
                pass
            det_section.append(Spacer(1, 10))
            elements.append(KeepTogether(det_section))
        
        # Count comparison
        if 'pattern_count' in charts:
            count_section = []
            count_section.append(Paragraph("Pattern Count Comparison", styles['H2']))
            try:
                count_section.append(RLImage(charts['pattern_count'], width=4*inch, height=3*inch))
            except:
                pass
            count_section.append(Spacer(1, 10))
            elements.append(KeepTogether(count_section))
    
    # Spatial Distribution
    if settings.enable_pattern_rep_spatial:
        if 'density_ref' in charts and 'density_test' in charts:
            spatial_section = []
            spatial_section.append(Paragraph("Spatial Distribution", styles['H2']))
            try:
                density_row = [[
                    RLImage(charts['density_ref'], width=2.5*inch, height=2*inch),
                    RLImage(charts['density_test'], width=2.5*inch, height=2*inch)
                ]]
                spatial_section.append(Table(density_row, colWidths=[2.7*inch, 2.7*inch]))
            except:
                pass
            spatial_section.append(Spacer(1, 10))
            elements.append(KeepTogether(spatial_section))
    
    # Integrity Radar
    if settings.enable_pattern_rep_integrity and 'integrity_radar' in charts:
        integrity_section = []
        integrity_section.append(Paragraph("Pattern Integrity Assessment", styles['H2']))
        try:
            integrity_section.append(RLImage(charts['integrity_radar'], width=4*inch, height=4*inch))
        except:
            pass
        integrity_section.append(Spacer(1, 10))
        elements.append(KeepTogether(integrity_section))
    
    elements.append(PageBreak())


def build_spectrophotometer_unit(elements, results, settings, styles):
    """Build the Spectrophotometer Analysis Unit"""
    elements.append(Paragraph("<b>Spectrophotometer Unit</b>", styles['H1']))
    elements.append(Spacer(1, 6))
    
    spectro = results.get('spectrophotometer', {})
    charts = results.get('charts', {})
    
    # Configuration
    if settings.enable_spectro_config:
        config_section = []
        config_section.append(Paragraph("Configuration", styles['H2']))
        
        config_data = [
            ["Parameter", "Value"],
            ["Observer Angle", f"{settings.observer_angle}°"],
            ["Geometry Mode", settings.geometry_mode],
            ["CMC Ratio", settings.cmc_l_c_ratio if settings.use_delta_e_cmc else "Disabled"],
        ]
        config_section.append(make_table(config_data, colWidths=[2*inch, 3*inch]))
        config_section.append(Spacer(1, 10))
        elements.append(KeepTogether(config_section))
    
    # Whiteness/Yellowness
    if settings.enable_spectro_whiteness:
        white_section = []
        white_section.append(Paragraph("Whiteness & Yellowness Indices", styles['H2']))
        
        white_data = [
            ["Index", "Reference", "Sample", "Δ"],
            ["CIE Whiteness", fmt2(spectro.get('whiteness_ref', 0)),
             fmt2(spectro.get('whiteness_test', 0)),
             fmt2(spectro.get('whiteness_test', 0) - spectro.get('whiteness_ref', 0))],
            ["ASTM Yellowness", fmt2(spectro.get('yellowness_ref', 0)),
             fmt2(spectro.get('yellowness_test', 0)),
             fmt2(spectro.get('yellowness_test', 0) - spectro.get('yellowness_ref', 0))],
        ]
        white_section.append(make_table(white_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1*inch]))
        white_section.append(Spacer(1, 10))
        elements.append(KeepTogether(white_section))
    
    # Metamerism Analysis
    if settings.enable_spectro_metamerism and spectro.get('metamerism'):
        meta_section = []
        meta_section.append(Paragraph("Metamerism Analysis", styles['H2']))
        meta_section.append(Paragraph("Color difference under various illuminants.", styles['Small']))
        
        meta_data = [["Illuminant", "ΔE2000", "Status"]]
        for m in spectro['metamerism']:
            de = m['delta_e']
            status = "PASS" if de < 2.0 else ("CONDITIONAL" if de <= 3.5 else "FAIL")
            meta_data.append([m['illuminant'], fmt2(de), status])
        
        meta_table = Table(meta_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        meta_style = [
            ("BACKGROUND", (0, 0), (-1, 0), NEUTRAL_L),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, NEUTRAL_L),
        ]
        for i in range(1, len(meta_data)):
            status = meta_data[i][2]
            if status == "PASS":
                meta_style.append(("BACKGROUND", (2, i), (2, i), GREEN))
                meta_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
            elif status == "CONDITIONAL":
                meta_style.append(("BACKGROUND", (2, i), (2, i), ORANGE))
                meta_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
            else:
                meta_style.append(("BACKGROUND", (2, i), (2, i), RED))
                meta_style.append(("TEXTCOLOR", (2, i), (2, i), colors.white))
        meta_table.setStyle(TableStyle(meta_style))
        meta_section.append(meta_table)
        
        # Add metamerism index
        meta_index = spectro.get('metamerism_index', 0)
        meta_section.append(Paragraph(f"<b>Metamerism Index:</b> {fmt2(meta_index)}", styles['Body']))
        meta_section.append(Spacer(1, 10))
        elements.append(KeepTogether(meta_section))
        
        # Metamerism Chart
        if 'metamerism' in charts:
            try:
                elements.append(RLImage(charts['metamerism'], width=5*inch, height=3*inch))
                elements.append(Spacer(1, 10))
            except:
                pass


# Backwards compatibility - alias old function name
build_main_report = build_comprehensive_report
