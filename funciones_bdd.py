# funciones_bdd.py

import sqlite3

# Función para obtener la conexión a la base de datos
def obtener_conexion():
    return sqlite3.connect('indice_libreria.db')

# Función para crear la base de datos y las tablas necesarias
def crear_base_datos():
    conn = sqlite3.connect('indice_libreria.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS libros_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_archivo TEXT,
                        titulo TEXT,
                        autor TEXT,
                        genero TEXT,
                        idioma TEXT,
                        serie TEXT,
                        estado TEXT,
                        fecha_inicio TEXT,
                        fecha_finalizacion TEXT,
                        etiquetas TEXT,
                        formatos TEXT)''')

    cursor.execute("INSERT INTO libros_temp (id, nombre_archivo, titulo, autor, genero, idioma, serie, estado, fecha_inicio, fecha_finalizacion, etiquetas, formatos) "
                   "SELECT id, nombre_archivo, titulo, autor, genero, idioma, serie, estado, fecha_inicio, fecha_finalizacion, etiquetas, formatos FROM libros")

    cursor.execute("DROP TABLE IF EXISTS libros")
    cursor.execute("ALTER TABLE libros_temp RENAME TO libros")
    
    conn.commit()
    return conn, cursor

# Función para agregar la columna 'formatos' si no existe
def agregar_columna_formatos(cursor):
    cursor.execute("PRAGMA table_info(libros)")
    columnas = cursor.fetchall()
    columnas_existentes = [col[1] for col in columnas]
    if 'formatos' not in columnas_existentes:
        cursor.execute("ALTER TABLE libros ADD COLUMN formatos TEXT")
        print("Columna 'formatos' añadida correctamente.")

# Función para verificar si un libro existe en la base de datos
def libro_existe(cursor, titulo, autor):
    cursor.execute("SELECT * FROM libros WHERE titulo = ? AND autor = ?", (titulo, autor))
    return cursor.fetchone()

# Función para guardar libros en la base de datos
def guardar_libros_en_db(libros, conn, cursor):
    for libro in libros:
        libro_existente = libro_existe(cursor, libro['titulo'], libro['autor'])
        
        if libro_existente:
            formatos_existentes = libro_existente[-1]  # Última columna 'formatos'
            formatos = formatos_existentes.split(", ") if formatos_existentes else []
            if libro['tipo'] not in formatos:
                formatos.append(libro['tipo'])
                cursor.execute('''UPDATE libros SET formatos = ? WHERE id = ?''', 
                               (', '.join(formatos), libro_existente[0]))
        else:
            cursor.execute('''INSERT INTO libros (nombre_archivo, titulo, autor, genero, idioma, serie, estado, fecha_inicio, fecha_finalizacion, etiquetas, formatos)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (libro['nombre_archivo'], libro['titulo'], libro['autor'], '', libro['idioma'], '', 'No leído', '', '', '', libro['tipo']))
    conn.commit()

# Función para mostrar los libros almacenados
def mostrar_libros(cursor):
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    for libro in libros:
        print(libro)

# Función para actualizar la tabla en la interfaz gráfica con los datos de la base de datos
def actualizar_tabla(treeview, filtro=""):
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Modificar la consulta SQL para incluir el filtro de búsqueda
    if filtro:
        cursor.execute("SELECT id, nombre_archivo, titulo, autor, idioma, formatos FROM libros WHERE nombre_archivo LIKE ? OR titulo LIKE ? OR autor LIKE ? OR idioma LIKE ?", 
                       ('%' + filtro + '%', '%' + filtro + '%', '%' + filtro + '%', '%' + filtro + '%'))
    else:
        cursor.execute("SELECT id, nombre_archivo, titulo, autor, idioma, formatos FROM libros")

    libros = cursor.fetchall()
    conn.close()

    # Limpiar la tabla actual
    for i in treeview.get_children():
        treeview.delete(i)

    # Insertar los datos de los libros en la tabla
    for libro in libros:
        treeview.insert("", "end", iid=libro[0], values=libro)
