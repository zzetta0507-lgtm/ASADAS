import struct
import json
from config import ARCHIVO_PRINCIPAL

def guardar_registros_secuenciales(lista_asadas):
    """
    Escribe los registros completos en el archivo binario principal de forma secuencial.
    Antepone un entero de 4 bytes indicando la longitud del bloque de datos.
    Retorna un mapa {id_asada: posicion_fisica} de enteros.
    """
    mapa_posiciones = {}
    
    if not lista_asadas or not isinstance(lista_asadas, list):
        print("Error: La colección de ASADAS es inválida o nula.")
        return mapa_posiciones

    with open(ARCHIVO_PRINCIPAL, "wb") as f:
        for asada in lista_asadas:
            if not isinstance(asada, dict):
                continue
                
            id_asada_raw = asada.get("id_Asada")
            if id_asada_raw is None:
                continue
            
            try:
                # Normalización restrictiva a tipo entero del identificador
                id_asada = int(id_asada_raw)
            except (ValueError, TypeError):
                continue
                
            datos_bytes = json.dumps(asada).encode('utf-8')
            longitud = len(datos_bytes)
            
            # Captura de la posición física del puntero en el archivo (Direccionamiento directo)
            posicion_actual = f.tell()
            
            # Serialización binaria: Longitud (4 bytes 'I') + Datos UTF-8
            f.write(struct.pack("I", longitud))
            f.write(datos_bytes)
            
            mapa_posiciones[id_asada] = posicion_actual
            
    return mapa_posiciones

def leer_registro_por_posicion(posicion):
    """
    Realiza acceso directo posicionándose en los bytes exactos indicados
    y extrae el objeto JSON original.
    """
    try:
        with open(ARCHIVO_PRINCIPAL, "rb") as f:
            f.seek(posicion)
            longitud_bytes = f.read(4)
            if not longitud_bytes:
                return None
            longitud = struct.unpack("I", longitud_bytes)[0]
            datos_json = f.read(longitud).decode('utf-8')
            return json.loads(datos_json)
    except Exception as e:
        print(f"Error de acceso directo en el archivo principal: {e}")
        return None