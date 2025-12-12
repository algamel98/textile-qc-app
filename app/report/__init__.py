# -*- coding: utf-8 -*-
"""
Report generation module
"""
from app.report.pdf_builder import build_main_report
from app.report.styles import get_styles, get_paragraph_styles
from app.report.components import make_table, badge, colored_status_cell

__all__ = ['build_main_report', 'get_styles', 'get_paragraph_styles', 
           'make_table', 'badge', 'colored_status_cell']

