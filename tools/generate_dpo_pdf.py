import json
import os
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import HRFlowable


ROOT = Path(__file__).resolve().parents[1]
SOURCE_JSON = ROOT / "domande_privacy_sanita_REVISIONE_DPO.json"
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT_PDF = OUTPUT_DIR / "edigit_domande_privacy_revisione_dpo.pdf"
LOGO = ROOT / "src" / "assets" / "edigit-logo.svg"

PAGE_WIDTH, PAGE_HEIGHT = A4

EDIGIT_BLUE = colors.HexColor("#3b4d82")
EDIGIT_ORANGE = colors.HexColor("#f28f52")
TEXT = colors.HexColor("#172033")
MUTED = colors.HexColor("#5c6675")
LIGHT = colors.HexColor("#f4f6f9")
LINE = colors.HexColor("#dce2ea")

AREA_COLORS = {
    "giallo": colors.HexColor("#f2b705"),
    "fucsia": colors.HexColor("#d9368a"),
    "verde": colors.HexColor("#10a16b"),
    "rosso porpora": colors.HexColor("#8d1f3d"),
    "blu": colors.HexColor("#0f74bd"),
    "bianco e nero": colors.HexColor("#d9dee7"),
}


def clean(text):
    return str(text or "").strip()


def esc(text):
    value = clean(text)
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def strip_answer_prefix(text):
    value = clean(text)
    return re.sub(r"^(SI|SÌ|NO|OBBLIGATORIA|SCONSIGLIATO\s*/\s*NO)\.\s*", "", value, flags=re.I)


