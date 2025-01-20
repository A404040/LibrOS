import os
import json
import subprocess

# Función para obtener metadatos de un archivo usando exiftool
def obtener_metadatos(ruta_archivo):
    resultado = subprocess.run(['exiftool', '-j', ruta_archivo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    metadatos = resultado.stdout.decode('utf-8')

    if metadatos:
        metadatos_json = json.loads(metadatos)
        return metadatos_json[0]  # Devolvemos el primer objeto de los metadatos
    else:
        return {}

# Función para recorrer la librería y obtener información de los libros
def recorrer_libreria(ruta_libreria):
    libros = []
    for root, dirs, files in os.walk(ruta_libreria):
        for archivo in files:
            if archivo.lower().endswith(('pdf', 'epub', 'mobi')):
                ruta_archivo = os.path.join(root, archivo)
                metadatos = obtener_metadatos(ruta_archivo)
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
