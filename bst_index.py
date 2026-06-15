import struct
from config import ARCHIVO_INDICE_ABB

class NodoABB:
    def __init__(self, id_asada, posicion_fisica):
        self.id_asada = id_asada
        self.posicion_fisica = posicion_fisica
        self.izq = None
        self.der = None

def insertar_nodo_iterativo(raiz, id_asada, posicion_fisica):
    """
    Inserta un nodo en el árbol binario de manera puramente iterativa usando ciclos.
    Previene el colapso de la pila de llamadas de Python.
    """
    nuevo_nodo = NodoABB(id_asada, posicion_fisica)
    if raiz is None:
        return nuevo_nodo
    
    actual = raiz
    while True:
        if id_asada < actual.id_asada:
            if actual.izq is None:
                actual.izq = nuevo_nodo
                break
            actual = actual.izq
        elif id_asada > actual.id_asada:
            if actual.der is None:
                actual.der = nuevo_nodo
                break
            actual = actual.der
        else:
            break  # Elemento duplicado omitido
    return raiz

def buscar_en_abb(raiz, id_asada):
    """
    Busca de manera óptima O(log n) utilizando un ciclo repetitivo directo.
    """
    actual = raiz
    while actual is not None:
        if id_asada == actual.id_asada:
            return actual
        elif id_asada < actual.id_asada:
            actual = actual.izq
        else:
            actual = actual.der
    return None

def guardar_abb_binario(raiz):
    """
    Guarda el árbol en el archivo binario del índice recorriéndolo en Pre-orden
    mediante una pila secuencial en memoria RAM, evitando la recursión.
    """
    if raiz is None:
        return

    with open(ARCHIVO_INDICE_ABB, "wb") as f:
        pila = [raiz]
        while len(pila) > 0:
            nodo_actual = pila.pop()
            
            # Empaquetado binario de dos enteros nativos (8 bytes totales -> 'II')
            f.write(struct.pack("II", nodo_actual.id_asada, nodo_actual.posicion_fisica))
            
            if nodo_actual.der is not None:
                pila.append(nodo_actual.der)
            if nodo_actual.izq is not None:
                pila.append(nodo_actual.izq)

def cargar_abb_desde_binario():
    """
    Reconstruye el Árbol Binario de Búsqueda iterativamente leyendo el archivo de índice.
    """
    raiz = None
    try:
        with open(ARCHIVO_INDICE_ABB, "rb") as f:
            while True:
                datos = f.read(8)
                if not datos:
                    break
                id_asada, posicion_fisica = struct.unpack("II", datos)
                raiz = insertar_nodo_iterativo(raiz, id_asada, posicion_fisica)
    except FileNotFoundError:
        return None
    return raiz