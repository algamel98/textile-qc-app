# -*- coding: utf-8 -*-
"""
ReportLab styles for PDF generation
"""
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from app.core.constants import BLUE1, BLUE2, NEUTRAL_DARK, NEUTRAL


def get_styles():
    """Get base stylesheet"""
    return getSampleStyleSheet()


def get_paragraph_styles():
    """Get custom paragraph styles"""
    styles = {}
    
    styles['Title'] = ParagraphStyle(
        'Title',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=NEUTRAL_DARK,
        spaceAfter=12
    )
    
    styles['Subtitle'] = ParagraphStyle(
        'Subtitle',
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        textColor=NEUTRAL,
        spaceAfter=6
    )
    
    styles['H1'] = ParagraphStyle(
        'H1',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=BLUE1,
        spaceBefore=12,
        spaceAfter=6
    )
    
    styles['H2'] = ParagraphStyle(
        'H2',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=BLUE2,
        spaceBefore=8,
        spaceAfter=4
    )
    
    styles['H3'] = ParagraphStyle(
        'H3',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=NEUTRAL_DARK,
        spaceBefore=6,
        spaceAfter=3
    )
    
    styles['Body'] = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.black,
        spaceAfter=4
    )
    
    styles['Small'] = ParagraphStyle(
        'Small',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=NEUTRAL,
        spaceAfter=2
    )
    
    styles['Footer'] = ParagraphStyle(
        'Footer',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=NEUTRAL
    )
    
    styles['TableHeader'] = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    
    styles['TableCell'] = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER
    )
    
    return styles

