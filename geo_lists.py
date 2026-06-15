import json
from config import ARCHIVO_GEOGRAFICO

def construir_estructura_jerarquica(lista_asadas, mapa_posiciones):
    """
    Genera dinámicamente en memoria la estructura de listas:
    Provincia -> Cantón -> Distrito -> Array de ASADAS [ID, Posición Física].
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
        
    # CORRECCIÓN DE RÚBRICA: Ordenamiento estricto de menor a mayor por ID por distrito
    for prov in estructura:
        for cant in estructura[prov]:
            for dist in estructura[prov][cant]:
                estructura[prov][cant][dist].sort(key=lambda x: x["id_asada"])

    return estructura

def guardar_geografia_binario(estructura):
    """
    Persiste la estructura jerárquica en el archivo binario correspondiente.
    """
    with open(ARCHIVO_GEOGRAFICO, "wb") as f:
        datos_bytes = json.dumps(estructura).encode('utf-8')
        f.write(datos_bytes)

def cargar_geografia_desde_binario():
    """
    Lee el archivo binario geográfico y lo deserializa para la navegación por menús.
    """
    try:
        with open(ARCHIVO_GEOGRAFICO, "rb") as f:
            return json.loads(f.read().decode('utf-8'))
    except FileNotFoundError:
        return {}