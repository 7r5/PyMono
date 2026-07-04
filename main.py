import csv
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

CSV_FILE = "props.csv"
OUTPUT_FILE = "Tarjetas_Monopoly.pdf"
CARD_WIDTH = 7 * cm
CARD_HEIGHT = 8 * cm
PAGE_MARGIN = 1 * cm
H_GAP = 0.6 * cm
V_GAP = 0.6 * cm
CARDS_PER_ROW = 2
CARDS_PER_COL = 3
CARDS_PER_PAGE = CARDS_PER_ROW * CARDS_PER_COL

COLOR_MAP = {
    "cafe": (0.55, 0.33, 0.17),
    "azul": (0.12, 0.3, 0.75),
    "rosa": (0.86, 0.36, 0.70),
    "naranja": (0.96, 0.55, 0.18),
    "rojo": (0.80, 0.1, 0.15),
    "amarillo": (0.96, 0.86, 0.18),
    "verde": (0.06, 0.55, 0.20),
    "morado": (0.55, 0.14, 0.55),
}

BACK_COLOR = (0.82, 0.05, 0.1)
CARD_BORDER_COLOR = (0.85, 0.85, 0.85)
CARD_FILL_COLOR = (0.97, 0.97, 0.98)


def read_properties(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if not row:
                continue
            blank_key = next((k for k in row if k is not None and k.strip() == ""), None)
            rows.append({
                "id": row.get("id-propiedad", "").strip(),
                "color": row.get("color", "").strip().lower(),
                "grupo": row.get(blank_key, "").strip() if blank_key else row.get("grupo", "").strip(),
                "titulo": row.get("titulo", "").strip(),
                "renta_simple": row.get("renta-simple", "").strip(),
                "renta_grupo": row.get("renta-grupo", "").strip(),
                "renta1": row.get("renta1", "").strip(),
                "renta2": row.get("renta2", "").strip(),
                "renta3": row.get("renta3", "").strip(),
                "renta4": row.get("renta4", "").strip(),
                "renta_hotel": row.get("renta-hotel", "").strip(),
                "costo_casa": row.get("costo-casa", "").strip(),
                "costo_hotel": row.get("costo-hotel", "").strip(),
                "hipotecado_por": row.get("hipotecado por", "").strip(),
                "para_deshipotecar": row.get("para deshipotecar", "").strip(),
            })
    return rows


def get_rgb_color(color_name):
    return COLOR_MAP.get(color_name.lower(), (0.65, 0.65, 0.65))


def wrap_text(text, max_chars):
    lines = textwrap.wrap(text, width=max_chars)
    return lines if lines else [""]


def draw_house_icon(c, x, y, color):
    c.setFillColorRGB(*color)
    c.roundRect(x, y, 0.35 * cm, 0.35 * cm, 0.08 * cm, fill=1, stroke=0)


def draw_front_card(c, x, y, prop):
    c.saveState()

    c.setFillColorRGB(*CARD_FILL_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, 0.3 * cm, fill=1, stroke=0)
    c.setStrokeColorRGB(*CARD_BORDER_COLOR)
    c.setLineWidth(0.8)
    c.roundRect(x + 0.06 * cm, y + 0.06 * cm, CARD_WIDTH - 0.12 * cm, CARD_HEIGHT - 0.12 * cm, 0.25 * cm, fill=0, stroke=1)

    header_height = 1.8 * cm
    color_rgb = get_rgb_color(prop["color"])
    c.setFillColorRGB(*color_rgb)
    c.roundRect(x + 0.1 * cm, y + CARD_HEIGHT - header_height - 0.1 * cm, CARD_WIDTH - 0.2 * cm, header_height, 0.2 * cm, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 11)
    title_lines = wrap_text(prop["titulo"], 18)
    title_y = y + CARD_HEIGHT - 0.6 * cm
    for line in title_lines[:2]:
        c.drawCentredString(x + CARD_WIDTH / 2, title_y, line.upper())
        title_y -= 0.45 * cm

    if prop["grupo"]:
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 1.25 * cm, prop["grupo"].upper())

    body_x = x + 0.35 * cm
    body_w = CARD_WIDTH - 0.7 * cm
    body_y = y + 0.55 * cm
    body_h = CARD_HEIGHT - header_height - 1.05 * cm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(body_x, body_y, body_w, body_h, 0.18 * cm, fill=1, stroke=0)
    c.setStrokeColorRGB(0.85, 0.85, 0.85)
    c.setLineWidth(0.6)
    c.roundRect(body_x, body_y, body_w, body_h, 0.18 * cm, fill=0, stroke=1)

    section_x = body_x + 0.25 * cm
    section_right = body_x + body_w - 0.25 * cm
    current_y = body_y + body_h - 0.3 * cm

    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColorRGB(0.13, 0.13, 0.13)
    c.drawString(section_x, current_y, "RENTA")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(section_right, current_y, f"${prop['renta_simple']}")
    current_y -= 0.45 * cm

    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.setLineWidth(0.5)
    c.line(section_x, current_y, section_right, current_y)
    current_y -= 0.35 * cm

    c.setFont("Helvetica", 7)
    for label, key, icons in [
        ("With 1 House", "renta1", 1),
        ("With 2 Houses", "renta2", 2),
        ("With 3 Houses", "renta3", 3),
        ("With 4 Houses", "renta4", 4),
        ("With HOTEL", "renta_hotel", 0),
    ]:
        c.drawString(section_x, current_y, label)
        if icons > 0:
            icon_x = section_x + 5.5 * cm
            for i in range(icons):
                draw_house_icon(c, icon_x + i * 0.45 * cm, current_y - 0.07 * cm, (0.08, 0.55, 0.18))
        else:
            draw_house_icon(c, section_x + 5.5 * cm, current_y - 0.07 * cm, (0.85, 0.08, 0.12))
        c.drawRightString(section_right, current_y, f"${prop[key]}")
        current_y -= 0.35 * cm

    current_y -= 0.15 * cm
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.setLineWidth(0.5)
    c.line(section_x, current_y, section_right, current_y)
    current_y -= 0.35 * cm

    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(section_x, current_y, "MORTGAGE VALUE")
    current_y -= 0.35 * cm
    c.setFont("Helvetica", 7)
    c.drawString(section_x, current_y, f"${prop['hipotecado_por']}")
    current_y -= 0.35 * cm
    c.drawString(section_x, current_y, f"Houses cost ${prop['costo_casa']} each")
    current_y -= 0.28 * cm
    c.drawString(section_x, current_y, f"Hotels ${prop['costo_hotel']} plus 4 houses")

    c.restoreState()


