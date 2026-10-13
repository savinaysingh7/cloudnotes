from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, PageTemplate, PageBreak,
    Paragraph, Spacer, Table, TableStyle, Preformatted, KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CloudNotes_Project_Report.md"
OUTPUT = ROOT / "CloudNotesProjectReport.pdf"
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 19 * mm
TOP = 20 * mm
BOTTOM = 18 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    "CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=25, leading=31, textColor=colors.HexColor("#123B56"),
    alignment=TA_CENTER, spaceAfter=18 * mm
))
styles.add(ParagraphStyle(
    "CoverMeta", parent=styles["Normal"], fontSize=13, leading=20,
    textColor=colors.HexColor("#34566B"), alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    "ReportH1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=17, leading=22, textColor=colors.HexColor("#123B56"),
    spaceBefore=13, spaceAfter=8, keepWithNext=True
))
styles.add(ParagraphStyle(
    "ReportH2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=12.5, leading=16, textColor=colors.HexColor("#167A78"),
    spaceBefore=9, spaceAfter=5, keepWithNext=True
))
styles.add(ParagraphStyle(
    "ReportH3", parent=styles["Heading3"], fontName="Helvetica-Bold",
    fontSize=10.5, leading=13, textColor=colors.HexColor("#34566B"),
    spaceBefore=7, spaceAfter=4, keepWithNext=True
))
styles.add(ParagraphStyle(
    "ReportBody", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=9.1, leading=13.2, alignment=TA_JUSTIFY, spaceAfter=6
))
styles.add(ParagraphStyle(
    "ReportCell", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=7.6, leading=9.6, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    "ReportCellHeader", parent=styles["ReportCell"], fontName="Helvetica-Bold",
    textColor=colors.white
))
styles.add(ParagraphStyle(
    "ReportCode", parent=styles["Code"], fontName="Courier",
    fontSize=7.3, leading=9.2, leftIndent=6, rightIndent=6,
    backColor=colors.HexColor("#F2F5F7"), borderPadding=5,
    spaceBefore=3, spaceAfter=7
))
styles.add(ParagraphStyle(
    "ReportCaption", parent=styles["Italic"], fontName="Helvetica-Oblique",
    fontSize=8, leading=10, textColor=colors.HexColor("#536B78"),
    alignment=TA_CENTER, spaceAfter=8
))


def inline_markup(text):
    text = text.replace("\u2010", "-").replace("\u2011", "-")
    text = text.replace("\u2012", "-").replace("\u2013", "-")
    text = text.replace("\u2014", "-").replace("\u2212", "-")
    text = escape(text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#167A78">\1</link>', text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8">\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    return text


def parse_table_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def make_table(lines):
    parsed = [parse_table_row(line) for line in lines]
    if len(parsed) > 1 and all(re.fullmatch(r"\s*:?-{3,}:?\s*", c) for c in parsed[1]):
        parsed.pop(1)
    columns = max(len(row) for row in parsed)
    data = []
    for row_index, row in enumerate(parsed):
        row = row + [""] * (columns - len(row))
        cell_style = styles["ReportCellHeader"] if row_index == 0 else styles["ReportCell"]
        data.append([Paragraph(inline_markup(cell), cell_style) for cell in row])
    widths = [CONTENT_W / columns] * columns
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123B56")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FAFB")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C8D0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(filename, pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT,
                         topMargin=TOP, bottomMargin=BOTTOM,
                         title="CloudNotes Project Report",
                         author="Savinay Singh",
                         subject="INT378: Advancements in Cloud and DevOps")
        frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM,
                      id="normal", leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="report", frames=frame, onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        if doc.page > 1:
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#B7C8D0"))
            canvas.setLineWidth(0.5)
            canvas.line(LEFT, PAGE_H - 13 * mm, PAGE_W - RIGHT, PAGE_H - 13 * mm)
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#536B78"))
            canvas.drawString(LEFT, PAGE_H - 10 * mm, "CloudNotes | INT378 Project Report")
            canvas.drawRightString(PAGE_W - RIGHT, 10 * mm, f"Page {doc.page}")
            canvas.restoreState()


def build_story():
    text = SOURCE.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = "CloudNotes Project Report"
    metadata = []
    while lines and lines[0].startswith("%"):
        value = lines.pop(0).lstrip("% ").strip()
        if value:
            metadata.append(value)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and lines[0].strip() == "\\newpage":
        lines.pop(0)
    if metadata and metadata[0] == title:
        metadata.pop(0)
    story = [Spacer(1, 39 * mm), Paragraph(escape(title), styles["CoverTitle"])]
    story.append(Spacer(1, 9 * mm))
    story.append(Paragraph("<br/>".join(escape(v) for v in metadata), styles["CoverMeta"]))
    story.append(Spacer(1, 21 * mm))
    story.append(Paragraph("Cloud-native application, infrastructure, delivery, and operations", styles["CoverMeta"]))
    story.append(PageBreak())

    i = 0
    paragraph = []
    in_code = False
    code_lines = []
    top_heading_count = 0

    def flush_paragraph():
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(p.strip() for p in paragraph)), styles["ReportBody"]))
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue
        if stripped == "\\newpage":
            flush_paragraph()
            i += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            if not in_code:
                in_code = True
                code_lines = []
            else:
                story.append(Preformatted("\n".join(code_lines), styles["ReportCode"], maxLineLength=90))
                in_code = False
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            story.append(make_table(table_lines))
            story.append(Spacer(1, 6))
            continue
        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_paragraph()
            alt, rel = image_match.groups()
            path = (ROOT / rel).resolve()
            if path.exists():
                im = Image(str(path))
                scale = min((CONTENT_W * 0.94) / im.imageWidth, (92 * mm) / im.imageHeight, 1)
                im.drawWidth = im.imageWidth * scale
                im.drawHeight = im.imageHeight * scale
                im.hAlign = "CENTER"
                story.append(KeepTogether([Spacer(1, 4), im, Paragraph(escape(alt), styles["ReportCaption"])]))
            else:
                story.append(Paragraph(f"[Figure not found: {escape(rel)}]", styles["ReportCaption"]))
            i += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level, value = len(heading.group(1)), heading.group(2)
            if level == 1:
                if value != "Contents" and top_heading_count > 0:
                    story.append(PageBreak())
                top_heading_count += 1
            style = {1: styles["ReportH1"], 2: styles["ReportH2"], 3: styles["ReportH3"]}[level]
            story.append(Paragraph(inline_markup(value), style))
            i += 1
            continue
        if stripped.startswith("- ") or stripped.startswith("* "):
            flush_paragraph()
            items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                item = re.sub(r"^\s*[-*]\s+", "", lines[i].strip())
                items.append(Paragraph("&bull;&nbsp; " + inline_markup(item), styles["ReportBody"]))
                i += 1
            for item in items:
                story.append(item)
            continue
        if re.fullmatch(r"[-*_]{3,}", stripped):
            flush_paragraph()
            story.append(Spacer(1, 8))
            i += 1
            continue
        paragraph.append(stripped)
        i += 1
    flush_paragraph()
    return story


if __name__ == "__main__":
    ReportDoc(str(OUTPUT)).build(build_story())
    print(f"Wrote {OUTPUT}")
