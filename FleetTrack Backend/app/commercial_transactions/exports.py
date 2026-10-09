from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from xml.etree.ElementTree import Element, SubElement, tostring, register_namespace
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle

FIELDS = [('invoiceNo', 'Invoice'), ('date', 'Date'), ('voucherTypeName', 'Type'),
          ('customer', 'Customer'), ('grandTotal', 'Amount'), ('taxAmount', 'Tax'), ('narration', 'Narration')]


def value_text(value):
    if isinstance(value, (datetime, date)):
        return value.strftime('%d/%m/%Y')
    if isinstance(value, Decimal):
        return f'{value:.2f}'
    return str(value or '')


def excel(rows):
    # Excel's XML workbook format avoids a new runtime dependency and preserves cell types.
    ns = 'urn:schemas-microsoft-com:office:spreadsheet'
    register_namespace('ss', ns)
    tag = lambda name: '{' + ns + '}' + name
    workbook = Element(tag('Workbook'))
    sheet = SubElement(workbook, tag('Worksheet'), {tag('Name'): 'Sales Invoices'})
    table = SubElement(sheet, tag('Table'))
    for values in [[label for _, label in FIELDS]] + [[row.get(key) for key, _ in FIELDS] for row in rows]:
        row = SubElement(table, tag('Row'))
        for value in values:
            cell = SubElement(row, tag('Cell'))
            numeric = isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)
            data = SubElement(cell, tag('Data'), {tag('Type'): 'Number' if numeric else 'String'})
            data.text = str(value) if numeric else value_text(value)
    return tostring(workbook, encoding='utf-8', xml_declaration=True)


def pdf(rows):
    result = BytesIO()
    document = SimpleDocTemplate(result, pagesize=landscape(A4), leftMargin=28, rightMargin=28, topMargin=28, bottomMargin=28)
    body = ParagraphStyle('Cell', fontName='Helvetica', fontSize=8, leading=11, wordWrap='CJK')
    heading = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=16, leading=20)
    content = [Paragraph('Sales Invoice Register', heading), Spacer(1, 12)]
    cells = [[Paragraph(label, body) for _, label in FIELDS]]
    cells.extend([[Paragraph(escape(value_text(row.get(key))), body) for key, _ in FIELDS] for row in rows])
    table = LongTable(cells, colWidths=[78, 62, 95, 150, 70, 65, 209], repeatRows=1, splitInRow=1)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EEF5')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, 0), .6, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7), ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('LINEBELOW', (0, 1), (-1, -1), .2, colors.HexColor('#DDE3EA'))]))
    content.append(table)
    def footer(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(810, 14, f'Page {doc.page}')
    document.build(content, onFirstPage=footer, onLaterPages=footer)
    return result.getvalue()
