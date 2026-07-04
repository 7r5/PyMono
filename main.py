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


def draw_front_card(c, x, y, prop):
    c.saveState()
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    header_height = 1.4 * cm
    color_rgb = get_rgb_color(prop["color"])
    c.setFillColorRGB(*color_rgb)
    c.rect(x, y + CARD_HEIGHT - header_height, CARD_WIDTH, header_height, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 9)
    title_lines = wrap_text(prop["titulo"], 18)
    title_y = y + CARD_HEIGHT - 0.45 * cm
    for line in title_lines[:2]:
        c.drawCentredString(x + CARD_WIDTH / 2, title_y, line)
        title_y -= 0.45 * cm

    if prop["grupo"]:
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 1.15 * cm, prop["grupo"].upper())

    body_x = x + 0.4 * cm
    body_y = y + CARD_HEIGHT - header_height - 0.3 * cm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(body_x, body_y, "RENTAS")

    c.setFont("Helvetica", 7)
    for label, key in [
        ("Renta:", "renta_simple"),
        ("Renta grupo:", "renta_grupo"),
        ("1 casa:", "renta1"),
        ("2 casas:", "renta2"),
        ("3 casas:", "renta3"),
        ("4 casas:", "renta4"),
        ("Hotel:", "renta_hotel"),
    ]:
        body_y -= 0.35 * cm
        c.drawString(body_x, body_y, f"{label} ${prop[key]}")

    body_y -= 0.45 * cm
    c.setFont("Helvetica-Bold", 7)
    c.drawString(body_x, body_y, "COSTOS")
    body_y -= 0.35 * cm
    c.setFont("Helvetica", 7)
    c.drawString(body_x, body_y, f"Casa: ${prop['costo_casa']}  Hotel: ${prop['costo_hotel']}")

    body_y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 7)
    c.drawString(body_x, body_y, "HIPOTECA")
    body_y -= 0.35 * cm
    c.setFont("Helvetica", 7)
    c.drawString(body_x, body_y, f"Hipotecado por: ${prop['hipotecado_por']}")
    body_y -= 0.35 * cm
    c.drawString(body_x, body_y, f"Deshipotecar: ${prop['para_deshipotecar']}")

    icon_start_x = x + 0.4 * cm
    icon_y = y + 0.5 * cm
    square_size = 0.35 * cm
    c.setFillColorRGB(0, 0.45, 0.1)
    for i in range(4):
        c.rect(icon_start_x + i * (square_size + 0.15 * cm), icon_y, square_size, square_size, fill=1, stroke=0)
    c.setFillColorRGB(0.85, 0.05, 0.05)
    c.rect(icon_start_x + 4 * (square_size + 0.15 * cm), icon_y, square_size, square_size, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 6)
    c.drawString(icon_start_x, icon_y - 0.25 * cm, "1 2 3 4 H")

    c.restoreState()


def draw_back_card(c, x, y, prop):
    c.saveState()
    c.setFillColorRGB(*BACK_COLOR)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=0)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 1.5 * cm, "HIPOTECAR")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT - 2.3 * cm, "TARJETA DE PROPIEDAD")

    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT / 2 + 0.2 * cm, prop["titulo"])
    if prop["grupo"]:
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + CARD_WIDTH / 2, y + CARD_HEIGHT / 2 - 0.3 * cm, prop["grupo"].upper())

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x + CARD_WIDTH / 2, y + 1.7 * cm, "DESHIPOTECAR")
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
