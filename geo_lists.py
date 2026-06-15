import json
from config import ARCHIVO_GEOGRAFICO

def construir_estructura_jerarquica(lista_asadas, mapa_posiciones):
    """Agrupa las ASADAS en un mapa multinivel que emula listas enlazadas jerárquicas.

    Organiza la división político-administrativa bajo la estructura 
    Provincia -> Cantón -> Distrito. Ordena internamente las listas finales de 
    ASADAS de menor a mayor según sus identificadores numéricos.

    Args:
        lista_asadas (list): Colección de diccionarios con los datos originales.
        mapa_posiciones (dict): Diccionario de punteros físicos {ID: Posición}.

    Returns:
        dict: Estructura jerárquica multinivel con las relaciones geográficas.
    """
    estructura = {}

    for asada in lista_asadas:
        prov = asada.get("provincia")
        cant = asada.get("canton")
        dist = asada.get("distrito")
        id_asada_raw = asada.get("id_Asada")
        
        if not all([prov, cant, dist, id_asada_raw]):
            continue
            
        try:
            id_asada = int(id_asada_raw)
        except (ValueError, TypeError):
            continue
            
        pos_fisica = mapa_posiciones.get(id_asada)
        if pos_fisica is None:
            continue

        if prov not in estructura:
            estructura[prov] = {}
        if cant not in estructura[prov]:
            estructura[prov][cant] = {}
        if dist not in estructura[prov][cant]:
            estructura[prov][cant][dist] = []

        estructura[prov][cant][dist].append({
            "id_asada": id_asada,
            "posicion_fisica": pos_fisica
        })
        
    for prov in estructura:
        for cant in estructura[prov]:
            for dist in estructura[prov][cant]:
                estructura[prov][cant][dist].sort(key=lambda x: x["id_asada"])

    return estructura

def guardar_geografia_binario(estructura):
    """Persiste el mapa de la estructura jerárquica en el archivo binario geográfico.

    Args:
        estructura (dict): Mapa jerárquico multinivel generado en memoria.
    """
    with open(ARCHIVO_GEOGRAFICO, "wb") as f:
        datos_bytes = json.dumps(estructura).encode('utf-8')
        f.write(datos_bytes)

def cargar_geografia_desde_binario():
    """Lee y deserializa el archivo binario geográfico para su despliegue jerárquico.

    Returns:
        dict: Estructura jerárquica multinivel recuperada, o un mapa vacío si no existe.
    """
    try:
        with open(ARCHIVO_GEOGRAFICO, "rb") as f:
            return json.loads(f.read().decode('utf-8'))
    except FileNotFoundError:
        return {}