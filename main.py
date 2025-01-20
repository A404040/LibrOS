import os
import sqlite3
import subprocess
import requests
import pandas as pd
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# FUNCIONES NECESARIAS PARA EL PROGRAMA

def obtener_metadatos(ruta_archivo):
    # Ejecutamos exiftool para obtener los metadatos en formato JSON
    resultado = subprocess.run(['exiftool', '-j', ruta_archivo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    metadatos = resultado.stdout.decode('utf-8')

    if metadatos:
        # Cargamos la salida en formato JSON para facilitar su manejo
        metadatos_json = json.loads(metadatos)
        return metadatos_json[0]  # Devolvemos el primer objeto de los metadatos (si hay varios)
    else:
        return {}

def crear_base_datos():
    conn = sqlite3.connect('indice_libreria.db')
    cursor = conn.cursor()

    # Eliminar la columna 'tipo' y crear una nueva tabla sin ella
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
                        formatos TEXT)''')  # Sin la columna 'tipo'

    cursor.execute("INSERT INTO libros_temp (id, nombre_archivo, titulo, autor, genero, idioma, serie, estado, fecha_inicio, fecha_finalizacion, etiquetas, formatos) "
                   "SELECT id, nombre_archivo, titulo, autor, genero, idioma, serie, estado, fecha_inicio, fecha_finalizacion, etiquetas, formatos FROM libros")

    # Eliminar la tabla original y renombrar la tabla nueva
    cursor.execute("DROP TABLE IF EXISTS libros")
    cursor.execute("ALTER TABLE libros_temp RENAME TO libros")
    
    conn.commit()
    return conn, cursor

def agregar_columna_formatos(cursor):
    # Verificar si la columna 'formatos' ya existe en la tabla
    cursor.execute("PRAGMA table_info(libros)")
    columnas = cursor.fetchall()

    # Buscar la columna 'formatos'
    columnas_existentes = [col[1] for col in columnas]
    if 'formatos' not in columnas_existentes:
        # Si no existe, agregarla
        cursor.execute("ALTER TABLE libros ADD COLUMN formatos TEXT")
        print("Columna 'formatos' añadida correctamente.")

def libro_existe(cursor, titulo, autor):
    cursor.execute("SELECT * FROM libros WHERE titulo = ? AND autor = ?", (titulo, autor))
    return cursor.fetchone()

def guardar_libros_en_db(libros, conn, cursor):
    for libro in libros:
        # Verificamos si el libro ya existe
        libro_existente = libro_existe(cursor, libro['titulo'], libro['autor'])
        
        if libro_existente:
            # Si el libro ya existe, actualizamos el formato (solo si es un formato nuevo)
            formatos_existentes = libro_existente[-1]  # Última columna 'formatos'
            formatos = formatos_existentes.split(", ") if formatos_existentes else []
            if libro['tipo'] not in formatos:
                formatos.append(libro['tipo'])  # Añadimos el nuevo formato
                # Actualizamos la columna de 'formatos'
                cursor.execute('''UPDATE libros SET formatos = ? WHERE id = ?''', 
                               (', '.join(formatos), libro_existente[0]))
        else:
            # Si el libro no existe, lo insertamos
            cursor.execute('''INSERT INTO libros (nombre_archivo, titulo, autor, genero, idioma, serie, estado, fecha_inicio, fecha_finalizacion, etiquetas, formatos)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (libro['nombre_archivo'], libro['titulo'], libro['autor'], '', libro['idioma'], '', 'No leído', '', '', '', libro['tipo']))
    conn.commit()

def mostrar_libros(cursor):
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    for libro in libros:
        print(libro)

def recorrer_libreria(ruta_libreria):
    libros = []
    for root, dirs, files in os.walk(ruta_libreria):
        for archivo in files:
            if archivo.lower().endswith(('pdf', 'epub', 'mobi')):
                ruta_archivo = os.path.join(root, archivo)
                metadatos = obtener_metadatos(ruta_archivo)
                # Extraemos información específica (título, autor, etc.)
                titulo = metadatos.get('Title', 'Desconocido')
                autor = metadatos.get('Author', 'Desconocido')
                idioma = metadatos.get('Language', 'Desconocido')
                tipo = archivo.split('.')[-1].upper()  # Obtenemos el tipo de formato (pdf, epub, mobi)
                libros.append({
                    'nombre_archivo': archivo,
                    'tipo': tipo,
                    'titulo': titulo,
                    'autor': autor,
                    'idioma': idioma
                })
    return libros

# IMPORTAR INTERFAZ GRÁFICA
from interfaz import iniciar_interfaz  # Asegúrate de que 'interfaz.py' está en el mismo directorio.

# PRINCIPAL

if __name__ == "__main__":
    # Crear la base de datos
    conn, cursor = crear_base_datos()

    # Añadir la columna 'formatos' si no existe
    agregar_columna_formatos(cursor)

    # Ruta a la carpeta de tu librería
    ruta_libreria = "../Libreria" # Modificar la ruta a la carpeta de tus libros. Consultar rutas relativas si no sabes.
    
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
