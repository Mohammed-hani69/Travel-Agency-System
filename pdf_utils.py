# This script is used by app.py to add watermark and logo to PDF exports
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

def draw_pdf_header(c, width, height, logo_path, company_name, section, month_year):
    # خلفية رأس باللون البنفسجي الفاتح
    c.saveState()
    c.setFillColor(HexColor('#f3e9fd'))
    c.roundRect(20, height-90, width-40, 70, 18, fill=1, stroke=0)
    c.restoreState()
    # رسم اللوجو واسم الشركة
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height-70, width=48, height=48, mask='auto')
    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(HexColor('#8a3ee9'))
    c.drawString(100, height-50, company_name)
    c.setFont('Helvetica', 13)
    c.setFillColor(HexColor('#444444'))
    c.drawString(100, height-70, f'{section} - {month_year}')
    c.setFillColor(HexColor('#000000'))


def draw_watermark(c, width, height, logo_path):
    # لوجو شفاف في منتصف الصفحة كخلفية
    if os.path.exists(logo_path):
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(30)
        c.setFillAlpha(0.10)
        c.drawImage(logo_path, -220, -220, width=440, height=440, mask='auto')
        c.setFillAlpha(1)
        c.restoreState()


def create_custom_pdf(filename, data_rows, columns, logo_path, company_name, section, month_year):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import mm
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4), leftMargin=10, rightMargin=10, topMargin=80, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    purple = HexColor('#8a3ee9')
    # عنوان الجدول
    if section == 'hotels':
        table_title = 'تقرير حجوزات الفنادق'
    elif section == 'tickets':
        table_title = 'تقرير التذاكر'
    elif section == 'expenses':
        table_title = 'تقرير المصروفات'
    elif section == 'salaries':
        table_title = 'تقرير الرواتب'
    else:
        table_title = company_name
    title_style = ParagraphStyle('title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=purple, alignment=TA_CENTER, spaceAfter=12)
    elements.append(Paragraph(table_title, title_style))
    elements.append(Paragraph(f"{section} - {month_year}", styles['Normal']))
    elements.append(Spacer(1, 12))
    # جدول البيانات
    table_data = [columns] + data_rows
    table = Table(table_data, repeatRows=1, style=[('ROUNDRECT', (0,0), (-1,-1), 12, 12)], colWidths=[None]*len(columns))
    # تصغير حجم الخط وتضييق الأعمدة إذا كان عدد الأعمدة كبيراً
    if len(columns) > 8:
        table._argW = [65 for _ in columns]  # كل عمود 65 نقطة تقريباً
        header_font_size = 9  # تصغير الخط
        cell_font_size = 8
    else:
        header_font_size = 11  # تصغير الخط
        cell_font_size = 12
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), purple),
        ('TEXTCOLOR', (0,0), (-1,0), '#000'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), header_font_size),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,1), (-1,-1), Color(243/255, 233/255, 253/255, alpha=0.95)),
        ('GRID', (0,0), (-1,-1), 0.5, purple),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [Color(255/255,255/255,255/255,0.7), Color(243/255,233/255,253/255,0.95)]),
        ('FONTSIZE', (0,1), (-1,-1), cell_font_size),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1.5, purple),
        ('ROUNDED', (0,0), (-1,-1), 12),
    ]))
    elements.append(table)
    def on_first_page(canvas, doc):
        width, height = landscape(A4)
        draw_watermark(canvas, width, height, logo_path)
        draw_pdf_header(canvas, width, height, logo_path, company_name, section, month_year)
    def on_later_pages(canvas, doc):
        width, height = landscape(A4)
        draw_watermark(canvas, width, height, logo_path)
    doc.build(elements, onFirstPage=on_first_page, onLaterPages=on_later_pages)
