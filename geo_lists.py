import json
from config import ARCHIVO_GEOGRAFICO

# Representación lógica de los nodos jerárquicos
class NodoSimple:
    def __init__(self, nombre):
        self.nombre = nombre
        self.siguiente = None
        self.sublista = None  # Apunta al siguiente nivel jerárquico

def construir_estructura_jerarquica(lista_asadas, mapa_posiciones):
    """
    Construye en memoria la estructura de listas enlazadas dinámicas:
    Provincia -> Cantón -> Distrito -> [Lista de IDs de ASADAS y posiciones]
    """
    estructura_provincias = {}

    for asada in lista_asadas:
        prov = asada.get("provincia")
        cant = asada.get("canton")
        dist = asada.get("distrito")
        id_asada = asada.get("id_Asada")
        pos_fisica = mapa_posiciones.get(id_asada)

        if not all([prov, cant, dist, id_asada]):
            continue

        if prov not in estructura_provincias:
            estructura_provincias[prov] = {}
        if cant not in estructura_provincias[prov]:
            estructura_provincias[prov][cant] = {}
        if dist not in estructura_provincias[prov][cant]:
            estructura_provincias[prov][cant][dist] = []

        # Agregar info de la ASADA (ID y Posición Física)
        estructura_provincias[prov][cant][dist].append({
            "id_asada": id_asada,
            "posicion_fisica": pos_fisica
        })
        
    # Ordenar las ASADAS por ID dentro de cada distrito tal como solicita la rúbrica
    for prov in estructura_provincias:
        for cant in estructura_provincias[prov]:
            for dist in estructura_provincias[prov][cant]:
                estructura_provincias[prov][cant][dist].sort(key=lambda x: x["id_asada"])

    return estructura_provincias

def guardar_geografia_binario(estructura):
    """
    Guarda de manera estructurada las listas en formato JSON comprimido a binario.
    """
    with open(ARCHIVO_GEOGRAFICO, "wb") as f:
        datos_bytes = json.dumps(estructura).encode('utf-8')
        f.write(datos_bytes)

def cargar_geografia_desde_binario():
    try:
        with open(ARCHIVO_GEOGRAFICO, "rb") as f:
            return json.loads(f.read().decode('utf-8'))
    except FileNotFoundError:
        return {}