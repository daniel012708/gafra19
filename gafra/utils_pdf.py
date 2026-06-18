from django.template.loader import render_to_string
from django.http import HttpResponse
import io
import base64
import re
import datetime


def render_pdf_from_template(request, template_name, context, filename='report.pdf'):
    """Renderiza un template HTML a PDF usando WeasyPrint si está disponible.

    Si WeasyPrint falla por falta de librerías nativas, usa ReportLab como fallback
    para generar un PDF básico que contenga título, gráfico (si existe) y tabla.
    """
    # Intentar WeasyPrint primero (mejor CSS), si falla usar ReportLab como fallback rápido
    try:
        from weasyprint import HTML, CSS

        html_string = render_to_string(template_name, context)
        base_url = request.build_absolute_uri('/')
        html = HTML(string=html_string, base_url=base_url)

        pdf_bytes = html.write_pdf(stylesheets=[])
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as weasy_exc:
        # Fallback: generar PDF simple con ReportLab (no requiere las librerías nativas de WeasyPrint)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
        except Exception:
            # No está disponible ReportLab: re-lanzamos el error original para que el desarrollador lo vea
            raise weasy_exc

        buffer = io.BytesIO()
        left_margin = right_margin = top_margin = bottom_margin = 24
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=right_margin,
            leftMargin=left_margin,
            topMargin=top_margin,
            bottomMargin=bottom_margin,
        )
        styles = getSampleStyleSheet()
        story = []
        # Rows/cols provided by views
        rows = context.get('rows', []) or []
        cols = context.get('columns')

        # Header area: optional logo (left) + company info (right)
        logo_uri = context.get('logo')
        company_block = context.get('company') or ''

        header_elems = []
        if logo_uri:
            m = re.match(r'data:image/(?P<fmt>png|jpeg);base64,(?P<data>.+)', logo_uri)
            if m:
                img_bytes = base64.b64decode(m.group('data'))
                img_buffer = io.BytesIO(img_bytes)
                try:
                    logo = Image(img_buffer)
                    logo._restrictSize(120, 60)
                    header_elems.append(logo)
                except Exception:
                    header_elems.append(Paragraph('', styles['Normal']))
        else:
            header_elems.append(Paragraph('', styles['Normal']))

        # company info on the right
        header_elems.append(Paragraph(company_block, styles['Normal']))

        # place header elements in a table to align left/right
        hdr_table = Table([header_elems], colWidths=[280, 260])
        hdr_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        story.append(hdr_table)
        story.append(Spacer(1, 8))

        # Title centered
        title = context.get('title') or 'REPORTE'
        title_style = styles['Title']
        story.append(Paragraph(title.upper(), title_style))
        story.append(Spacer(1, 8))

        # Metadata block: two-column key/value table (example: Proyecto, Fecha, Cliente...)
        meta = context.get('meta') or {}
        meta_items = list(meta.items())
        # build rows of two pairs per row
        meta_rows = []
        i = 0
        while i < len(meta_items):
            left = f'<b>{meta_items[i][0]}:</b> {meta_items[i][1]}'
            right = ''
            if i + 1 < len(meta_items):
                right = f'<b>{meta_items[i+1][0]}:</b> {meta_items[i+1][1]}'
            meta_rows.append([Paragraph(left, styles['Normal']), Paragraph(right, styles['Normal'])])
            i += 2

        if meta_rows:
            meta_tbl = Table(meta_rows, colWidths=[260, 260])
            meta_tbl.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#EEF2FF')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(meta_tbl)
            story.append(Spacer(1, 12))

        # Section header and description
        section_title = context.get('section_title') or 'DESCRIPCIÓN'
        story.append(Paragraph(section_title.upper(), styles['Heading3']))
        story.append(Spacer(1, 6))
        description = context.get('description') or ''
        story.append(Paragraph(description, styles['Normal']))
        story.append(Spacer(1, 12))

        # Chart larger and centered if present
        chart_data_uri = context.get('chart_img')
        if chart_data_uri:
            m = re.match(r'data:image/(?P<fmt>png|jpeg);base64,(?P<data>.+)', chart_data_uri)
            if m:
                img_bytes = base64.b64decode(m.group('data'))
                img_buffer = io.BytesIO(img_bytes)
                try:
                    img = Image(img_buffer)
                    img._restrictSize(520, 260)
                    story.append(img)
                    story.append(Spacer(1, 12))
                except Exception:
                    pass

        # Prepare results table with highlighted cells for negative values
        table_data = []
        if rows:
            if isinstance(rows[0], dict):
                if not cols:
                    cols = list(rows[0].keys())
                table_data.append(cols)
                for r in rows:
                    table_data.append([r.get(c, '') for c in cols])
            else:
                if cols:
                    table_data.append(cols)
                for r in rows:
                    table_data.append([x for x in (r if isinstance(r, (list, tuple)) else [r])])

        if table_data:
            page_width = A4[0]
            avail_width = page_width - left_margin - right_margin
            col_count = len(table_data[0])
            col_width = avail_width / col_count
            col_widths = [col_width] * col_count

            tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
            tbl_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E5E7EB')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])

            # alternating backgrounds and conditional highlights
            for r_idx in range(1, len(table_data)):
                if r_idx % 2 == 0:
                    tbl_style.add('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor('#FBFCFE'))
                # check each cell for numeric negative to highlight
                for c_idx in range(len(table_data[0])):
                    try:
                        val = table_data[r_idx][c_idx]
                        n = float(val)
                        if n < 0:
                            tbl_style.add('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#FEF3C7'))
                    except Exception:
                        # not numeric
                        continue

            tbl.setStyle(tbl_style)
            story.append(tbl)
        else:
            story.append(Paragraph('No hay datos para mostrar.', styles['Normal']))

        # Footer with page numbers
        def _footer(canvas, doc):
            canvas.saveState()
            footer_text = f'Página {canvas.getPageNumber()}'
            canvas.setFont('Helvetica', 8)
            canvas.drawCentredString(A4[0] / 2.0, 12, footer_text)
            canvas.restoreState()

        doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