def draw_back_card(c, x, y, prop):
    c.saveState()

    c.setFillColorRGB(*CARD_FILL_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, 0.3 * cm, fill=1, stroke=0)
    c.setStrokeColorRGB(*CARD_BORDER_COLOR)
    c.setLineWidth(0.8)
    c.roundRect(x + 0.06 * cm, y + 0.06 * cm, CARD_WIDTH - 0.12 * cm, CARD_HEIGHT - 0.12 * cm, 0.25 * cm, fill=0, stroke=1)

    header_height = 1.4 * cm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(x + 0.35 * cm, y + CARD_HEIGHT - header_height - 0.35 * cm, CARD_WIDTH - 0.7 * cm, header_height, 0.25 * cm, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0.11, 0.11, 0.11)
    c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 0.9 * cm, "HIPOTECAR")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 1.3 * cm, prop["titulo"])
    if prop["grupo"]:
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 1.7 * cm, prop["grupo"].upper())

    body_x = x + 0.35 * cm
    body_y = y + 0.55 * cm
    body_w = CARD_WIDTH - 0.7 * cm
    body_h = CARD_HEIGHT - header_height - 1.1 * cm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(body_x, body_y, body_w, body_h, 0.18 * cm, fill=1, stroke=0)
    c.setStrokeColorRGB(0.85, 0.85, 0.85)
    c.setLineWidth(0.6)
    c.roundRect(body_x, body_y, body_w, body_h, 0.18 * cm, fill=0, stroke=1)

    section_x = body_x + 0.25 * cm
    section_right = body_x + body_w - 0.25 * cm
    current_y = body_y + body_h - 0.35 * cm

    c.setFont("Helvetica-Bold", 8)
    c.drawString(section_x, current_y, "Mortgage Value")
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(section_right, current_y, f"${prop['hipotecado_por']}")
    current_y -= 0.45 * cm

    c.setFont("Helvetica", 7)
    c.drawString(section_x, current_y, f"Houses cost ${prop['costo_casa']} each")
    current_y -= 0.32 * cm
    c.drawString(section_x, current_y, f"Hotels ${prop['costo_hotel']} plus 4 houses")
    current_y -= 0.45 * cm

    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0.74, 0.16, 0.21)
    c.drawCentredString(x + CARD_WIDTH / 2, body_y + 0.35 * cm, "DESHIPOTECAR")
    c.restoreState()


def card_position(index, page_width, page_height):
    page_index = index % CARDS_PER_PAGE
    row = page_index // CARDS_PER_ROW
    col = page_index % CARDS_PER_ROW
    x = PAGE_MARGIN + col * (CARD_WIDTH + H_GAP)
    y_top = page_height - PAGE_MARGIN - CARD_HEIGHT
    y = y_top - row * (CARD_HEIGHT + V_GAP)
    return x, y


def create_pdf(properties):
    c = canvas.Canvas(OUTPUT_FILE, pagesize=letter)
    page_width, page_height = letter

    for idx, prop in enumerate(properties):
        if idx > 0 and idx % CARDS_PER_PAGE == 0:
            c.showPage()
        x, y = card_position(idx, page_width, page_height)
        draw_front_card(c, x, y, prop)
    c.showPage()

    for idx, prop in enumerate(properties):
        if idx > 0 and idx % CARDS_PER_PAGE == 0:
            c.showPage()
        x, y = card_position(idx, page_width, page_height)
        draw_back_card(c, x, y, prop)

    c.save()
    print(f"PDF generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        props = read_properties(CSV_FILE)
        if not props:
            print(f"No se encontraron propiedades en {CSV_FILE}.")
        else:
            create_pdf(props)
    except FileNotFoundError:
        print(f"No se encontró el archivo: {CSV_FILE}")
    except Exception as exc:
        print(f"Error al generar el PDF: {exc}")
