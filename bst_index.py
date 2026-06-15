import struct
from config import ARCHIVO_INDICE_ABB

class NodoABB:
    def __init__(self, id_asada, posicion_fisica):
        self.id_asada = id_asada
        self.posicion_fisica = posicion_fisica
        self.izq = None
        self.der = None

def insertar_nodo(raiz, id_asada, posicion_fisica):
    if raiz is None:
        return NodoABB(id_asada, posicion_fisica)
    if id_asada < raiz.id_asada:
        raiz.izq = insertar_nodo(raiz.izq, id_asada, posicion_fisica)
    elif id_asada > raiz.id_asada:
        raiz.der = insertar_nodo(raiz.der, id_asada, posicion_fisica)
    return raiz

def buscar_en_abb(raiz, id_asada):
    """
    Busca de forma eficiente O(log n) el ID en el árbol cargado en memoria.
    Retorna la posición física en el archivo principal.
    """
    if raiz is None or raiz.id_asada == id_asada:
        return raiz
    if id_asada < raiz.id_asada:
        return buscar_en_abb(raiz.izq, id_asada)
    return buscar_en_abb(raiz.der, id_asada)

def guardar_abb_binario(raiz, archivo_f=None):
    """
    Persiste el árbol recorriéndolo en Pre-orden y guardándolo en el archivo binario.
    Estructura del registro indexado: [id_asada (int), posicion_fisica (int)]
    """
    abrir_archivo = archivo_f is None
    if abrir_archivo:
        archivo_f = open(ARCHIVO_INDICE_ABB, "wb")
        
    if raiz is not None:
        # Empaquetar ID y Posición Física (2 enteros de 4 bytes = 'II')
        archivo_f.write(struct.pack("II", raiz.id_asada, raiz.posicion_fisica))
        guardar_abb_binario(raiz.izq, archivo_f)
        guardar_abb_binario(raiz.der, archivo_f)
        
    if abrir_archivo:
        archivo_f.close()

def cargar_abb_desde_binario():
    """
    Lee el archivo binario del índice y reconstruye el árbol en memoria.
    """
    raiz = None
    try:
        with open(ARCHIVO_INDICE_ABB, "rb") as f:
            while True:
                datos = f.read(8) # 2 enteros de 4 bytes cada uno
                if not datos:
                    break
                id_asada, posicion_fisica = struct.unpack("II", datos)
                raiz = insertar_nodo(raiz, id_asada, posicion_fisica)
    except FileNotFoundError:
        return None
    return raiz