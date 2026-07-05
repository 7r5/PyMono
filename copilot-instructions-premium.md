# Instrucciones de estilo para Copilot — PyMono

## Estado del proyecto

App web Flask completa para imprimir componentes de juego Monopoly personalizado.

### Secciones implementadas

| Sección | Ruta | Dimensiones | Layout impresión |
|---|---|---|---|
| Propiedades | `/` | 6.5×8 cm | 4 por fila, portrait, salto por fila |
| Fortunas | `/fortunas` | 9×5.8 cm | 3 por fila, landscape |
| Desgracias | `/desgracias` | 9×5.8 cm | 3 por fila, landscape |
| Reversos | `/reversos` | 9×5.8 cm | 3 por fila, landscape, ~9/página |
| Billetes | `/billetes` | 5×10 cm (rotados) | 5×2=10/página, landscape |

---

# Instrucciones de estilo — Tarjetas de Propiedades

## Objetivo

Generar tarjetas de propiedades con apariencia profesional, consistentes
entre sí e inspiradas en el lenguaje visual del Monopoly moderno,
manteniendo un diseño minimalista, limpio y altamente legible.

---

## Concepto General

- Tarjeta vertical.
- Dimensiones: **6.5×8 cm**.
- Fondo blanco puro.
- Diseño vectorial.
- Estilo editorial.
- Sin texturas, degradados, efectos 3D, biseles ni decoraciones innecesarias.

Debe parecer una carta de juego premium impresa.

---

## Estructura (de arriba hacia abajo)

1. Barra superior de color
2. Nombre de la propiedad
3. Ciudad o zona
4. Bloque de RENTA
5. Tabla de rentas
6. Separador
7. Hipoteca
8. Separador
9. Costos de construcción

Nunca cambiar este orden.

---

## Encabezado

- Barra sólida ocupando todo el ancho.
- Color según el grupo (mapeo en `app.py` → `COLOR_MAP`).
- Sin sombras ni degradados.

Nombre: MAYÚSCULAS · Blanco · Negrita · Centrado
Ciudad: Blanco · Más pequeña · Centrada

---

## Colores del grupo

```python
COLOR_MAP = {
    "cafe":    "#8b5a2b",
    "azul":    "#1e56c4",
    "rosa":    "#c84f9a",
    "naranja": "#f07e2b",
    "rojo":    "#c31f2d",
    "amarillo":"#f1c40f",
    "verde":   "#1f8a44",
    "morado":  "#6b2e8c",
}
```

Texto principal: `#111111` · Fondo: `#FFFFFF`

---

## Tipografía

- Inter, Montserrat, Segoe UI, Arial — nunca serif.
- Pesos: 800 (títulos), 700 (etiquetas), 400 (valores).

---

## Tabla de Rentas

Tres columnas: Descripción · Iconos · Precio.
Precios alineados a la derecha. Espaciado uniforme.

---

## Iconografía

- Casas: verde plano `#24B04A`, `<span class="icon house">` (div cuadrado)
- Hotel: rojo plano `#D62828`, `<span class="icon hotel">` (div cuadrado)

---

## Impresión de tarjetas de propiedad

- Layout: CSS Grid con `.print-row` wrappers (cada 4 tarjetas).
- En pantalla: `.print-row { display: contents }` — transparente para el grid.
- En print: `.cards-grid { display: block }` + `.print-row { display: flex; page-break-after: always }`.
- `@page { size: auto; margin: 6mm }` — NO fijar orientación para permitir al usuario elegir.
- Borde de corte: `outline: 1px dashed rgba(0,0,0,0.28); outline-offset: -4px` en `@media print`.

---

# Instrucciones de estilo — Fortunas y Desgracias

## Dimensiones

- Tarjeta horizontal: **9×5.8 cm** (ancho × alto).
- Barra superior fina (1.1 cm) con etiqueta "FORTUNA" / "DESGRACIA" en negro sobre fondo transparente.
- Cuerpo: texto izquierda (58%) + placeholder de imagen derecha (38%).

