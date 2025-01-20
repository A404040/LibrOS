import tkinter as tk
from tkinter import ttk, messagebox
from funciones_bdd import actualizar_tabla  # Asegúrate de que esta función esté definida en funciones_bdd.py

# Función para mostrar la vista de la tabla
def mostrar_vista_tabla():
    # Limpiar la ventana
    for widget in window.winfo_children():
        widget.destroy()

    # Crear el Treeview para mostrar los libros
    treeview = ttk.Treeview(window, columns=("ID", "nombre_archivo", "titulo", "autor", "idioma", "formatos"), show="headings")
    treeview.pack(fill="both", expand=True)

    # Definir las columnas y encabezados
    for col in ("ID", "nombre_archivo", "titulo", "autor", "idioma", "formatos"):
        treeview.heading(col, text=col)
        treeview.column(col, width=150 if col != "ID" else 50)

    # Actualizar la tabla con los datos de la base de datos
    actualizar_tabla(treeview)

    # Barra de búsqueda
    search_frame = tk.Frame(window)
    search_frame.pack(pady=10)

    barra_busqueda = tk.Entry(search_frame, width=30)
    barra_busqueda.pack(side="left")

    buscar_button = tk.Button(search_frame, text="Buscar", command=lambda: actualizar_tabla(treeview, barra_busqueda.get()))
    buscar_button.pack(side="left", padx=5)

    # Botón para cambiar a Modo Edición
    tk.Button(window, text="Modo Edición", command=mostrar_modo_edicion).pack(pady=10)

# Función para mostrar el Modo Edición
def mostrar_modo_edicion():
    # Limpiar la ventana
    for widget in window.winfo_children():
        widget.destroy()

    # Crear un contenedor para las celdas editables
    frame = tk.Frame(window)
    frame.pack(fill="both", expand=True)

    # Suponiendo que cargamos los datos de la base de datos
    datos = cargar_datos()  # Esta función debe cargar los datos de los libros desde la base de datos
    columnas = ["ID", "nombre_archivo", "titulo", "autor", "idioma", "formatos"]

    # Crear etiquetas de encabezado para cada columna
    for j, col in enumerate(columnas):
        tk.Label(frame, text=col, borderwidth=1, relief="solid", width=20).grid(row=0, column=j)

    # Crear las celdas editables
    entradas = {}  # Guardar referencias a los campos de texto
    for i, libro in enumerate(datos):
        for j, valor in enumerate(libro):
            # Crear campo de entrada editable solo si no es la columna "ID"
            if j == 0:  # La columna ID no es editable
                tk.Label(frame, text=valor, borderwidth=1, relief="solid", width=20).grid(row=i + 1, column=j)
            else:
                entrada = tk.Entry(frame, width=20)
                entrada.insert(0, valor)
                entrada.grid(row=i + 1, column=j)
                entradas[(i, j)] = entrada  # Guardar referencia

    # Función para guardar los cambios
    def guardar_cambios():
        cambios = []
        for (i, j), entrada in entradas.items():
            valor_nuevo = entrada.get()
            valor_original = datos[i][j]
            if valor_nuevo != valor_original:  # Solo guardar si hay cambios
                cambios.append((columnas[j], valor_nuevo, datos[i][0]))  # (columna, nuevo_valor, id)

        if cambios:
            # Confirmar antes de aplicar cambios
            if messagebox.askyesno("Confirmar Cambios", "¿Deseas guardar los cambios?"):
                for columna, nuevo_valor, libro_id in cambios:
                    actualizar_celda_bd(columna, nuevo_valor, libro_id)  # Asegúrate de que esta función esté definida
                messagebox.showinfo("Cambios Guardados", "Se han guardado los cambios exitosamente.")
                mostrar_modo_edicion()  # Recargar la vista de edición
        else:
            messagebox.showinfo("Sin Cambios", "No se han detectado cambios.")

    # Botón para guardar los cambios
    tk.Button(window, text="Guardar Cambios", command=guardar_cambios).pack(pady=10)

    # Botón para volver a la Vista de Tabla
    tk.Button(window, text="Volver a Vista de Tabla", command=mostrar_vista_tabla).pack(pady=10)

# Función para cargar los datos desde la base de datos
def cargar_datos():
    # Esta función debería cargar los datos de los libros desde la base de datos y devolverlos
    conn = obtener_conexion()  # Asegúrate de que esta función esté definida correctamente en funciones_bdd.py
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_archivo, titulo, autor, idioma, formatos FROM libros")
    libros = cursor.fetchall()
    conn.close()
    return libros

# Función para obtener la conexión a la base de datos
def obtener_conexion():
    import sqlite3
    return sqlite3.connect('indice_libreria.db')

# Función para actualizar una celda en la base de datos
def actualizar_celda_bd(columna, nuevo_valor, libro_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE libros SET {columna} = ? WHERE id = ?", (nuevo_valor, libro_id))
    conn.commit()
    conn.close()

# Función para iniciar la interfaz
def iniciar_interfaz():
    global window
    window = tk.Tk()
    window.title("Gestión de Librería")
    window.geometry("800x600")

    # Mostrar la Vista de Tabla al inicio
    mostrar_vista_tabla()

    # Ejecutar la interfaz
    window.mainloop()
