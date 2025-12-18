import pandas as pd
import os

# --- CONFIGURACIÓN ---
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_STOCK = os.path.join(DIRECTORIO_ACTUAL, "stock_real.xlsx")

# --- EL MAPA DE TRADUCCIÓN (EL MISMO DEL CONSOLIDADOR) ---
MAPA_CATEGORIAS = {

    "Belleza_Accesorios": "Belleza y Accesorios",
    "Belleza": "Belleza y Accesorios",
    "Accesorios": "Belleza y Accesorios",

    # Marroquinería
    "Mochilas_Maletines": "Marroquineria",
    "Mochilas": "Marroquineria",
    "Articulos_Viaje": "Marroquineria",
    "Bandoleras": "Marroquineria",
    "Marroquinería": "Marroquineria", # Por si acaso con tilde
    
    # Librería
    "Cartucheras_Carpetas": "Libreria",
    "Cartucheras": "Libreria",
    "Libros": "Libreria",
    "Arte_Manualidades": "Libreria",
    "Escolar": "Libreria",
    "Papeleria": "Libreria",
    "Carpetas": "Libreria",
    
    # Hogar
    "Bazar_Cocina": "Hogar",
    "Deco_Hogar": "Hogar",
    "Aromatizacion_Velas": "Hogar",
    "Textil": "Hogar",
    "Higiene_Limpieza": "Hogar",
    "Bazar": "Hogar",
    
    # Juguetería
    "Pelucheria": "Pelucheria", 
    "Juguetes": "Jugueteria",
    "Peluches": "Pelucheria",
    
    # Cotillón
    "Navidad": "Cotillon",
    "Simbolos_Patrios": "Cotillon",
    
    # Verano
    "Verano": "Verano"
}

def normalizar(cat_actual):
    if pd.isna(cat_actual): return "Varios"
    cat_limpia = str(cat_actual).strip()
    
    # Si está en el mapa, devolvemos la traducción
    if cat_limpia in MAPA_CATEGORIAS:
        return MAPA_CATEGORIAS[cat_limpia]
    
    # Si ya es una de las correctas, la dejamos
    valores_correctos = list(MAPA_CATEGORIAS.values())
    if cat_limpia in valores_correctos:
        return cat_limpia
        
    return cat_limpia # Si no sabemos qué es, la dejamos igual (o podrías forzar "Varios")

def migrar():
    if not os.path.exists(ARCHIVO_STOCK):
        print("❌ No encuentro el archivo stock_real.xlsx")
        return

    print("📂 Leyendo Excel...")
    df = pd.read_excel(ARCHIVO_STOCK)
    
    if 'categoria' not in df.columns:
        print("❌ El Excel no tiene columna 'categoria'")
        return

    print("🔄 Traduciendo categorías...")
    # Aplicamos la función fila por fila
    df['categoria'] = df['categoria'].apply(normalizar)
    
    print("💾 Guardando cambios...")
    try:
        df.to_excel(ARCHIVO_STOCK, index=False)
        print("✅ ¡LISTO! Tu Excel de Stock ha sido estandarizado.")
        print("   Ahora abre tu App y verás las categorías limpias.")
    except PermissionError:
        print("❌ ERROR: Cierra el archivo Excel antes de ejecutar esto.")

if __name__ == "__main__":
    migrar()