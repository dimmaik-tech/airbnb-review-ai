import json
import io
import os
import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from db import init_db, list_history, get_history_item

init_db()

st.set_page_config(page_title="PDF Export", page_icon="📄", layout="wide")
st.title("📄 PDF Export")
st.caption("Διάλεξε ένα history item και κατέβασέ το σαν PDF report.")

# ---------------------------
# Font (Greek/Unicode safe)
# ---------------------------
FONT_REGULAR_NAME = "DejaVuSans"
FONT_BOLD_NAME = "DejaVuSans-Bold"

FONT_REGULAR_PATH = os.path.join("assets", "fonts", "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join("assets", "fonts", "DejaVuSans-Bold.ttf")  # optional

def ensure_fonts():
    # Regular required
    if FONT_REGULAR_NAME not in pdfmetrics.getRegisteredFontNames():
        if not os.path.exists(FONT_REGULAR_PATH):
            st.error(
                "Λείπει font για ελληνικά.\n\n"
                "Βάλε στο repo: assets/fonts/DejaVuSans.ttf"
            )
            st.stop()
        pdfmetrics.registerFont(TTFont(FONT_REGULAR_NAME, FONT_REGULAR_PATH))

    # Bold optional (αν δεν υπάρχει, θα κάνουμε bold με regular)
    if FONT_BOLD_NAME not in pdfmetrics.getRegisteredFontNames():
        if os.path.exists(FONT_BOLD_PATH):
            pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, FONT_BOLD_PATH))

ensure_fonts()

items = list_history(limit=100)
if not items:
    st.info("Δεν υπάρχει ιστορικό ακόμα.")
    st.stop()

ids = [it["id"] for it in items]
chosen_id = st.selectbox("Select history item", ids, index=0)

item = get_history_item(int(chosen_id))
if not item:
    st.error("Δεν βρέθηκε.")
    st.stop()

issues = json.loads(item["issues_json"]) if item.get("issues_json") else []
highlights = json.loads(item["highlights_json"]) if item.get("highlights_json") else []

def wrap_to_width(c: canvas.Canvas, text: str, font_name: str, font_size: int, max_width: float):
    """
    Wrap lines based on actual rendered width (points), not character count.
    Preserves newlines.
    """
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")  # blank line
            continue

        words = paragraph.split()
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if pdfmetrics.stringWidth(test, font_name, font_size) <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                # If a single word is too long, hard-split it
                if pdfmetrics.stringWidth(w, font_name, font_size) > max_width:
                    chunk = ""
                    for ch in w:
                        test2 = chunk + ch
                        if pdfmetrics.stringWidth(test2, font_name, font_size) <= max_width:
                            chunk = test2
                        else:
                            lines.append(chunk)
                            chunk = ch
                    if chunk:
                        cur = chunk
                    else:
                        cur = ""
                else:
                    cur = w
        if cur:
            lines.append(cur)

    return lines if lines else [""]

def make_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    left = 40
    right = 40
    top = 40
    bottom = 50
    max_width = w - left - right

    y = h - top

    def new_page():
        nonlocal y
        c.showPage()
        y = h - top

    def set_font(bold: bool, size: int):
        if bold and (FONT_BOLD_NAME in pdfmetrics.getRegisteredFontNames()):
            c.setFont(FONT_BOLD_NAME, size)
            return FONT_BOLD_NAME
        c.setFont(FONT_REGULAR_NAME, size)
        return FONT_REGULAR_NAME

    def line(txt: str, dy: int = 14, bold: bool = False, size: int = 10, gap_before: int = 0):
        nonlocal y
        y -= gap_before
        font_name = set_font(bold, size)
        wrapped = wrap_to_width(c, txt, font_name, size, max_width)

        for row in wrapped:
            if y < bottom:
                new_page()
                font_name = set_font(bold, size)
            c.drawString(left, y, row)
            y -= dy

    # ---- Content ----
    line("Host Reply Pro — Review Report", bold=True, size=14, dy=18, gap_before=0)
    line(f"Created at: {item['created_at']}", size=10, dy=14, gap_before=6)
    line(f"Property: {item.get('property_name') or '-'}", size=10, dy=14)
    line(
        f"Platform: {item['platform']} | Tone: {item['tone']} | Language: {item['language']} | Length: {item['length']}",
        size=10, dy=14
    )
    line(f"Sentiment: {item['sentiment']}", size=10, dy=16, gap_before=6)

    line("Summary:", bold=True, size=12, dy=16, gap_before=10)
    line(item.get("summary", "-") or "-", size=10, dy=14)

    line("Highlights:", bold=True, size=12, dy=16, gap_before=10)
    line(", ".join(highlights) if highlights else "-", size=10, dy=14)

    line("Issues:", bold=True, size=12, dy=16, gap_before=10)
    if issues:
        for it2 in issues:
            line(f"- {it2.get('label')} (sev {it2.get('severity')}): {it2.get('note')}", size=10, dy=14)
    else:
        line("- None", size=10, dy=14)

    line("Review:", bold=True, size=12, dy=16, gap_before=12)
    line(item.get("review", "") or "-", size=10, dy=14)

    line("Reply:", bold=True, size=12, dy=16, gap_before=12)
    line(item.get("reply", "") or "-", size=10, dy=14)

    c.save()
    buf.seek(0)
    return buf.read()

if st.button("📄 Generate PDF", type="primary"):
    pdf_bytes = make_pdf()
    st.download_button(
        "⬇️ Download PDF report",
        data=pdf_bytes,
        file_name=f"review_report_{chosen_id}.pdf",
        mime="application/pdf"
    )
    st.success("Ready ✅")
