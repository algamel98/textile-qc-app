# -*- coding: utf-8 -*-
"""
ReportLab components for PDF reports
"""
from reportlab.platypus import Table, TableStyle, Flowable, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch
from app.core.constants import (
    BLUE1, BLUE2, GREEN, RED, ORANGE, NEUTRAL, NEUTRAL_L, NEUTRAL_DARK
)


class Badge(Flowable):
    """Colored badge/label flowable"""
    
    def __init__(self, text, bg_color):
        Flowable.__init__(self)
        self.text = text
        self.bg = bg_color
        self.w = len(text) * 6 + 12
        self.h = 14
    
    def draw(self):
        self.canv.setFillColor(self.bg)
        self.canv.roundRect(0, 0, self.w, self.h, 3, fill=1, stroke=0)
        self.canv.setFillColor(colors.white)
        self.canv.setFont('Helvetica-Bold', 8)
        self.canv.drawCentredString(self.w / 2, 4, self.text)
    
    def wrap(self, availW, availH):
        return (self.w, self.h)


def badge(text, back_color=NEUTRAL):
    """Create a badge flowable"""
    return Badge(text, back_color)


def colored_status_cell(text, status):
    """Get background color for status"""
    color_map = {
        'PASS': GREEN,
        'FAIL': RED,
        'CONDITIONAL': ORANGE,
        'ACCEPT': GREEN,
        'REJECT': RED
    }
    return color_map.get(status, NEUTRAL)


def make_table(data, colWidths=None, alt=True, header_bg=NEUTRAL_L):
    """
    Create a styled table.
    
    Args:
        data: List of rows (first row is header)
        colWidths: Column widths
        alt: Whether to use alternating row colors
        header_bg: Header background color
        
    Returns:
        Table: Styled table
    """
    if colWidths is None:
        colWidths = [1.5 * inch] * len(data[0]) if data else [1.5 * inch]
    
    table = Table(data, colWidths=colWidths)
    
    style = [
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, NEUTRAL_L),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    
    # Alternating row colors
    if alt and len(data) > 1:
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.Color(0.97, 0.97, 0.97)))
    
    table.setStyle(TableStyle(style))
    return table


def wrap_text_cell(text, max_chars=60):
    """Wrap long text for table cells"""
    if len(text) <= max_chars:
        return text
    
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def fmt_pct(x):
    """Format as percentage"""
    return f"{x:.1f}%"


def fmt2(x):
    """Format with 2 decimal places"""
    return f"{x:.2f}"


def fmt1(x):
    """Format with 1 decimal place"""
    return f"{x:.1f}"