def make_styles():
    base = getSampleStyleSheet()
    return {
        "cover_brand": ParagraphStyle(
            "cover_brand",
            parent=base["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=42,
            leading=46,
            textColor=EDIGIT_BLUE,
            spaceAfter=10,
        ),
        "motto": ParagraphStyle(
            "motto",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=EDIGIT_ORANGE,
            spaceAfter=34,
        ),
        "cover_question": ParagraphStyle(
            "cover_question",
            parent=base["Heading1"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=27,
            leading=32,
            textColor=TEXT,
            spaceAfter=18,
        ),
        "cover_note": ParagraphStyle(
            "cover_note",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            leading=15,
            textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "section",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=TEXT,
            spaceAfter=8,
        ),
        "section_meta": ParagraphStyle(
            "section_meta",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=MUTED,
            spaceAfter=18,
        ),
        "question": ParagraphStyle(
            "question",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12.4,
            leading=15.5,
            textColor=TEXT,
            spaceAfter=7,
        ),
        "answer": ParagraphStyle(
            "answer",
            parent=base["Normal"],
            fontSize=10.3,
            leading=13.2,
            textColor=TEXT,
            spaceAfter=5,
        ),
        "sales": ParagraphStyle(
            "sales",
            parent=base["Italic"],
            fontSize=9.2,
            leading=12,
            textColor=MUTED,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#818b99"),
        ),
    }


def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(doc.leftMargin, 1.42 * cm, PAGE_WIDTH - doc.rightMargin, 1.42 * cm)
    canvas.setFillColor(colors.HexColor("#818b99"))
    canvas.setFont("Helvetica", 8)
    label = f"E-Digit - Revisione DPO - pagina {doc.page}"
    canvas.drawCentredString(PAGE_WIDTH / 2, 1.0 * cm, label)
    canvas.restoreState()


def cover_logo():
    from reportlab.graphics.shapes import Drawing, Path, Rect

    target = 4.6 * cm
    scale = target / 375.0
    drawing = Drawing(target, target)
    drawing.add(Rect(0, 0, target, target, fillColor=EDIGIT_BLUE, strokeColor=None))

    def rect(x, y, width, height, color):
        drawing.add(
            Rect(
                x * scale,
                (375 - y - height) * scale,
                width * scale,
                height * scale,
                fillColor=color,
                strokeColor=None,
            )
        )

    rect(99.074219, 135.335938, 82.730469, 23.238281, EDIGIT_ORANGE)
    rect(99.074219, 180.445312, 82.730469, 23.238282, EDIGIT_ORANGE)
    rect(99.074219, 225.554688, 82.730469, 23.238281, EDIGIT_ORANGE)

    path = Path()
    path.moveTo(242.65625 * scale, (375 - 135.335938) * scale)
    path.lineTo(205.050781 * scale, (375 - 135.335938) * scale)
    path.lineTo(205.050781 * scale, (375 - 158.574219) * scale)
    path.lineTo(242.65625 * scale, (375 - 158.574219) * scale)
    path.curveTo(
        261.117188 * scale,
        (375 - 158.574219) * scale,
        276.160156 * scale,
        (375 - 173.613281) * scale,
        276.160156 * scale,
        (375 - 192.066406) * scale,
    )
    path.curveTo(
        276.160156 * scale,
        (375 - 210.519531) * scale,
        261.117188 * scale,
        (375 - 225.554688) * scale,
        242.65625 * scale,
        (375 - 225.554688) * scale,
    )
    path.lineTo(205.050781 * scale, (375 - 225.554688) * scale)
    path.lineTo(205.050781 * scale, (375 - 248.792969) * scale)
    path.lineTo(242.65625 * scale, (375 - 248.792969) * scale)
    path.curveTo(
        273.972656 * scale,
        (375 - 248.792969) * scale,
        299.410156 * scale,
        (375 - 223.371094) * scale,
        299.410156 * scale,
        (375 - 192.066406) * scale,
    )
    path.curveTo(
        299.410156 * scale,
        (375 - 160.761719) * scale,
        273.972656 * scale,
        (375 - 135.335938) * scale,
        242.65625 * scale,
        (375 - 135.335938) * scale,
    )
    path.closePath()
    path.fillColor = colors.HexColor("#518ecb")
    path.strokeColor = None
    drawing.add(path)
    return drawing


def question_block(styles, item):
    answer = clean(item.get("risposta"))
    sales = clean(item.get("gancio_sales"))
    flowables = [
        Paragraph(f"{item.get('id')}. {esc(item.get('domanda'))}", styles["question"]),
        Paragraph(esc(answer), styles["answer"]),
        Paragraph(f"<i>{esc(sales)}</i>", styles["sales"]),
    ]
    card = Table(
        [[flowables]],
        colWidths=[16.6 * cm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        ),
    )
    return KeepTogether([card, Spacer(1, 8)])


def build_pdf():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with SOURCE_JSON.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=1.75 * cm,
        leftMargin=1.75 * cm,
        topMargin=1.65 * cm,
        bottomMargin=1.75 * cm,
        title="E-Digit - Domande privacy per revisione DPO",
        author="E-Digit",
    )

    story = []
    logo = cover_logo()
    story.extend(
        [
            Spacer(1, 2.6 * cm),
            Table(
                [[logo]],
                colWidths=[16.6 * cm],
                style=TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                ),
            ),
            Spacer(1, 0.7 * cm),
            Paragraph("E-Digit", styles["cover_brand"]),
            Paragraph("Digital Compliance per le PMI: semplice, sicura, accessibile.", styles["motto"]),
            Paragraph(
                "Sei sicuro che ogni tassello della tua data privacy sia al posto giusto?",
                styles["cover_question"],
            ),
            Spacer(1, 1.3 * cm),
            HRFlowable(width="55%", thickness=1.3, color=EDIGIT_ORANGE, hAlign="CENTER"),
            PageBreak(),
        ]
    )

    for section_index, area in enumerate(data["aree"]):
        if section_index > 0:
            story.append(PageBreak())

        code = clean(area.get("codice_colore")).lower()
        area_color = AREA_COLORS.get(code, EDIGIT_BLUE)
        story.append(
            Table(
                [[Paragraph(esc(area["area"]), styles["section"])]],
                colWidths=[16.6 * cm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                        ("LINEBEFORE", (0, 0), (0, 0), 7, area_color),
                        ("LEFTPADDING", (0, 0), (-1, -1), 13),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                ),
            )
        )
        story.append(Spacer(1, 16))

        for item in area["domande"]:
            story.append(question_block(styles, item))

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return OUTPUT_PDF


if __name__ == "__main__":
    pdf_path = build_pdf()
    print(pdf_path)
