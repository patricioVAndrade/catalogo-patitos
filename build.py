import sqlite3
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# --- CONFIGURACIÓN ---
MI_TELEFONO = "5493582405970" # Tu número (sin +)
# ---------------------

def formato_moneda(valor):
    if valor is None: return "0"
    return "{:,.0f}".format(valor).replace(",", ".")

def main():
    # 1. Conexión a BD
    conn = sqlite3.connect('tienda.db')
    conn.row_factory = sqlite3.Row
    
    try:
        
        cursor = conn.execute("SELECT * FROM productos WHERE activo = 1 ORDER BY categoria ASC")
        datos_db = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"❌ Error SQL: {e}")
        print("💡 Consejo: Asegúrate de haber corrido 'setup_db.py' y 'cargar_stock.py' nuevos.")
        return
    finally:
        conn.close()

    # 2. Procesar datos
    lista_productos = []
    # Usamos un SET para guardar categorías únicas automáticamente
    categorias_unicas = set() 

    for row in datos_db:
        prod = dict(row)
        
        # Asegurarnos de que el precio sea numérico antes de formatear
        precio = prod.get('precio', 0)
        prod['precio_fmt'] = formato_moneda(precio)
        
        lista_productos.append(prod)
        
        # Guardamos la categoría si existe
        cat = prod.get('categoria', 'Varios')
        if cat:
            categorias_unicas.add(cat)

    # Convertimos el set a lista ordenada para enviarla al HTML
    lista_categorias = sorted(list(categorias_unicas))

    # 3. Configurar Jinja2
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('base.html')

    # 4. Renderizar HTML
    fecha = datetime.now().strftime("%d/%m/%Y a las %H:%M hs")
    
    html_final = template.render(
        productos=lista_productos, 
        categorias=lista_categorias,
        fecha_actualizacion=fecha,
        telefono_ventas=MI_TELEFONO
    )

    # 5. Guardar index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_final)
    
    print(f"✅ Sitio generado correctamente.")
    print(f"   📊 Productos: {len(lista_productos)}")
    print(f"   📂 Categorías: {len(lista_categorias)}")

if __name__ == "__main__":
    main()