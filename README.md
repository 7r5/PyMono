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
2. Ejecuta el script:
   ```bash
   python main.py
   ```
3. Revisa `Tarjetas_Monopoly.pdf`.

## Archivos
- `main.py` — script principal
- `props.csv` — datos de las propiedades
- `Tarjetas_Monopoly.pdf` — resultado generado

## Notas
Se recomienda usar el entorno virtual local `.venv` para instalar `reportlab`.
