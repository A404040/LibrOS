import os
from funciones_bdd import (crear_base_datos, agregar_columna_formatos, 
                                   guardar_libros_en_db, mostrar_libros)
from funciones_lib import recorrer_libreria, obtener_metadatos
from interfaz import iniciar_interfaz

# PRINCIPAL

if __name__ == "__main__":
    # Crear la base de datos
    conn, cursor = crear_base_datos()

    # Añadir la columna 'formatos' si no existe
    agregar_columna_formatos(cursor)

    # Ruta a la carpeta de tu librería
    ruta_libreria = "../Libreria"  # Modificar la ruta a la carpeta de tus libros
    
    # Recorrer la librería y obtener los metadatos de estos
    libros = recorrer_libreria(ruta_libreria)

    # Guardar los libros en la base de datos
    guardar_libros_en_db(libros, conn, cursor)

    # Mostrar los libros almacenados (debug, se puede eliminar si sabes que está funcionando correctamente)
    mostrar_libros(cursor)

    # Cerrar la conexión a la base de datos
    conn.close()

    print("Índice creado y almacenado en la base de datos.")
    
    # Iniciar la interfaz gráfica después de procesar los libros
    iniciar_interfaz()
