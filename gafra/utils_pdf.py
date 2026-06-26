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
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.styles import ParagraphStyle
        except Exception:
            # No está disponible ReportLab: re-lanzamos el error original para que el desarrollador lo vea
            raise weasy_exc

        # Rows/cols provided by views
        rows = context.get('rows', []) or []
        cols = context.get('columns')

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

        col_count = len(table_data[0]) if table_data else len(cols or [])
        use_landscape = col_count >= 9
        page_size = landscape(A4) if use_landscape else A4
        left_margin = right_margin = 18 if use_landscape else 24
        top_margin = bottom_margin = 20 if use_landscape else 24

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=page_size,
            rightMargin=right_margin,
            leftMargin=left_margin,
            topMargin=top_margin,
            bottomMargin=bottom_margin,
        )

        page_width = page_size[0]
        avail_width = page_width - left_margin - right_margin

        styles = getSampleStyleSheet()
        small_normal = ParagraphStyle(
            'GafraSmallNormal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8 if col_count >= 9 else 9,
            leading=10 if col_count >= 9 else 11,
            wordWrap='CJK',
        )
        header_style = ParagraphStyle(
            'GafraHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8 if col_count >= 9 else 9,
            leading=10,
            textColor=colors.white,
            wordWrap='CJK',
        )

        def _clip(value, max_chars=160):
            text = '' if value is None else str(value)
            if len(text) <= max_chars:
                return text
            return text[:max_chars - 1] + '…'

        def _col_widths(headers, total_width):
            if not headers:
                return [total_width]

            weights = []
            for h in headers:
                key = str(h).strip().lower()
                w = 1.0
                if 'descrip' in key or 'direc' in key or 'observ' in key:
                    w = 2.4
                elif 'nombre' in key or 'contact' in key:
                    w = 1.7
                elif 'email' in key or 'web' in key:
                    w = 1.5
                elif 'fecha' in key:
                    w = 1.35
                elif 'precio' in key or 'total' in key:
                    w = 1.2
                elif key in {'id', 'cp'} or 'activo' in key or 'estado' in key:
                    w = 0.8
                weights.append(w)

            base = sum(weights) or 1.0
            widths = [total_width * (w / base) for w in weights]
            min_w = 42 if col_count >= 9 else 48
            widths = [max(min_w, w) for w in widths]

            extra = sum(widths) - total_width
            if extra > 0:
                shrinkable = [i for i, w in enumerate(widths) if w > min_w]
                while extra > 0.1 and shrinkable:
                    step = extra / len(shrinkable)
                    for i in list(shrinkable):
                        room = widths[i] - min_w
                        dec = min(room, step)
                        widths[i] -= dec
                        extra -= dec
                        if widths[i] <= min_w + 0.01:
                            shrinkable.remove(i)
            return widths

        story = []

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
        hdr_table = Table([header_elems], colWidths=[avail_width * 0.45, avail_width * 0.55])
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
            meta_tbl = Table(meta_rows, colWidths=[avail_width * 0.5, avail_width * 0.5])
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

        if table_data:
            raw_headers = table_data[0]
            col_widths = _col_widths(raw_headers, avail_width)

            formatted_data = [[Paragraph(_clip(h, 80), header_style) for h in raw_headers]]
            for row in table_data[1:]:
                formatted_row = []
                for value in row:
                    formatted_row.append(Paragraph(_clip(value), small_normal))
                formatted_data.append(formatted_row)

            tbl = Table(formatted_data, colWidths=col_widths, repeatRows=1)
            tbl_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8 if col_count >= 9 else 9),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E5E7EB')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8 if col_count >= 9 else 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ])

            # alternating backgrounds and conditional highlights
            for r_idx in range(1, len(formatted_data)):
                if r_idx % 2 == 0:
                    tbl_style.add('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor('#FBFCFE'))
                # check each cell for numeric negative to highlight
                for c_idx in range(len(raw_headers)):
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
            canvas.drawCentredString(page_size[0] / 2.0, 12, footer_text)
            canvas.restoreState()

        doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
