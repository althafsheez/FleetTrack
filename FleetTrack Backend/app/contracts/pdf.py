"""Render FleetTrack contract values over the approved two-page paper template."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


TEMPLATE_PATH = Path(__file__).with_name("templates") / "rental_agreement_template.pdf"
SOURCE_WIDTH = 989
SOURCE_HEIGHT = 1402


def _text(value) -> str:
    return "" if value is None else str(value).strip()


def _date(value) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    return value.strftime("%d/%m/%Y")


def _time(value) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return ""
    return value.strftime("%H:%M")


def _money(value) -> str:
    if value is None or value == "":
        return ""
    return f"{Decimal(str(value)):,.2f}"


class Overlay:
    """Draw using coordinates measured from the top-left of the source scan."""

    def __init__(self, pdf: canvas.Canvas, width: float, height: float):
        self.pdf = pdf
        self.width = width
        self.height = height
        self.x_scale = width / SOURCE_WIDTH
        self.y_scale = height / SOURCE_HEIGHT

    def value(self, value, x: float, y: float, *, size: float = 8.5, max_width: float = 220):
        value = _text(value)
        if not value:
            return
        font = "Helvetica"
        scaled_size = size
        available = max_width * self.x_scale
        while scaled_size > 6 and self.pdf.stringWidth(value, font, scaled_size) > available:
            scaled_size -= 0.25
        if self.pdf.stringWidth(value, font, scaled_size) > available:
            while value and self.pdf.stringWidth(value + "...", font, scaled_size) > available:
                value = value[:-1]
            value += "..."
        self.pdf.setFont(font, scaled_size)
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.drawCentredString(x * self.x_scale, self.height - y * self.y_scale, value)


def _agreement_overlay(pdf: canvas.Canvas, width: float, height: float, data: dict):
    page = Overlay(pdf, width, height)
    page.value(data.get("agreementNo"), 682, 184, size=10, max_width=210)

    page.value(data.get("passportNo"), 350, 225, max_width=245)
    page.value(data.get("hirerName"), 717, 225, max_width=245)
    page.value(data.get("nationality"), 717, 263, max_width=245)
    page.value(_date(data.get("passportExpiryDate")), 282, 300, max_width=235)
    page.value(_date(data.get("dateOfBirth")), 717, 300, max_width=245)
    page.value(data.get("drivingLicenseNo"), 717, 336, max_width=245)
    page.value(data.get("phone"), 282, 372, max_width=235)
    page.value(data.get("dlPlaceOfIssue"), 717, 372, max_width=245)
    page.value(_date(data.get("dlIssueDate")), 717, 409, max_width=245)
    page.value(_date(data.get("dlExpiryDate")), 717, 445, max_width=245)

    checkout = data.get("checkoutDate")
    page.value(_date(checkout), 323, 548, max_width=180)
    page.value(_time(checkout), 323, 580, max_width=180)
    page.value(data.get("vehicleMake"), 713, 542, max_width=250)
    page.value(data.get("plateNumber"), 713, 573, max_width=250)
    page.value(data.get("vehicleModel"), 713, 599, max_width=250)
    page.value(data.get("colour"), 713, 627, max_width=250)
    page.value(_money(data.get("dailyPrice")), 713, 656, max_width=250)
    page.value(_money(data.get("weeklyPrice")), 713, 684, max_width=250)
    page.value(_money(data.get("monthlyPrice")), 713, 713, max_width=250)
    page.value(_money(data.get("allowedKm")), 713, 762, max_width=250)


def _checklist_overlay(pdf: canvas.Canvas, width: float, height: float, data: dict):
    page = Overlay(pdf, width, height)
    page.value(data.get("plateNumber"), 206, 203, size=8, max_width=210)
    page.value(data.get("vehicleMake"), 535, 203, size=8, max_width=75)
    page.value(data.get("vehicleModel"), 718, 203, size=8, max_width=80)

    checkout = data.get("checkoutDate")
    page.value(_date(checkout), 744, 480, size=8, max_width=150)
    page.value(_time(checkout), 891, 480, size=8, max_width=88)
    page.value(data.get("hirerName"), 207, 1068, size=7, max_width=120)
    page.value(data.get("hirerName"), 255, 1112, size=7, max_width=180)


def render_contract_pdf(data: dict) -> bytes:
    """Return a static two-page PDF with vector text over the untouched template."""
    if not TEMPLATE_PATH.is_file():
        raise RuntimeError("Rental agreement PDF template is missing")

    template = PdfReader(str(TEMPLATE_PATH))
    if len(template.pages) != 2:
        raise RuntimeError("Rental agreement PDF template must contain exactly two pages")

    overlay_buffer = BytesIO()
    first_width = float(template.pages[0].mediabox.width)
    first_height = float(template.pages[0].mediabox.height)
    overlay = canvas.Canvas(overlay_buffer, pagesize=(first_width, first_height))
    _agreement_overlay(overlay, first_width, first_height, data)
    overlay.showPage()

    second_width = float(template.pages[1].mediabox.width)
    second_height = float(template.pages[1].mediabox.height)
    overlay.setPageSize((second_width, second_height))
    _checklist_overlay(overlay, second_width, second_height, data)
    overlay.save()
    overlay_buffer.seek(0)

    overlay_pdf = PdfReader(overlay_buffer)
    writer = PdfWriter(clone_from=str(TEMPLATE_PATH))
    for template_page, overlay_page in zip(writer.pages, overlay_pdf.pages, strict=True):
        template_page.merge_page(overlay_page)

    output = BytesIO()
    writer.write(output)
    return output.getvalue()