## Toggle de color de fondo

- Sin color (default): fondo blanco — para imprimir en papel de color.
- Con color:
  - Fortuna: `#fffbe6` (amarillo claro)
  - Desgracia: `#fff0d6` (naranja claro)
- Clase `.fyd-colores` en `.fyd-grid`; persistida en `localStorage`.

## Impresión

- 3 por fila, landscape, `@page margin: 3mm`.
- `.fyd-print-row { display: flex; page-break-inside: avoid }` — sin page-break-after (múltiples filas por página).

---

# Instrucciones de estilo — Reversos

## Dimensiones

- Mismo tamaño que fortunas/desgracias: **9×5.8 cm**.
- Sin color (default): fondo blanco, borde negro, caja interior con fondo claro (amarillo/rosa).
- Con color: fondo sólido (fortuna `#e09c10`, desgracia `#7A1A1A`), caja interior transparente, texto blanco.
- Toggle clase `.reverso-colores` en `.fyd-grid`; key localStorage: `reversoColor`.

## Controles UI (ocultos en print)

- Selector de tipo (Fortunas / Desgracias)
- Input de cantidad
- Contador: `ceil(cantidad / 9)` páginas

---

# Instrucciones de estilo — Billetes

## Dimensiones

- Imagen original: **10×5 cm** (landscape).
- Mostrados rotados 90°: **5×10 cm** (portrait).
- Técnica CSS: contenedor `width:5cm; height:10cm; overflow:hidden` + imagen `transform: translate(-50%,-50%) rotate(90deg)`.

## Layout de impresión

- 5 por fila × 2 filas = **10 por página** en landscape.
- `@page margin: 3mm`.
- Agrupados en `.bill-print-row` (5 por row).
- Contador: `ceil(cantidad / 10)` páginas.

## Archivos de imagen

`static/billetes/1.png`, `5.png`, `10.png`, `20.png`, `50.png`, `100.png`, `500.png`

---

# Reglas generales para Copilot

1. **No agregar comentarios ni docstrings** a código existente que no se modifica.
2. **No refactorizar** fuera del alcance de la tarea solicitada.
3. **Siempre usar `multi_replace_string_in_file`** para ediciones múltiples independientes.
4. **Siempre actualizar el nav** en todos los templates cuando se agregue o renombre una sección.
5. **Ocultar todo el UI en `@media print`**: nav, controles, toggles, botones — usar `display: none !important`.
6. **`print-color-adjust: exact`** en cualquier elemento con background de color que deba imprimirse.
7. **Bordes de corte** solo en `@media print` con `outline: 1px dashed` y `outline-offset: -4px`.
8. **`@page size: auto`** — nunca forzar orientación desde CSS para no bloquear el diálogo del navegador. Solo fijar márgenes.


## Objetivo

Generar tarjetas de propiedades con apariencia profesional, consistentes
entre sí e inspiradas en el lenguaje visual del Monopoly moderno,
manteniendo un diseño minimalista, limpio y altamente legible.

------------------------------------------------------------------------

# Concepto General

-   Tarjeta vertical.
-   Proporción aproximada 7 x 8 cm.
-   Fondo blanco puro.
-   Diseño vectorial.
-   Estilo editorial.
-   Sin texturas.
-   Sin degradados.
-   Sin efectos 3D.
-   Sin biseles.
-   Sin elementos decorativos innecesarios.

Debe parecer una carta de juego premium impresa.

------------------------------------------------------------------------

# Estructura (de arriba hacia abajo)

1.  Barra superior de color
2.  Nombre de la propiedad
3.  Ciudad o zona
4.  Bloque de RENTA
5.  Tabla de rentas
6.  Separador
7.  Hipoteca
8.  Separador
9.  Costos de construcción

Nunca cambiar este orden.

------------------------------------------------------------------------

# Distribución Vertical

-   Encabezado: 18%
-   Renta: 10%
-   Tabla: 42%
-   Hipoteca: 10%
-   Construcción: 12%
-   Márgenes: 8%

