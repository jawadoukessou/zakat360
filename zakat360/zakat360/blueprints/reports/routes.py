import csv
from io import StringIO, BytesIO
from datetime import datetime
from flask import render_template, request, Response
from sqlalchemy import func

from . import reports_bp
from ...extensions import db
from ...models import Donation, Cause


@reports_bp.route('/annual')
def annual():
    year = request.args.get('year', str(datetime.utcnow().year))
    export_format = request.args.get('format')

    # Agrégation par cause et par mois
    monthly = (
        db.session.query(
            func.strftime('%m', Donation.created_at).label('month'),
            func.coalesce(func.sum(Donation.amount), 0).label('total')
        )
        .filter(func.strftime('%Y', Donation.created_at) == str(year))
        .group_by('month')
        .order_by('month')
        .all()
    )

    by_cause = (
        db.session.query(
            Cause.name.label('cause'),
            func.coalesce(func.sum(Donation.amount), 0).label('total')
        )
        .join(Donation, Donation.cause_id == Cause.id)
        .filter(func.strftime('%Y', Donation.created_at) == str(year))
        .group_by(Cause.name)
        .order_by(func.sum(Donation.amount).desc())
        .all()
    )

    if export_format == 'csv':
        # Export CSV standard
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Mois', 'Total'])
        for m in monthly:
            writer.writerow([m.month, m.total])
        writer.writerow([])
        writer.writerow(['Cause', 'Total'])
        for c in by_cause:
            writer.writerow([c.cause, c.total])
        csv_data = output.getvalue()
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename="annual_{year}.csv"'}
        )

    if export_format == 'pdf':
        # PDF via ReportLab
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Rapport Annuel {year} - Zakat360")
        y -= 30
        c.setFont("Helvetica", 12)
        c.drawString(50, y, "Dons par Mois:")
        y -= 20
        for m in monthly:
            c.drawString(60, y, f"Mois {m.month}: {float(m.total):.2f} €")
            y -= 18
        y -= 10
        c.drawString(50, y, "Par Cause:")
        y -= 20
        for cse in by_cause:
            c.drawString(60, y, f"{cse.cause}: {float(cse.total):.2f} €")
            y -= 18
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 12)
        c.showPage()
        c.save()
        pdf_data = buffer.getvalue()
        buffer.close()
        return Response(pdf_data, mimetype='application/pdf', headers={'Content-Disposition': f'attachment; filename="annual_{year}.pdf"'})

    return render_template('reports/annual.html', year=year, monthly=monthly, by_cause=by_cause)