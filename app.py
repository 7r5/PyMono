import csv
import os
from flask import Flask, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "props.csv")

COLOR_MAP = {
    "cafe": "#8b5a2b",
    "azul": "#1e56c4",
    "rosa": "#c84f9a",
    "naranja": "#f07e2b",
    "rojo": "#c31f2d",
    "amarillo": "#f1c40f",
    "verde": "#1f8a44",
    "morado": "#6b2e8c",
}


def read_properties(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if not row:
                continue
            blank_key = next((k for k in row if k is not None and k.strip() == ""), None)
            color_name = row.get("color", "").strip().lower()
            rows.append({
                "id": row.get("id-propiedad", "").strip(),
                "color": color_name,
                "display_color": COLOR_MAP.get(color_name, "#8e8e8e"),
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


@app.route("/")
def index():
    properties = read_properties(CSV_FILE)
    return render_template("index.html", properties=properties)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
