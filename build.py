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
RUTA_BASE_PROYECTOS = os.path.abspath(os.path.join(RUTA_BASE, ".."))

RUTAS_SCRAPING = [
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingCoronel", "resultados"),
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingPopeye", "resultados"),
    os.path.join(RUTA_BASE_PROYECTOS, "ScrappingDyG", "resultados")
]

# --- FUNCIONES ---

def calcular_precio_venta(valor_raw):
    """
    1. Limpia el valor del Excel (Costo Base).
    2. Multiplica por 2 (100% Ganancia).
    3. Redondea a la CENTENA más cercana (ej: 2750 -> 2800, 2348 -> 2300).
    """
    try:
        precio_costo = 0.0
        
        # 1. Limpieza de datos
        if isinstance(valor_raw, (int, float)):
            precio_costo = float(valor_raw)
        else:
            texto = str(valor_raw).strip().replace('$', '').strip()
            if ',' in texto:
                texto = texto.replace('.', '').replace(',', '.')
            elif '.' in texto:
                 pass 
            precio_costo = float(texto)
            
        # 2. MULTIPLICAR COSTO BASE POR 2
        precio_venta_bruto = precio_costo * 2.0
        
        # 3. REDONDEO INTELIGENTE A LA CENTENA (Termina en 00)
        # Fórmula: (Valor / 100) + 0.5 -> Convertir a entero -> Multiplicar por 100
        # Esto asegura el redondeo matemático estándar (2750 sube, 2749 baja)
        precio_final = int((precio_venta_bruto / 100) + 0.5) * 100
        
        return precio_final
        
    except Exception as e:
        return 0.0

def formato_moneda(valor):
    if valor is None or valor == "": return "0"
    try:
        val_float = float(valor)
        # Formato: 1.200 (sin decimales)
        return "{:,.0f}".format(val_float).replace(",", ".")
    except:
        return str(valor)

def sanitizar_texto(texto):
    """
    Limpia el texto para que sea seguro en atributos HTML.
    Reemplaza comillas dobles por el símbolo de pulgadas (″)
    """
    if not texto:
        return ""
    # Reemplazar comillas dobles por símbolo de pulgadas
    texto = str(texto).replace('"', '″')  # ″ es el símbolo correcto de pulgadas
    return texto

def buscar_y_copiar_foto(nombre_foto):
    """Busca la foto en las carpetas de scraping y la copia a static/img"""
    if not nombre_foto or str(nombre_foto).lower() in ['nan', 'none', '']: 
        return False
    
    destino = os.path.join(CARPETA_WEB_IMG, nombre_foto)
    
    if os.path.exists(destino):
        return True

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
    
    return False

# --- PROCESO PRINCIPAL ---

def main():
    print("🚀 Iniciando construcción del sitio web...")

    # 1. Leer el Excel (SOLO LECTURA DEL COSTO BASE)
    if not os.path.exists(RUTA_EXCEL):
        print(f"❌ ERROR: No encuentro el archivo {RUTA_EXCEL}")
        return

    try:
        df = pd.read_excel(RUTA_EXCEL) 
        df = df.fillna('')
        df.columns = df.columns.str.strip().str.lower()
        
        if 'estado' in df.columns:
            df = df[df['estado'].astype(str).str.upper() == 'SI']
        
        # --- ORDENAMIENTO: NUEVOS PRIMERO ---
        def calcular_prioridad(row):
            es_nuevo = str(row.get('nuevo', '')).upper() == 'SI'
            return 0 if es_nuevo else 1

        df['prioridad_orden'] = df.apply(calcular_prioridad, axis=1)
        
        # Ordenamos: Prioridad -> Categoria -> Nombre
        df = df.sort_values(by=['prioridad_orden', 'categoria', 'nombre'], ascending=[True, True, True])
        
        print(f"📦 Procesando {len(df)} productos...")

    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return

    # 2. Procesar datos
    lista_productos = []
    categorias_unicas = set() 

    for index, row in df.iterrows():
        codigo = str(row.get('codigo', '')).strip()
        nombre = sanitizar_texto(str(row.get('nombre', '')).strip())
        categoria = str(row.get('categoria', '')).strip()
        
        # --- CÁLCULO DE PRECIO ---
        # Tomamos el PRECIO BASE del Excel y aplicamos la fórmula x2 + Redondeo
        precio_crudo_base = row.get('precio', 0)
        precio_final_calculado = calcular_precio_venta(precio_crudo_base)
        
        foto_nombre = str(row.get('foto', '')).strip()
        es_oferta = True if str(row.get('oferta', '')).upper() == 'SI' else False
        es_nuevo = True if str(row.get('nuevo', '')).upper() == 'SI' else False

        # Buscar foto
        tiene_foto = buscar_y_copiar_foto(foto_nombre)
        ruta_foto = f"static/img/{foto_nombre}" if tiene_foto else "static/img/sin_foto.png"

        prod = {
            'codigo': codigo,
            'nombre': nombre,
            'categoria': categoria,
            'precio_fmt': formato_moneda(precio_final_calculado), 
            'foto': ruta_foto,
            'es_oferta': es_oferta,
            'es_nuevo': es_nuevo 
        }
        
        lista_productos.append(prod)
        if categoria: categorias_unicas.add(categoria)

    lista_categorias = sorted(list(categorias_unicas))

    # 3. Renderizar HTML
    env = Environment(loader=FileSystemLoader('.'))
    try:
        template = env.get_template('templates/base.html')
        
        fecha = datetime.now().strftime("%d/%m/%Y a las %H:%M hs")
        
        html_final = template.render(
            productos=lista_productos, 
            categorias=lista_categorias,
            fecha_actualizacion=fecha,
            telefono_ventas=MI_TELEFONO
        )

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_final)
        print("✅ ¡Sitio web generado correctamente en 'index.html'!")
        
    except Exception as e:
        print(f"❌ Error en Jinja2 o guardando archivo: {e}")

if __name__ == "__main__":
    main()