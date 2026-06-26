import io

import pandas as pd
from django.http import HttpResponse


EXCEL_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def build_excel_template_response(filename, columns, sample_rows=None):
    """Build an in-memory .xlsx template with fixed columns and optional sample rows."""
    rows = sample_rows or [{col: '' for col in columns}]
    df = pd.DataFrame(rows)

    # Keep the exact expected column order for bulk upload views.
    for col in columns:
        if col not in df.columns:
            df[col] = ''
    df = df[columns]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='plantilla', index=False)

    response = HttpResponse(output.getvalue(), content_type=EXCEL_CONTENT_TYPE)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
