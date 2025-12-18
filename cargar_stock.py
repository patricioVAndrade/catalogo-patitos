import pandas as pd
import sqlite3
import os
import shutil

# --- CONFIGURACIÓN ---
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_BASE_PROYECTOS = os.path.abspath(os.path.join(DIRECTORIO_ACTUAL, ".."))

ARCHIVO_STOCK = os.path.join(DIRECTORIO_ACTUAL, "stock_real.xlsx")
DB_NOMBRE = os.path.join(DIRECTORIO_ACTUAL, "tienda.db")
CARPETA_WEB_IMG = os.path.join(DIRECTORIO_ACTUAL, "static", "img")

# Lista de carpetas donde buscar las fotos
RUTAS_SCRAPING = [
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingCoronel", "resultados"),
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingPopeye", "resultados"),
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingDyG", "resultados")
]

def buscar_y_copiar_foto(nombre_foto):
    # Validaciones básicas
    if pd.isna(nombre_foto) or str(nombre_foto).strip() == "": return False
    
    # --- CORRECCIÓN AQUÍ ---
    # 1. Recorremos la LISTA de carpetas principales (Coronel, Popeye...)
    for ruta_base in RUTAS_SCRAPING:
        
        # Si la carpeta no existe (ej: aun no scrapeaste Popeye), la saltamos para no dar error
        if not os.path.exists(ruta_base): continue

        # 2. Ahora sí, usamos os.walk en ESA carpeta específica
        for root, dirs, files in os.walk(ruta_base):
            if nombre_foto in files:
                try:
                    # Encontramos la foto, la copiamos y terminamos (return True)
                    shutil.copy2(os.path.join(root, nombre_foto), os.path.join(CARPETA_WEB_IMG, nombre_foto))
                    return True
                except: 
                    return False
    
    # Si recorrimos todas las carpetas y no apareció:
    return False

def cargar_base_datos():
    if not os.path.exists(ARCHIVO_STOCK):
        print(f"❌ Error: No encuentro '{ARCHIVO_STOCK}'")
        return

    if not os.path.exists(CARPETA_WEB_IMG): os.makedirs(CARPETA_WEB_IMG)

    print("📂 Leyendo Excel de Stock (Costos)...")
    try:
        df = pd.read_excel(ARCHIVO_STOCK)
    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return
    
    df.columns = df.columns.str.strip().str.lower()
    if 'codigo' not in df.columns:
        print("❌ El Excel debe tener columna 'codigo'")
        return

    conn = sqlite3.connect(DB_NOMBRE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos") 
    conn.commit()

    print("🚀 Calculando Precios de Venta (Costo x 2)...")
    contador = 0

    for index, row in df.iterrows():
        codigo = str(row.get('codigo', '')).strip()
        if not codigo or codigo.lower() == 'nan': continue

        nombre = str(row['nombre']).strip()
        categoria = str(row['categoria']).strip()
        
        # --- LÓGICA DE ESTADO ---
        estado_excel = str(row.get('estado', 'SI')).strip().upper()
        activo = 0 if estado_excel == 'NO' else 1

        # --- LÓGICA DE PRECIOS (COSTO -> VENTA) ---
        try:
            val_excel = row['precio']
            precio_costo = 0.0

            # 1. Leer el número correctamente
            if isinstance(val_excel, (int, float)):
                precio_costo = float(val_excel)
            else:
                texto = str(val_excel).strip().replace('$', '').strip()
                if ',' in texto:
                    texto = texto.replace('.', '').replace(',', '.')
                elif '.' in texto:
                    if texto.endswith('.0'): texto = texto[:-2]
                    else: texto = texto.replace('.', '')
                precio_costo = float(texto)

            # 2. MULTIPLICAR POR 2 (100% Ganancia)
            precio_venta_bruto = precio_costo * 2.0
            
            # 3. REDONDEAR (Múltiplos de 50)
            precio_final = round(precio_venta_bruto / 50) * 50

        except:
            precio_final = 0.0

        # FOTO
        nombre_foto = str(row['foto']).strip()
        se_copio = buscar_y_copiar_foto(nombre_foto)
        ruta_foto = f"static/img/{nombre_foto}" if se_copio else "static/img/sin_foto.png"

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO productos (codigo, nombre, categoria, foto, precio, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (codigo, nombre, categoria, ruta_foto, precio_final, activo))
            contador += 1
        except Exception as e:
            print(f"Error {codigo}: {e}")

    conn.commit()
    conn.close()
    
    print("-" * 50)
    print(f"✅ ¡LISTO! Se procesaron {contador} productos.")
    print("📢 Precios actualizados (x2). Ejecuta 'python build.py'.")

if __name__ == "__main__":
    cargar_base_datos()