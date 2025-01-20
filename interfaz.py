import tkinter as tk
from tkinter import ttk
import sqlite3

# Función para obtener la conexión a la base de datos
def obtener_conexion():
    return sqlite3.connect('indice_libreria.db')

# Función para actualizar la tabla con los libros
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

# Función para mostrar los detalles de un libro cuando se hace clic
def mostrar_detalles_libro(event, treeview):
    # Obtener el item seleccionado
    item_id = treeview.selection()[0]
    libro = treeview.item(item_id, "values")

    # Crear una nueva ventana para mostrar los detalles del libro
    detalles_ventana = tk.Toplevel()
    detalles_ventana.title(f"Detalles de {libro[3]}")  # Libro[3] es el título

    # Mostrar la información del libro en etiquetas
    detalles = [
        ("ID", libro[0]),
        ("Nombre archivo", libro[1]),
        ("Título", libro[2]),
        ("Autor", libro[3]),
        ("Idioma", libro[4]),
        ("Formatos", libro[5])
    ]

    # Agregar las etiquetas en la ventana de detalles
    for i, (campo, valor) in enumerate(detalles):
        tk.Label(detalles_ventana, text=f"{campo}: {valor}").pack(padx=10, pady=5)

# Función para editar una celda
def editar_celda(event, treeview):
    item = treeview.selection()[0]
    col = treeview.identify_column(event.x)
    col_index = int(col[1:]) - 1

    current_value = treeview.item(item, 'values')[col_index]

    def guardar_edicion():
        new_value = entry.get()
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE libros SET {treeview['columns'][col_index]} = ? WHERE id = ?", (new_value, item))
        conn.commit()
        conn.close()
        actualizar_tabla(treeview)
        edit_window.destroy()

    edit_window = tk.Toplevel(window)
    edit_window.title(f"Editar celda")
    tk.Label(edit_window, text=f"Nuevo valor para {treeview['columns'][col_index]}:").pack(pady=10)
    entry = tk.Entry(edit_window)
    entry.insert(0, current_value)
    entry.pack(pady=5)

    entry.bind('<Return>', lambda e: guardar_edicion())

    tk.Button(edit_window, text="Guardar", command=guardar_edicion).pack(pady=10)

# Función para mostrar un menú contextual con la opción de editar
def mostrar_menu_contextual(event, treeview):
    # Obtener el ítem sobre el que se ha hecho clic derecho
    item_id = treeview.identify('item', event.x, event.y)

    if item_id:
        # Crear un menú contextual
        menu = tk.Menu(window, tearoff=0)
        menu.add_command(label="Editar", command=lambda: editar_celda(event, treeview))
        menu.post(event.x_root, event.y_root)

# Función para mostrar la vista de la tabla
def mostrar_vista_tabla():
    # Limpiar la ventana
    for widget in window.winfo_children():
        widget.destroy()

    # Crear el Treeview para mostrar los libros
    treeview = ttk.Treeview(window, columns=("ID", "nombre_archivo", "titulo", "autor", "idioma", "formatos"), show="headings")
    treeview.pack(fill="both", expand=True)

    # Definir las columnas y encabezados
    treeview.heading("ID", text="ID")
    treeview.heading("nombre_archivo", text="Nombre archivo")
    treeview.heading("titulo", text="Título")
    treeview.heading("autor", text="Autor")
    treeview.heading("idioma", text="Idioma")
    treeview.heading("formatos", text="Formatos")

    # Ajustar las columnas
    treeview.column("ID", width=50)
    treeview.column("nombre_archivo", width=200)
    treeview.column("titulo", width=200)
    treeview.column("autor", width=150)
    treeview.column("idioma", width=100)
    treeview.column("formatos", width=150)

    # Barra de búsqueda
    search_frame = tk.Frame(window)
    search_frame.pack(pady=10)

    barra_busqueda = tk.Entry(search_frame, width=30)
    barra_busqueda.pack(side="left")

    buscar_button = tk.Button(search_frame, text="Buscar", command=lambda: actualizar_tabla(treeview, barra_busqueda.get()))
    buscar_button.pack(side="left", padx=5)

    # Actualizar la tabla con los datos de la base de datos
    actualizar_tabla(treeview)

    # Vincular el evento de doble clic para mostrar los detalles del libro
    treeview.bind("<Double-1>", lambda event: mostrar_detalles_libro(event, treeview))

    # Vincular el clic derecho para mostrar el menú contextual de edición
    treeview.bind("<Button-3>", lambda event: mostrar_menu_contextual(event, treeview))

# Función para iniciar la interfaz gráfica
def iniciar_interfaz():
    global window
    window = tk.Tk()
    window.title("Gestión de Librería")

    # Crear un contenedor para los botones de las vistas
    vista_frame = tk.Frame(window)
    vista_frame.pack(pady=10)

    # Botón para mostrar la vista de la tabla
    tabla_button = tk.Button(vista_frame, text="Vista de tabla", command=mostrar_vista_tabla)
    tabla_button.pack(side="left", padx=5)

    # Iniciar la vista inicial (Vista de tabla)
    mostrar_vista_tabla()

    # Ejecutar la interfaz
    window.mainloop()

# Iniciar la interfaz gráfica
if __name__ == "__main__":
    iniciar_interfaz()
