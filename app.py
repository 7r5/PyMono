import csv
import hashlib
import json
import os
import threading
import base64
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "data", "props.csv")
IMAGENES_JSON = os.path.join(BASE_DIR, "data", "imagenes.json")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")
_lock = threading.Lock()
_generation_state = {"cancel": False}  # State dictionary for cancellation flag

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


def _procesar_una_imagen(h, prompt_estilo, model, client):
    """Procesa la generación de una imagen individual."""
    
    from PIL import Image
    from io import BytesIO
    
    # Early exit if cancelled before starting
    if _generation_state["cancel"]:
        return
    
    try:
        data = leer_imagenes()
        if h not in data:
            return
        
        texto = data[h]["texto"]
        tipo = data[h]["tipo"]
        prompt = f"{prompt_estilo}\n\nContexto de la tarjeta ({tipo}): {texto}"
        
        # Check again before making API call
        if _generation_state["cancel"]:
            return
        
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            n=1,
            response_format="b64_json",
        )
        
        # Check if cancelled after API response
        if _generation_state["cancel"]:
            return
        
        # Validate response structure
        if not response or not response.data or len(response.data) == 0:
            raise Exception(f"OpenAI returned empty response for model '{model}'")
        
        # Get image data from base64 response
        image_b64 = response.data[0].b64_json
        if not image_b64:
            raise Exception("OpenAI did not return image data.")
        
        # Decode base64 to image bytes
        try:
            img_data = base64.b64decode(image_b64)
            if not img_data:
                raise Exception("Failed to decode base64 image data from OpenAI")
        except Exception as e:
            raise Exception(f"Base64 decode error: {str(e)}")
        
        # Check if cancelled before processing image
        if _generation_state["cancel"]:
            return
        
        # Convert white background to transparent
        img = Image.open(BytesIO(img_data))
        
        # Convert to RGBA if not already
        img = img.convert("RGBA")
        data_arr = img.getdata()
        new_data = []
        
        # Replace near-white pixels with transparent
        for item in data_arr:
            # If pixel is near white (R,G,B > 240), make it transparent
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))  # transparent
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        
        # Check if cancelled before saving
        if _generation_state["cancel"]:
            return
        
        # Save as PNG with transparency
        filename = f"{tipo}_{h}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        img.save(filepath, "PNG")
        
        data = leer_imagenes()
        data[h]["imagen"] = f"/static/images/{filename}"
        data[h]["estado"] = "completado"
        data[h]["prompt_usado"] = prompt
        guardar_imagenes(data)
        
    except Exception as e:
        # Don't save error if generation was cancelled
        if not _generation_state["cancel"]:
            data = leer_imagenes()
            if h in data:
                data[h]["estado"] = "error"
                data[h]["error"] = str(e)
            guardar_imagenes(data)


def _generar_en_background(hashes, prompt_estilo, model="gpt-image-2"):
    """Background thread: calls OpenAI API in parallel and removes white backgrounds for transparency."""
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
    
    # Process images in parallel using ThreadPoolExecutor
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(_procesar_una_imagen, h, prompt_estilo, model, client): h for h in hashes}
            # Wait for all tasks to complete
            for future in futures:
                try:
                    future.result()
                except Exception:
                    pass  # Errors are handled inside _procesar_una_imagen
    finally:
        # After generation completes (or is cancelled), mark any pending/generating items as pending
        if _generation_state["cancel"]:
            data = leer_imagenes()
            for h in hashes:
                if h in data and data[h]["estado"] == "generando":
                    data[h]["estado"] = "pendiente"
            guardar_imagenes(data)
        
        # Reset cancel flag
        _generation_state["cancel"] = False


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
    model = body.get("model", "gpt-image-2")

    if not hashes:
        return jsonify({"error": "No hashes provided"}), 400

    # Reset cancel flag when new generation starts
    _generation_state["cancel"] = False
    
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
    t = threading.Thread(target=_generar_en_background, args=(hashes, prompt_estilo, model), daemon=True)
    t.start()

    return jsonify({"ok": True, "generando": len(hashes)}), 202


@app.route("/api/cancelar", methods=["POST"])
def api_cancelar():
    """Cancel all pending image generation."""
    _generation_state["cancel"] = True
    return jsonify({"ok": True, "mensaje": "Cancelación solicitada"}), 200


@app.route("/api/modelos")
def api_modelos():
    """List all available image generation models from OpenAI."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        models = client.models.list()
        
        # Filter for image generation models
        imagen_models = []
        for model in models:
            model_id = model.id
            # Include GPT Image models and DALL-E models
            if 'gpt-image' in model_id or 'dall-e' in model_id:
                imagen_models.append({
                    "id": model_id,
                    "owned_by": getattr(model, 'owned_by', 'unknown'),
                })
        
        return jsonify({
            "ok": True,
            "modelos": imagen_models,
            "total": len(imagen_models),
        })
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e),
        }), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
