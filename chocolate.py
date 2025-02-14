import os
import re
import argparse

def filtrar_directorios(dirs):
    """
    Filtra y elimina los directorios que comienzan con un punto.

    Args:
        dirs (list): Lista de nombres de directorios.
    """
    dirs[:] = [d for d in dirs if not d.startswith('.')]

def listar_estructura_markdown(ruta, archivo_salida):
    """
    Genera la estructura del directorio en formato Markdown con listas desordenadas,
    excluyendo directorios ocultos.

    Args:
        ruta (str): Ruta de la carpeta a analizar.
        archivo_salida (str): Nombre del archivo Markdown de salida.
    """
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("# Estructura del Proyecto\n\n")
        for root, dirs, files in os.walk(ruta):
            filtrar_directorios(dirs)

            relative_path = os.path.relpath(root, ruta)
            if relative_path == '.':
                level = 0
            else:
                level = relative_path.count(os.sep) + 1
            indent = '    ' * level

            carpeta = os.path.basename(root)
            if carpeta:
                f.write(f"{indent}- **🗀  {carpeta}/**\n")

            for file in files:
                if not file.startswith('.'):
                    file_indent = '    ' * (level + 1)
                    f.write(f"{file_indent}- 🗋  {file}\n")

def extraer_docstring(file_path):
    """
    Extrae el docstring o comentarios iniciales de un archivo según su tipo,
    excluyendo archivos en directorios ocultos y archivos binarios.

    Args:
        file_path (str): Ruta completa del archivo.

    Returns:
        str: Contenido del docstring/comentario si se encuentra, de lo contrario, una cadena vacía.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    doc = ""

    # Ignorar archivos binarios
    binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.db', '.bin', '.exe']
    if ext in binary_extensions:
        return doc

    partes = file_path.split(os.sep)
    if any(part.startswith('.') for part in partes):
        return doc

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if ext == '.py':
            match = re.match(r'^\s*(?:\'\'\'|\"\"\")([\s\S]*?)(?:\'\'\'|\"\"\")', content, re.DOTALL)
            if match:
                doc = match.group(1).strip()
            else:
                comments = []
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("#"):
                        comments.append(line.lstrip("#").strip())
                    elif not line:
                        continue
                    else:
                        break
                if comments:
                    doc = "\n".join(comments)
        elif ext in ['.js', '.php', '.css']:
            # Buscar comentarios multilínea (/* ... */)
            multiline_match = re.match(r'^\s*/\*([\s\S]*?)\*/', content, re.DOTALL)
            if multiline_match:
                doc = multiline_match.group(1).strip()
            else:
                # Buscar comentarios de una línea (//)
                comments = []
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("//"):
                        comments.append(line.lstrip("//").strip())
                    elif not line:
                        continue
                    else:
                        break
                if comments:
                    doc = "\n".join(comments)
        elif ext == '.html':
            match = re.match(r'^\s*<!--([\s\S]*?)-->', content, re.DOTALL)
            if match:
                doc = match.group(1).strip()
    except Exception as e:
        print(f"Error al procesar el archivo {file_path}: {e}")

    return doc

def agregar_docstrings_markdown(ruta, archivo_salida):
    """
    Agrega docstrings/comentarios de los archivos al documento Markdown,
    excluyendo directorios ocultos y archivos binarios.

    Args:
        ruta (str): Ruta de la carpeta a analizar.
        archivo_salida (str): Nombre del archivo Markdown de salida.
    """
    with open(archivo_salida, 'a', encoding='utf-8') as f:
        f.write("\n# Documentación de Archivos\n\n")
        for root, dirs, files in os.walk(ruta):
            filtrar_directorios(dirs)

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                ext = ext.lower().lstrip('.')

                # Ignorar archivos binarios
                binary_extensions = ['png', 'jpg', 'jpeg', 'gif', 'db', 'bin', 'exe']
                if ext in binary_extensions:
                    continue

                doc = extraer_docstring(file_path)
                if doc:
                    relative_path = os.path.relpath(file_path, ruta)
                    f.write(f"## {relative_path}\n\n")
                    f.write(f"{doc}\n\n")

def procesar(carpeta, archivo_md):
    """
    Ejecuta las dos fases del procesamiento.

    Args:
        carpeta (str): Ruta de la carpeta a analizar.
        archivo_md (str): Nombre del archivo Markdown de salida.
    """
    try:
        listar_estructura_markdown(carpeta, archivo_md)
        print("Estructura del proyecto generada.")

        agregar_docstrings_markdown(carpeta, archivo_md)
        print("Docstrings/comentarios agregados.")

        print(f"Proceso completado. Archivo generado: {archivo_md}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generador de Estructura Markdown")
    parser.add_argument("carpeta", help="Ruta de la carpeta a analizar")
    parser.add_argument("archivo_md", help="Nombre del archivo Markdown de salida")
    args = parser.parse_args()

    procesar(args.carpeta, args.archivo_md)

if __name__ == "__main__":
    main()