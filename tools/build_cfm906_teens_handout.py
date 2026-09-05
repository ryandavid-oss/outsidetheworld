"""Build the two-per-page September 6 handout for ages 16-17."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "media/cfm906-teens/sunday-notes.pdf"
NAVY = HexColor("#1B365D")
SLATE = HexColor("#3D5255")
BLUE = HexColor("#6395EE")
LINE = HexColor("#A6AFBA")


def card(pdf, bottom):
    left, right = 36, 576
    top = bottom + 396
    pdf.setFillColor(SLATE)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(left, top - 30, "SUNDAY SCHOOL  /  SEPTEMBER 6, 2026")
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawString(left, top - 61, "A thought to keep")
    pdf.setFillColor(SLATE)
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(right, top - 59, "Your notes stay with you.")
    prompts = [
        "An idea about Christ's forgiveness I want to remember:",
        "A choice I could make during sacrament meeting:",
        "A question I want to explore about Christ or His gospel:",
    ]
    for index, prompt in enumerate(prompts):
        y = top - 91 - index * 60
        pdf.setStrokeColor(BLUE)
        pdf.setLineWidth(1.2)
        pdf.roundRect(left, y - 5, 19, 19, 5, stroke=1, fill=0)
        pdf.setFillColor(NAVY)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(left + 9.5, y + 0.5, str(index + 1))
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(left + 28, y, prompt)
        pdf.setStrokeColor(LINE)
        pdf.setLineWidth(0.5)
        pdf.line(left + 28, y - 35, right, y - 35)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, top - 270, "This week, I'll...")
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.5)
    pdf.line(left, top - 294, right, top - 294)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left, top - 318, "When:")
    pdf.line(left + 38, top - 318, right, top - 318)
    pdf.setFillColor(SLATE)
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(left, bottom + 47, "Thy word is a lamp unto my feet, and a light unto my path.")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(left, bottom + 32, "Psalm 119:105  /  King James Version")
    pdf.drawRightString(right, bottom + 32, "OUTSIDE THE WORLD")


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=letter, invariant=1)
    pdf.setTitle("A Thought to Keep - Sunday School Ages 16-17 - September 6, 2026")
    pdf.setAuthor("Outside the World")
    pdf.setSubject("Two half-sheet handouts per page. Print one card per student.")
    card(pdf, 396)
    card(pdf, 0)
    pdf.setStrokeColor(LINE)
    pdf.setDash(3, 4)
    pdf.setLineWidth(0.5)
    pdf.line(18, 396, 594, 396)
    pdf.showPage()
    pdf.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
