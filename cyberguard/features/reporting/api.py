from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy.orm import Session
from cyberguard.core.database import get_db
from cyberguard.core.auth import get_current_user
from cyberguard.features.assets.models import Asset

router = APIRouter()

@router.get("/report")
async def download_report(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assets = db.query(Asset).filter(Asset.owner_username == current_user.username).order_by(Asset.id.desc()).all()
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(font_path): font_path = "./DejaVuSans.ttf"
    if os.path.exists(font_path): pdfmetrics.registerFont(TTFont('DejaVu', font_path)); turkce_font = 'DejaVu'
    else: turkce_font = 'Helvetica'
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], textColor=colors.HexColor('#00ff88'), fontName=turkce_font)
    story.append(Paragraph("AEGISMATRIX - Varlık Güvenlik Raporu", title_style))
    data = [["ID", "URL", "Durum", "Risk"]]
    for a in assets: data.append([str(a.id), a.url, a.status, a.risk_score])
    table = Table(data, colWidths=[1*cm, 6*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), turkce_font)]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=aegismatrix_raporu.pdf"})
