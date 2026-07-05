import csv
import hashlib
import json
import os
import threading
import urllib.request

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "data", "props.csv")
IMAGENES_JSON = os.path.join(BASE_DIR, "data", "imagenes.json")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")
_lock = threading.Lock()

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


def read_cards(csv_path, tipo):
    cards = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
        for line in lines[1:]:  # skip header row
            line = line.strip()
            if line:
                cards.append({"tipo": tipo, "texto": line})
    return cards


@app.route("/")
def index():
    properties = read_properties(CSV_FILE)
    return render_template("index.html", properties=properties, section="propiedades")


@app.route("/fortunas")
def fortunas():
    cards = read_cards(os.path.join(BASE_DIR, "data", "fortunas.csv"), "fortuna")
    data = leer_imagenes()
    for c in cards:
        c["imagen"] = data.get(card_hash(c["texto"]), {}).get("imagen")
    return render_template("fortunas.html", fortunas=cards, section="fortunas")


@app.route("/desgracias")
def desgracias():
    cards = read_cards(os.path.join(BASE_DIR, "data", "desgracias.csv"), "desgracia")
    data = leer_imagenes()
    for c in cards:
        c["imagen"] = data.get(card_hash(c["texto"]), {}).get("imagen")
    return render_template("desgracias.html", desgracias=cards, section="desgracias")


@app.route("/reversos")
def reversos():
    return render_template("reversos.html", section="reversos")


@app.route("/billetes")
def billetes():
    denominaciones = [1, 5, 10, 20, 50, 100, 500]
    return render_template("billetes.html", denominaciones=denominaciones, section="billetes")


# ── Imagenes helpers ──────────────────────────────────────────────────────────

def card_hash(texto):
    return hashlib.sha256(texto.encode()).hexdigest()[:8]


def leer_imagenes():
    with _lock:
        if not os.path.exists(IMAGENES_JSON):
            return {}
        with open(IMAGENES_JSON, encoding="utf-8") as f:
            return json.load(f)


def guardar_imagenes(data):
    with _lock:
        with open(IMAGENES_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def todas_las_cartas():
    fortunas = read_cards(os.path.join(BASE_DIR, "data", "fortunas.csv"), "fortuna")
    desgracias = read_cards(os.path.join(BASE_DIR, "data", "desgracias.csv"), "desgracia")
    cards = []
    for c in fortunas + desgracias:
        h = card_hash(c["texto"])
        cards.append({**c, "hash": h})
    return cards


def _generar_en_background(hashes, prompt_estilo):
    """Background thread: calls OpenAI DALL-E 3 for each hash and saves images."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    except Exception as e:
        data = leer_imagenes()
        for h in hashes:
            if h in data:
                data[h]["estado"] = "error"
                data[h]["error"] = str(e)
        guardar_imagenes(data)
        return

    for h in hashes:
        data = leer_imagenes()
        if h not in data:
            continue
        texto = data[h]["texto"]
        tipo = data[h]["tipo"]
        prompt = f"{prompt_estilo}\n\nContexto de la tarjeta ({tipo}): {texto}"
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            url = response.data[0].url
            filename = f"{tipo}_{h}.png"
            filepath = os.path.join(IMAGES_DIR, filename)
            urllib.request.urlretrieve(url, filepath)
            data = leer_imagenes()
            data[h]["imagen"] = f"/static/images/{filename}"
            data[h]["estado"] = "completado"
            data[h]["prompt_usado"] = prompt
            guardar_imagenes(data)
        except Exception as e:
            data = leer_imagenes()
            if h in data:
                data[h]["estado"] = "error"
                data[h]["error"] = str(e)
            guardar_imagenes(data)


# ── Imagenes routes ───────────────────────────────────────────────────────────

@app.route("/imagenes")
def imagenes():
    cards = todas_las_cartas()
    data = leer_imagenes()
    prompt_estilo = data.get("_config", {}).get(
        "prompt_estilo",
        "Ilustración estilo juego de mesa, diseño plano, trazo limpio, blanco y negro, líneas simples, sin degradados."
    )
    for c in cards:
        entry = data.get(c["hash"], {})
        c["imagen"] = entry.get("imagen")
        c["estado"] = entry.get("estado", "pendiente")
        c["error"] = entry.get("error")
    return render_template("imagenes.html", cards=cards, prompt_estilo=prompt_estilo, section="imagenes")


@app.route("/api/imagenes/estado")
def api_imagenes_estado():
    data = leer_imagenes()
    cards = todas_las_cartas()
    result = {}
    for c in cards:
        h = c["hash"]
        entry = data.get(h, {})
        result[h] = {
            "estado": entry.get("estado", "pendiente"),
            "imagen": entry.get("imagen"),
            "error": entry.get("error"),
        }
    return jsonify(result)


@app.route("/api/generar", methods=["POST"])
def api_generar():
    body = request.get_json()
    hashes = body.get("hashes", [])
    prompt_estilo = body.get("prompt_estilo", "")

    if not hashes:
        return jsonify({"error": "No hashes provided"}), 400

    # Save prompt_estilo in config
    data = leer_imagenes()
    data.setdefault("_config", {})["prompt_estilo"] = prompt_estilo

    # Mark each card as "generando"
    cards_map = {c["hash"]: c for c in todas_las_cartas()}
    for h in hashes:
        if h in cards_map:
            data[h] = {
                "tipo": cards_map[h]["tipo"],
                "texto": cards_map[h]["texto"],
                "estado": "generando",
                "imagen": data.get(h, {}).get("imagen"),
            }
    guardar_imagenes(data)

    # Launch background thread
    t = threading.Thread(target=_generar_en_background, args=(hashes, prompt_estilo), daemon=True)
    t.start()

    return jsonify({"ok": True, "generando": len(hashes)}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
