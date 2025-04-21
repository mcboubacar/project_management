from flask import render_template
from weasyprint import HTML
import os

def generate_pdf_report(template, **kwargs):
    # Render HTML template with data
    html_string = render_template(template, **kwargs)
    
    # Generate PDF from HTML
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    return pdf