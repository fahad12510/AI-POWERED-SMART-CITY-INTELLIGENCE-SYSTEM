from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf_report(data, metrics, ai_result):
    out = Path(__file__).parent / "generated_reports"
    out.mkdir(exist_ok=True)
    path = out / "smart_city_weekly_report.pdf"
    styles = getSampleStyleSheet()
    story = [Paragraph("AI-Powered Smart City Intelligence Report", styles["Title"]),
             Paragraph("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M"), styles["Normal"]),
             Spacer(1, 12),
             Paragraph("Executive Summary", styles["Heading2"]),
             Paragraph(ai_result.get("content","").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\\n","<br/>"), styles["BodyText"]),
             Spacer(1, 10),
             Paragraph("Traffic Analysis", styles["Heading2"]),
             Paragraph(str(metrics["traffic_stats"]), styles["BodyText"]),
             Paragraph("Air Quality Analysis", styles["Heading2"]),
             Paragraph(str(metrics["aqi_stats"]), styles["BodyText"]),
             Paragraph("Detected Anomalies", styles["Heading2"])]
    rows = [["Metric","Location","Day","Value","Reason"]]
    for item in metrics["anomalies"][:35]:
        rows.append([item["metric"], item["location"], str(item["day"]), str(item["value"]), item["reason"]])
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#174c38")),
                               ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                               ("GRID",(0,0),(-1,-1),0.4,colors.grey),
                               ("FONTSIZE",(0,0),(-1,-1),7),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story += [table, Spacer(1,10), Paragraph("Trend Estimates",styles["Heading2"]),
              Paragraph("Next-day values are experimental linear estimates based on only seven days of data and are not reliable operational forecasts.",styles["BodyText"]),
              Paragraph("Limitations and Data Quality",styles["Heading2"]),
              Paragraph("The built-in dataset is fictional educational data. Statistical flags are indicators for review, not proof of an emergency. Missing uploaded readings are rejected rather than silently replaced with zero.",styles["BodyText"])]
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=35,leftMargin=35,topMargin=35,bottomMargin=35).build(story)
    return str(path)
