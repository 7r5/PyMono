# PyMono

PyMono es una app web Flask para generar e imprimir todos los componentes del juego de mesa estilo Monopoly: tarjetas de propiedad, fortunas, desgracias, reversos y billetes.

## Características

- **Tarjetas de propiedad** — frente + reverso, 6.5×8 cm, 4 por fila en hoja carta portrait
- **Fortunas y Desgracias** — tarjetas horizontales 9×5.8 cm, 3 por fila en landscape, páginas separadas
- **Reversos de Fortunas/Desgracias** — selector de tipo y cantidad, fondo de color toggle
- **Billetes** — 7 denominaciones ($1–$500), selector + cantidad, rotados 90° para imprimir 10 por página en landscape
- **Toggle de color de fondo** — en fortunas, desgracias y reversos: imprime en hoja de color (sin fondo) o en hoja blanca (con fondo)
- **Bordes de corte** punteados visibles solo al imprimir
- **Contador de páginas** en reversos y billetes según la cantidad seleccionada

## Estructura

```
PyMonopoly/
├── app.py                   # Servidor Flask — rutas y lectura de datos
├── main.py                  # Generador PDF legacy con ReportLab
├── requirements.txt
├── data/
│   ├── props.csv            # Propiedades del juego
│   ├── fortunas.csv         # Tarjetas de fortuna
│   └── desgracias.csv       # Tarjetas de desgracia
├── static/
│   ├── styles.css           # Estilos globales (pantalla + impresión)
│   └── billetes/            # Imágenes PNG de billetes (1,5,10,20,50,100,500)
└── templates/
    ├── index.html           # Tarjetas de propiedad
    ├── fortunas.html        # Tarjetas de fortuna
    ├── desgracias.html      # Tarjetas de desgracia
    ├── reversos.html        # Reversos de fortunas/desgracias
    └── billetes.html        # Billetes
```

## Rutas

| URL | Descripción |
|---|---|
| `/` | Tarjetas de propiedad |
| `/fortunas` | Tarjetas de fortuna |
| `/desgracias` | Tarjetas de desgracia |
| `/reversos` | Reversos con selector de tipo y cantidad |
| `/billetes` | Billetes con selector de denominación y cantidad |

## Uso

1. Instala dependencias:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. Inicia el servidor web:
   ```bash
   python app.py
   ```
   Abre `http://127.0.0.1:5000` en Chrome.

3. Para cada sección, usa el botón **"Imprimir / Guardar PDF"**.

## Recomendaciones de impresión

- Usar **Chrome** (mejor soporte de `print-color-adjust`).
- Activar **"Gráficos de fondo"** en las opciones de impresión.
- Para tarjetas de propiedad: orientación **portrait**, márgenes mínimos.
- Para fortunas, desgracias, reversos y billetes: orientación **landscape**, márgenes mínimos.
- El toggle de color de fondo permite elegir entre imprimir sobre papel de color (fondo blanco) o sobre papel blanco (fondo de color).

## Notas

- `main.py` es un generador PDF legacy con ReportLab, no está integrado con las nuevas secciones.
- Los CSVs de fortunas y desgracias son de una columna: primera línea = encabezado, las siguientes = texto de cada tarjeta.
