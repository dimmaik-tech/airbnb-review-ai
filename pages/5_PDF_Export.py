import json
import io
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from db import init_db, list_history, get_history_item

init_db()

st.set_page_config(page_title="PDF Export", page_icon="📄", layout="wide")
st.title("📄 PDF Export")
st.caption("Διάλεξε ένα history item και κατέβασέ το σαν PDF report.")

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

def make_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    y = h - 40
    def line(txt, dy=14, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 11 if bold else 10)
        for chunk in wrap(txt, 95):
            c.drawString(40, y, chunk)
            y -= dy

    def wrap(text, width):
        words = (text or "").split()
        out, cur = [], []
        for wd in words:
            cur.append(wd)
            if len(" ".join(cur)) > width:
                cur.pop()
                out.append(" ".join(cur))
                cur = [wd]
        if cur:
            out.append(" ".join(cur))
        return out or [""]

    line("Host Reply Pro — Review Report", bold=True, dy=18)
    line(f"Created at: {item['created_at']}")
    line(f"Property: {item.get('property_name') or '-'}")
    line(f"Platform: {item['platform']} | Tone: {item['tone']} | Language: {item['language']} | Length: {item['length']}")
    line(f"Sentiment: {item['sentiment']}", dy=18)

    line("Summary:", bold=True)
    line(item.get("summary",""), dy=14)

    line("Highlights:", bold=True)
    line(", ".join(highlights) if highlights else "-", dy=14)

    line("Issues:", bold=True)
    if issues:
        for it2 in issues:
            line(f"- {it2.get('label')} (sev {it2.get('severity')}): {it2.get('note')}")
    else:
        line("- None")

    line("Review:", bold=True, dy=18)
    line(item["review"], dy=14)

    line("Reply:", bold=True, dy=18)
    line(item["reply"], dy=14)

    c.showPage()
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
