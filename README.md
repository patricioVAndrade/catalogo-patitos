# 🛒 Generador de Catálogo Estático - Patito's Bebe

Este proyecto toma un listado de productos desde un Excel y genera una página web estática (`index.html`) lista para publicar en GitHub Pages o compartir.

## 📂 Estructura del Proyecto

* **`setup_db.py`**: Script inicial. Crea la base de datos `tienda.db`.
* **`cargar_stock.py`**: Lee tu Excel de stock real, busca las fotos en tus carpetas de scraping, y carga todo en la base de datos.
* **`build.py`**: El "constructor". Lee la base de datos y genera el archivo `index.html`.
* **`templates/base.html`**: El diseño visual de la página (HTML + Estilos CSS).
* **`static/`**: Carpeta donde se guardan las imágenes y el favicon.
* **`index.html`**: El resultado final (Tu página web).

---

## 🚀 Instalación (Solo la primera vez)

1.  Abre la terminal en esta carpeta.
2.  Instala las librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🛠️ Flujo de Trabajo Diario (Cómo actualizar precios/stock)

Para actualizar tu página web, sigue estos 3 pasos en orden:

### Paso 1: Preparar los Datos
Asegúrate de tener en esta carpeta el archivo **`stock_real.xlsx`** con las columnas:
* `codigo` (Obligatorio)
* `nombre`
* `categoria`
* `precio`
* `foto` (Nombre del archivo, ej: `osito.jpg`)

*(Nota: Este Excel lo armas tú copiando los datos que te interesan de los resultados del Scraper).*

### Paso 2: Cargar la Base de Datos
Ejecuta este script para leer el Excel y copiar las fotos necesarias automáticamente:

```bash
python cargar_stock.py


###Opcional

Abrir Servidor de pruebas:  
python -m http.server 8000
.\cloudflared.exe tunnel --url http://localhost:8000


### NUEVO FLUJO 

EXTRACCIÓN (Minería):

Vas a ScrappingCoronel.

Ejecutas scraper_maestro.py.

Resultado: Miles de fotos y Excels sueltos en tu disco.

CONSOLIDACIÓN (Inteligencia):

Vas a Gestion_Stock.

Ejecutas consolidar_db_general.py.

Resultado: Tu base de datos productos_general.db se llena con TODO lo nuevo y actualiza precios de lo viejo.

(Aquí es donde en el futuro construirás tu Interfaz Visual para elegir qué vender).

PUBLICACIÓN (Venta):

(Por ahora manual): Copias datos de los Excels a stock_real.xlsx en Lista_Precios_Estatico.

(Futuro): Tu interfaz exportará automáticamente a stock_real.xlsx.

Vas a Lista_Precios_Estatico.

Ejecutas cargar_stock.py y build.py.

Resultado: Web actualizada.