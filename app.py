from flask import Flask, request, send_file, jsonify
import os
import shutil
from chocolate import procesar

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

# Crear las carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/test')
def test():
    return 'ok'

@app.route('/upload', methods=['POST'])
def upload():
    if 'folder' not in request.files:
        return jsonify({"error": "No se ha subido ninguna carpeta."}), 400

    # Obtener la lista de archivos subidos
    files = request.files.getlist('folder')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No se ha seleccionado ningún archivo."}), 400

    # Crear una carpeta temporal para los archivos subidos
    temp_folder = os.path.join(UPLOAD_FOLDER, 'temp')
    os.makedirs(temp_folder, exist_ok=True)

    # Guardar los archivos subidos manteniendo la estructura de directorios
    for file in files:
        # Obtener la ruta relativa del archivo dentro de la carpeta
        file_path = os.path.join(temp_folder, file.filename)
        
        # Crear directorios necesarios
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar el archivo
        file.save(file_path)
        print(f"Archivo guardado: {file_path}")  # Depuración

    # Procesar los archivos subidos
    output_md = os.path.join(OUTPUT_FOLDER, 'output.md')
    try:
        procesar(temp_folder, output_md)
    except FileNotFoundError as e:
        return jsonify({"error": f"No se encontró el archivo {e.filename}."}), 400
    except Exception as e:
        return jsonify({"error": f"Error al procesar la carpeta: {e}"}), 500
    finally:
        # Limpiar la carpeta de uploads después de procesar
        clean_upload_folder(UPLOAD_FOLDER)

    # Enviar el archivo generado para descargar
    return send_file(output_md, as_attachment=True)

def clean_upload_folder(folder_path):
    """
    Elimina todos los archivos y subdirectorios dentro de la carpeta especificada.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Eliminar archivos o enlaces simbólicos
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Eliminar directorios y su contenido
            print(f"Eliminado: {file_path}")  # Depuración
        except Exception as e:
            print(f"Error al eliminar {file_path}: {e}")  # Depuración

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)