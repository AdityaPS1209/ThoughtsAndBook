import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def _footer(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Times-Roman", 10)
    canvas.drawCentredString(doc.width/2 + doc.leftMargin, 1.2 * cm, f"{page_num}")


def build_cards_book(cards, title: str = "Cards Book") -> bytes:
    """Build a book-like PDF with one card per page.
    `cards` is a list of dicts with keys: id, content, created_at.
    Returns PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
        title=title,
        author="Cards App",
    )

    styles = getSampleStyleSheet()
    story = []

    # --- Cover Page ---
    cover_title = f"{title}"
    subtitle = datetime.now().strftime("Generated on %B %d, %Y")
    story.append(Spacer(1, 6*cm))
    story.append(Paragraph(f"<para align='center'><font size=24><b>{cover_title}</b></font></para>", styles["Title"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<para align='center'><font size=12>{subtitle}</font></para>", styles["Normal"]))
    story.append(PageBreak())

    # --- Cards ---
    for idx, card in enumerate(cards, start=1):
        created = card["created_at"].strftime("%Y-%m-%d %H:%M") if card.get("created_at") else ""
        header_html = f"<b>Page {idx} – Card #{card['id']}</b><br/><i>{created}</i>"
        story.append(Paragraph(header_html, styles["Heading3"]))
        story.append(Spacer(1, 0.4*cm))

        # Preserve line breaks
        content_html = card["content"].replace("\n", "<br/>")
        story.append(Paragraph(content_html, styles["BodyText"]))

        story.append(PageBreak())

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes