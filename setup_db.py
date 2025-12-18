import sqlite3

def init_db():
    conn = sqlite3.connect('tienda.db')
    c = conn.cursor()

    # ELIMINAMOS LA TABLA VIEJA SI EXISTE PARA EVITAR CONFLICTOS
    c.execute('DROP TABLE IF EXISTS productos')

    # CREAMOS LA TABLA NUEVA
    # 'codigo' ahora es TEXT PRIMARY KEY (No se permiten duplicados)
    c.execute('''CREATE TABLE productos
                 (codigo TEXT PRIMARY KEY, 
                  nombre TEXT, 
                  categoria TEXT,
                  foto TEXT, 
                  precio REAL, 
                  activo INTEGER)''')

    # Datos de prueba (Ahora con código real)
    productos = [
        ('TEST001', 'Producto Prueba 1', 'Varios', 'https://via.placeholder.com/150', 1000, 1),
        ('TEST002', 'Producto Prueba 2', 'Varios', 'https://via.placeholder.com/150', 2000, 1)
    ]

    c.executemany("INSERT OR REPLACE INTO productos VALUES (?, ?, ?, ?, ?, ?)", productos)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos 'tienda.db' recreada. PK es ahora 'codigo'.")

if __name__ == '__main__':
    init_db()