import struct
import json
from config import ARCHIVO_PRINCIPAL

def guardar_registros_secuenciales(lista_asadas):
    """
    Guarda todos los registros JSON en un archivo binario secuencialmente.
    Cada registro se precede por un entero que indica su tamaño en bytes.
    Retorna un diccionario {id_Asada: posicion_fisica} para construir los índices.
    """
    mapa_posiciones = {}
    
    with open(ARCHIVO_PRINCIPAL, "wb") as f:
        for asada in lista_asadas:
            id_asada = asada.get("id_Asada")
            if id_asada is None:
                continue
                
            # Serializar diccionario a string/bytes UTF-8
            datos_bytes = json.dumps(asada).encode('utf-8')
            longitud = len(datos_bytes)
            
            # Obtener la posición física actual en el archivo antes de escribir
            posicion_actual = f.tell()
            
            # Escribir tamaño (entero de 4 bytes 'I') y luego los datos
            f.write(struct.pack("I", longitud))
            f.write(datos_bytes)
            
            # Mapear el ID con su posición para el ABB y las listas
            mapa_posiciones[id_asada] = posicion_actual
            
    return mapa_posiciones

def leer_registro_por_posicion(posicion):
    """
    Acceso directo: Se posiciona en el archivo principal y extrae el registro completo.
    """
    with open(ARCHIVO_PRINCIPAL, "rb") as f:
        f.seek(posicion)
        # Leer los 4 bytes de la longitud del registro
        longitud_bytes = f.read(4)
        if not longitud_bytes:
            return None
        longitud = struct.unpack("I", longitud_bytes)[0]
        # Leer el JSON completo
        datos_json = f.read(longitud).decode('utf-8')
        return json.loads(datos_json)