------------------------------------------------------------------------

# Encabezado

-   Barra sólida ocupando todo el ancho.
-   Color según el grupo.
-   Sin sombras.
-   Sin degradados.

Nombre: - MAYÚSCULAS - Blanco - Negrita - Centrado

Ciudad: - Blanco - Más pequeña - Centrada

------------------------------------------------------------------------

# Colores

Texto principal: #111111

Texto secundario: #666666

Fondo: #FFFFFF

Borde: #222222

Colores del grupo: - Marrón - Azul claro - Rosa - Naranja - Rojo -
Amarillo - Verde - Azul oscuro

Siempre planos.

------------------------------------------------------------------------

# Tipografía

Fuente recomendada:

-   Inter
-   Montserrat
-   Gotham
-   Avenir

Pesos:

Bold SemiBold Regular

Nunca serif.

------------------------------------------------------------------------

# Jerarquía

Nombre propiedad: 100%

RENTA: 80%

Valores monetarios: 75%

Etiquetas: 55%

Notas: 45%

------------------------------------------------------------------------

# Tabla de Rentas

Tres columnas.

Columna izquierda: Descripción.

Columna central: Íconos.

Columna derecha: Precio.

Todos los precios alineados a la derecha.

Espaciado uniforme.

------------------------------------------------------------------------

# Iconografía

Casas

-   Verde plano (#24B04A)
-   Mismo tamaño
-   Sin sombras
-   Sin perspectiva

Hotel

-   Rojo plano (#D62828)
-   Mismo estilo

------------------------------------------------------------------------

# Hipoteca

Bloque independiente.

Ejemplo

Valor Hipoteca \$60

SemiBold.

------------------------------------------------------------------------

# Construcción

Casas cuestan \$50 cada una

Hotel cuesta \$50 + 4 casas

Usar texto secundario.

------------------------------------------------------------------------

# Espaciado

Padding interno: 24--32 px

Separación vertical: 16 px

Todo alineado mediante una retícula.

------------------------------------------------------------------------

# Bordes

Borde: 1--2 px

Esquinas: 8--12 px

Sombra opcional: Muy sutil (\<5% opacidad).

------------------------------------------------------------------------

# Restricciones

NO usar:

-   degradados
-   texturas
-   efectos glossy
-   sombras fuertes
-   biseles
-   3D
-   serif
-   iconos diferentes entre tarjetas

------------------------------------------------------------------------

# Datos esperados

Nombre de propiedad

Ciudad

Color

Renta

Renta con 1 casa

Renta con 2 casas

Renta con 3 casas

Renta con 4 casas

Hotel

Costo casa

Costo hotel

Hipoteca

------------------------------------------------------------------------

# Reglas estrictas para IA

Estas reglas tienen prioridad.

-   No inventar elementos.
-   No alterar el orden.
-   Mantener exactamente la estructura definida.
-   Todos los importes alineados a la derecha.
-   Todos los iconos centrados.
-   Todas las líneas divisorias con el mismo grosor.
-   Mantener exactamente los mismos márgenes en todas las tarjetas.
-   Mantener apariencia consistente entre propiedades.

------------------------------------------------------------------------

# Prompt base

Diseña una tarjeta de propiedad vertical inspirada en el Monopoly
moderno. Estilo vectorial limpio y editorial. Fondo blanco, borde fino
con esquinas redondeadas, barra superior sólida del color del grupo,
nombre de la propiedad en mayúsculas centrado, ciudad debajo, bloque
destacado de RENTA, tabla perfectamente alineada con tres columnas
(descripción, iconos y precio), iconos planos de casas verdes y hotel
rojo, separadores finos, bloque independiente para hipoteca y costos de
construcción. Utiliza tipografía sans-serif moderna (Inter o
Montserrat), excelente jerarquía visual, mucho espacio en blanco,
alineación mediante retícula y apariencia de carta premium impresa. No
usar degradados, texturas, efectos 3D ni elementos decorativos
adicionales.
