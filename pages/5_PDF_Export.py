from auth import require_login, show_logout_button
require_login("Host Reply Pro")

import json
import io
import os
import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from db import init_db, list_history, get_history_item


# ---------------------------
# App init
# ---------------------------
init_db()

st.set_page_config(page_title="PDF Export", page_icon="📄", layout="wide")
st.title("📄 PDF Export")
st.caption("Διάλεξε ένα history item και κατέβασέ το σαν PDF report.")


# ---------------------------
# Fonts (Greek/Unicode safe)
# ---------------------------
FONT_REGULAR_NAME = "DejaVu"
FONT_BOLD_NAME = "DejaVu-Bold"

FONT_REGULAR_PATH = os.path.join("assets", "fonts", "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join("assets", "fonts", "DejaVuSans-Bold.ttf")  # optional


def ensure_fonts():
    # Regular REQUIRED
    if FONT_REGULAR_NAME not in pdfmetrics.getRegisteredFontNames():
        if not os.path.exists(FONT_REGULAR_PATH):
            st.error(
                "Λείπει font για ελληνικά.\n\n"
                "Βάλε στο repo: assets/fonts/DejaVuSans.ttf\n"
                "(και προαιρετικά: assets/fonts/DejaVuSans-Bold.ttf)"
            )
            st.stop()
        pdfmetrics.registerFont(TTFont(FONT_REGULAR_NAME, FONT_REGULAR_PATH))

    # Bold OPTIONAL
    if FONT_BOLD_NAME not in pdfmetrics.getRegisteredFontNames():
        if os.path.exists(FONT_BOLD_PATH):
            pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, FONT_BOLD_PATH))


ensure_fonts()


# ---------------------------
# Load history
# ---------------------------
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


# ---------------------------
# Helpers
# ---------------------------
def wrap_to_width(text: str, font_name: str, font_size: int, max_width: float):
    """
    Wrap lines based on rendered width (points), not character count.
    Preserves newlines.
    """
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    out_lines = []

    for paragraph in text.split("\n"):
        if not paragraph.strip():
            out_lines.append("")
            continue

        words = paragraph.split()
        cur = ""

        for w in words:
            test = (cur + " " + w).strip()
            if pdfmetrics.stringWidth(test, font_name, font_size) <= max_width:
                cur = test
                continue

            # push current line
            if cur:
                out_lines.append(cur)

            # if single word too long, hard-split
            if pdfmetrics.stringWidth(w, font_name, font_size) > max_width:
                chunk = ""
                for ch in w:
                    test2 = chunk + ch
                    if pdfmetrics.stringWidth(test2, font_name, font_size) <= max_width:
                        chunk = test2
                    else:
                        out_lines.append(chunk)
                        chunk = ch
                cur = chunk
            else:
                cur = w

        if cur:
            out_lines.append(cur)

    return out_lines if out_lines else [""]


def make_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    left, right, top, bottom = 40, 40, 40, 50
    max_width = w - left - right
    y = h - top

    def new_page():
        nonlocal y
        c.showPage()
        y = h - top

    def set_font(bold: bool, size: int) -> str:
        # Use bold font only if registered; otherwise fallback to regular
        if bold and (FONT_BOLD_NAME in pdfmetrics.getRegisteredFontNames()):
            c.setFont(FONT_BOLD_NAME, size)
            return FONT_BOLD_NAME
        c.setFont(FONT_REGULAR_NAME, size)
        return FONT_REGULAR_NAME

    def write_block(
        text: str,
        bold: bool = False,
        size: int = 10,
        dy: int = 14,
        gap_before: int = 0,
    ):
        nonlocal y
        y -= gap_before
        font_name = set_font(bold, size)
        lines = wrap_to_width(text, font_name, size, max_width)

        for row in lines:
            if y < bottom:
                new_page()
                font_name = set_font(bold, size)
            c.drawString(left, y, row)
            y -= dy

    # ---- Content ----
    write_block("Host Reply Pro — Review Report", bold=True, size=14, dy=18)
    write_block(f"Created at: {item.get('created_at','-')}", gap_before=6)
    write_block(f"Property: {item.get('property_name') or '-'}")
    write_block(
        f"Platform: {item.get('platform','-')} | Tone: {item.get('tone','-')} | "
        f"Language: {item.get('language','-')} | Length: {item.get('length','-')}"
    )
    write_block(f"Sentiment: {item.get('sentiment','-')}", dy=16, gap_before=6)

    write_block("Summary:", bold=True, size=12, dy=16, gap_before=10)
    write_block(item.get("summary", "-") or "-")

    write_block("Highlights:", bold=True, size=12, dy=16, gap_before=10)
    write_block(", ".join(highlights) if highlights else "-")

    write_block("Issues:", bold=True, size=12, dy=16, gap_before=10)
    if issues:
        for it2 in issues:
            write_block(f"- {it2.get('label')} (sev {it2.get('severity')}): {it2.get('note')}")
    else:
        write_block("- None")

    write_block("Review:", bold=True, size=12, dy=16, gap_before=12)
    write_block(item.get("review", "") or "-")

    write_block("Reply:", bold=True, size=12, dy=16, gap_before=12)
    write_block(item.get("reply", "") or "-")

    c.save()
    buf.seek(0)
    return buf.read()


# ---------------------------
# UI
# ---------------------------
if st.button("📄 Generate PDF", type="primary"):
    pdf_bytes = make_pdf()
    st.download_button(
        "⬇️ Download PDF report",
        data=pdf_bytes,
        file_name=f"review_report_{chosen_id}.pdf",
        mime="application/pdf",
    )
    st.success("Ready ✅")
