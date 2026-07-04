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

CARD_BORDER_COLOR = (0.85, 0.85, 0.85)
CARD_FILL_COLOR = (1.0, 1.0, 1.0)


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
                "ciudad": row.get("ciudad", "").strip() or row.get("city", "").strip() or row.get("zone", "").strip(),
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
    c.saveState()
    c.setFillColorRGB(*color)
    c.roundRect(x, y, 0.34 * cm, 0.34 * cm, 0.07 * cm, fill=1, stroke=0)
    c.restoreState()


def draw_hotel_icon(c, x, y, color):
    c.saveState()
    c.setFillColorRGB(*color)
    c.rect(x, y, 0.42 * cm, 0.34 * cm, fill=1, stroke=0)
    c.restoreState()


def draw_front_card(c, x, y, prop):
    c.saveState()

    c.setFillColorRGB(*CARD_FILL_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, 0.3 * cm, fill=1, stroke=0)
    c.setStrokeColorRGB(*CARD_BORDER_COLOR)
    c.setLineWidth(0.85)
    c.roundRect(x + 0.05 * cm, y + 0.05 * cm, CARD_WIDTH - 0.1 * cm, CARD_HEIGHT - 0.1 * cm, 0.25 * cm, fill=0, stroke=1)

    color_rgb = get_rgb_color(prop["color"])
    header_height = 1.4 * cm
    c.setFillColorRGB(*color_rgb)
    c.rect(x + 0.05 * cm, y + CARD_HEIGHT - header_height - 0.05 * cm, CARD_WIDTH - 0.1 * cm, header_height, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 10)
    title_lines = wrap_text(prop["titulo"].upper(), 22)
    title_y = y + CARD_HEIGHT - 0.55 * cm
    for line in title_lines[:2]:
        c.drawCentredString(x + CARD_WIDTH / 2, title_y, line)
        title_y -= 0.35 * cm

    if prop["ciudad"]:
        c.setFont("Helvetica", 7.2)
        c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 1.05 * cm, prop["ciudad"].upper())

    body_x = x + 0.2 * cm
    body_w = CARD_WIDTH - 0.4 * cm
    current_y = y + CARD_HEIGHT - header_height - 0.55 * cm

    rent_height = 0.95 * cm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(body_x, current_y - rent_height, body_w, rent_height, 0.14 * cm, fill=1, stroke=1)
    c.setStrokeColorRGB(0.82, 0.82, 0.82)
    c.setLineWidth(0.6)
    c.roundRect(body_x, current_y - rent_height, body_w, rent_height, 0.14 * cm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColorRGB(0.11, 0.11, 0.11)
    c.drawString(body_x + 0.18 * cm, current_y - 0.46 * cm, "RENTA")
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(body_x + body_w - 0.18 * cm, current_y - 0.46 * cm, f"${prop['renta_simple']}")
    current_y -= rent_height + 0.25 * cm

    row_height = 0.42 * cm
    table_rows = [
        ("Renta de grupo", "renta_grupo", 0),
        ("1 casa", "renta1", 1),
        ("2 casas", "renta2", 2),
        ("3 casas", "renta3", 3),
        ("4 casas", "renta4", 4),
        ("Hotel", "renta_hotel", 0),
    ]

    icon_center = body_x + body_w * 0.55
    price_x = body_x + body_w - 0.18 * cm
    for index, (label, key, icons) in enumerate(table_rows):
        row_y = current_y - index * row_height
        c.setFont("Helvetica-Bold" if index == 0 else "Helvetica", 7.0)
        c.setFillColorRGB(0.37, 0.37, 0.37) if index == 0 else c.setFillColorRGB(0.11, 0.11, 0.11)
        c.drawString(body_x + 0.18 * cm, row_y - 0.08 * cm, label)
        if icons > 0:
            size = 0.32 * cm
            total_width = icons * size + (icons - 1) * 0.1 * cm
            icon_start = icon_center - total_width / 2
            for i in range(icons):
                draw_house_icon(c, icon_start + i * (size + 0.1 * cm), row_y - 0.18 * cm, (0.145, 0.690, 0.290))
        elif key == "renta_hotel":
            draw_hotel_icon(c, icon_center - 0.21 * cm, row_y - 0.18 * cm, (0.84, 0.16, 0.16))
        c.drawRightString(price_x, row_y - 0.08 * cm, f"${prop[key]}")

    current_y -= len(table_rows) * row_height + 0.2 * cm
    c.setStrokeColorRGB(0.82, 0.82, 0.82)
    c.setLineWidth(0.5)
    c.line(body_x + 0.18 * cm, current_y + 0.2 * cm, body_x + body_w - 0.18 * cm, current_y + 0.2 * cm)
    current_y -= 0.25 * cm

    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColorRGB(0.11, 0.11, 0.11)
    c.drawString(body_x + 0.18 * cm, current_y, "HIPOTECA")
    c.drawRightString(price_x, current_y, f"${prop['hipotecado_por']}")
    current_y -= 0.38 * cm

    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawString(body_x + 0.18 * cm, current_y, f"Casas cuestan ${prop['costo_casa']} cada una")
    current_y -= 0.3 * cm
    c.drawString(body_x + 0.18 * cm, current_y, f"Hotel cuesta ${prop['costo_hotel']} + 4 casas")

    c.restoreState()


def draw_back_card(c, x, y, prop):
    c.saveState()

    c.setFillColorRGB(*CARD_FILL_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, 0.3 * cm, fill=1, stroke=0)
    c.setStrokeColorRGB(*CARD_BORDER_COLOR)
    c.setLineWidth(0.85)
    c.roundRect(x + 0.05 * cm, y + 0.05 * cm, CARD_WIDTH - 0.1 * cm, CARD_HEIGHT - 0.1 * cm, 0.25 * cm, fill=0, stroke=1)

    color_rgb = get_rgb_color(prop["color"])
    header_height = 1.2 * cm
    c.setFillColorRGB(*color_rgb)
    c.rect(x + 0.05 * cm, y + CARD_HEIGHT - header_height - 0.05 * cm, CARD_WIDTH - 0.1 * cm, header_height, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 0.5 * cm, "HIPOTECAR")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0.11, 0.11, 0.11)
    c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - header_height - 0.25 * cm, prop["titulo"].upper())
    if prop["grupo"]:
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - header_height - 0.65 * cm, prop["grupo"].upper())

    body_x = x + 0.2 * cm
    body_w = CARD_WIDTH - 0.4 * cm
    body_y = y + 0.4 * cm
    body_h = CARD_HEIGHT - header_height - 0.55 * cm
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(body_x, body_y, body_w, body_h, 0.18 * cm, fill=1, stroke=1)

    section_x = body_x + 0.18 * cm
    section_right = body_x + body_w - 0.18 * cm
    current_y = body_y + body_h - 0.7 * cm

    c.setFont("Helvetica-Bold", 8)
    c.drawString(section_x, current_y, "Hipoteca")
    c.drawRightString(section_right, current_y, f"${prop['hipotecado_por']}")
    current_y -= 0.5 * cm

    c.setFont("Helvetica-Bold", 8)
    c.drawString(section_x, current_y, "Deshipotecar")
    c.drawRightString(section_right, current_y, f"${prop['para_deshipotecar']}")
    current_y -= 0.55 * cm

    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawString(section_x, current_y, f"Casas ${prop['costo_casa']} cada una")
    current_y -= 0.3 * cm
    c.drawString(section_x, current_y, f"Hotel ${prop['costo_hotel']} + 4 casas")

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
