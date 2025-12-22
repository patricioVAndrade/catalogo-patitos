import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import sys
import shutil

# --- CONFIGURACIÓN ---
MI_TELEFONO = "5493582405970" 

# --- RUTAS INTELIGENTES ---
def obtener_ruta_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

RUTA_BASE = obtener_ruta_base()
RUTA_EXCEL = os.path.join(RUTA_BASE, "stock_real.xlsx")
CARPETA_WEB_IMG = os.path.join(RUTA_BASE, "static", "img")

# --- RUTAS DONDE BUSCAR FOTOS (SCRAPING) ---
# Agregamos aquí las carpetas donde tus scrappers guardan las fotos originales
RUTA_BASE_PROYECTOS = os.path.abspath(os.path.join(RUTA_BASE, ".."))

RUTAS_SCRAPING = [
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingCoronel", "resultados"),
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingPopeye", "resultados"),
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingDyG", "resultados")
]

# --- FUNCIONES ---

def formato_moneda(valor):
    if valor is None or valor == "": return "0"
    try:
        val_float = float(valor)
        return "{:,.0f}".format(val_float).replace(",", ".")
    except:
        return str(valor)

def buscar_y_copiar_foto(nombre_foto):
    """Busca la foto en las carpetas de scraping y la copia a static/img"""
    if not nombre_foto or str(nombre_foto).lower() in ['nan', 'none', '']: 
        return False
    
    destino = os.path.join(CARPETA_WEB_IMG, nombre_foto)
    
    # 1. Si ya existe en la web, no hacemos nada (ahorramos tiempo)
    if os.path.exists(destino):
        return True

    # 2. Si no existe, salimos a buscarla a las carpetas de scraping
    print(f"🔍 Buscando foto perdida: {nombre_foto}...")
    
    for ruta_base in RUTAS_SCRAPING:
        if not os.path.exists(ruta_base): continue
        
        for root, dirs, files in os.walk(ruta_base):
            if nombre_foto in files:
                origen = os.path.join(root, nombre_foto)
                try:
                    if not os.path.exists(CARPETA_WEB_IMG):
                        os.makedirs(CARPETA_WEB_IMG)
                    shutil.copy(origen, destino)
                    print(f"   ✅ Encontrada y copiada: {nombre_foto}")
                    return True
                except Exception as e:
                    print(f"   ❌ Error copiando: {e}")
                    return False
    
    print(f"   ⚠️ No se encontró en ninguna carpeta de scraping.")
    return False

# --- PROCESO PRINCIPAL ---

def main():
    print("🚀 Iniciando construcción del sitio web...")

    # 1. Leer el Excel
    if not os.path.exists(RUTA_EXCEL):
        print(f"❌ ERROR: No encuentro el archivo {RUTA_EXCEL}")
        return

    try:
        df = pd.read_excel(RUTA_EXCEL, dtype=str)
        df = df.fillna('')
        
        # Filtramos solo estado SI
        if 'estado' in df.columns:
            df = df[df['estado'].str.upper() == 'SI']
        df = df.sort_values(by=['categoria', 'nombre'], ascending=[True, True])
        
        # --- ORDENAMIENTO (Corrección que pediste) ---
        # Ordenamos por Categoría y luego por Nombre
        df = df.sort_values(by=['categoria', 'nombre'], ascending=[True, True])
        # ---------------------------------------------
        
        print(f"📦 Procesando {len(df)} productos...")

    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return

    # 2. Procesar datos y BUSCAR FOTOS
    lista_productos = []
    categorias_unicas = set() 

    for index, row in df.iterrows():
        codigo = str(row['codigo']).strip()
        nombre = str(row['nombre']).strip()
        categoria = str(row['categoria']).strip()
        precio = row['precio']
        foto_nombre = str(row['foto']).strip()

        # --- LÓGICA DE FOTO MEJORADA ---
        # Intentamos buscar y copiar la foto si no está
        tiene_foto = buscar_y_copiar_foto(foto_nombre)
        
        if tiene_foto:
            ruta_foto = f"static/img/{foto_nombre}"
        else:
            # Si falló la búsqueda o no tiene nombre
            ruta_foto = "static/img/sin_foto.png" 

        # Crear diccionario
        prod = {
            'codigo': codigo,
            'nombre': nombre,
            'categoria': categoria,
            'precio_fmt': formato_moneda(precio),
            'foto': ruta_foto,
            # Lógica para etiqueta "NUEVO" (si usas la columna marcado en el futuro)
            'es_nuevo': False 
        }
        
        lista_productos.append(prod)
        if categoria: categorias_unicas.add(categoria)

    lista_categorias = sorted(list(categorias_unicas))

    # 3. Configurar Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    try:
        template = env.get_template('templates/base.html')
    except Exception as e:
        print(f"❌ Error cargando base.html: {e}")
        return

    # 4. Renderizar HTML
    fecha = datetime.now().strftime("%d/%m/%Y a las %H:%M hs")
    
    html_final = template.render(
        productos=lista_productos, 
        categorias=lista_categorias,
        fecha_actualizacion=fecha,
        telefono_ventas=MI_TELEFONO
    )

    # 5. Guardar index.html
    try:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_final)
        print("✅ ¡Sitio web generado correctamente en 'index.html'!")
    except Exception as e:
        print(f"❌ Error guardando index.html: {e}")

if __name__ == "__main__":
    main()