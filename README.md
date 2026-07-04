# PyMono

PyMono es un proyecto Python para generar tarjetas estilo Monopoly a partir de un archivo CSV.

## Qué hace
- Lee `props.csv`
- Genera un PDF con tarjetas de propiedad de 7x8 cm
- Crea caras frontales y reversos para imprimir y pegar

## Uso
1. Instala dependencias:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. Genera tarjetas directamente en PDF:
   ```bash
   python main.py
   ```
   - El resultado se guarda en `Tarjetas_Monopoly.pdf`.

3. O utiliza la versión web editable:
   ```bash
   python app.py
   ```
   - Abre `http://127.0.0.1:5000`.
   - Usa el botón "Imprimir / Guardar PDF" para generar el PDF desde el navegador.

## Archivos
- `main.py` — script principal
- `props.csv` — datos de las propiedades
- `Tarjetas_Monopoly.pdf` — resultado generado

## Notas
Se recomienda usar el entorno virtual local `.venv` para instalar `reportlab`.
