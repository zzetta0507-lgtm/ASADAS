import struct
from config import ARCHIVO_INDICE_ABB

class NodoABB:
    """Representa un nodo individual dentro del Árbol Binario de Búsqueda."""

    def __init__(self, id_asada, posicion_fisica):
        """Inicializa las propiedades clave y punteros del nodo.

        Args:
            id_asada (int): Identificador numérico único de la ASADA (llave).
            posicion_fisica (int): Dirección de bytes en el archivo binario secuencial.
        """
        self.id_asada = id_asada
        self.posicion_fisica = posicion_fisica
        self.izq = None
        self.der = None

def insertar_nodo_iterativo(raiz, id_asada, posicion_fisica):
    """Inserta una nueva llave en el árbol binario utilizando un ciclo iterativo.

    Evita el crecimiento de la pila de llamadas de Python, anulando el riesgo 
    de sufrir un desbordamiento de memoria por recursión masiva.

    Args:
        raiz (NodoABB): Nodo raíz actual del árbol.
        id_asada (int): Identificador de la ASADA a insertar.
        posicion_fisica (int): Dirección física en bytes de la ASADA.

    Returns:
        NodoABB: La raíz del árbol modificado.
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
            break  
    return raiz

def buscar_en_abb(raiz, id_asada):
    """Busca una ASADA en el árbol con un rendimiento logarítmico O(log n).

    Navega de forma puramente iterativa a través de los punteros izquierdo o 
    derecho comparando el identificador numérico.

    Args:
        raiz (NodoABB): Nodo raíz del árbol donde se realizará la consulta.
        id_asada (int): Identificador numérico a buscar.

    Returns:
        NodoABB: El objeto nodo coincidente si se encuentra, de lo contrario None.
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
    """Serializa el ABB completo en el archivo binario de índice.

    Recorre el árbol en Pre-orden utilizando una estructura de pila (stack) 
    manual en RAM, empaquetando cada nodo en bloques fijos de 8 bytes (dos enteros).

    Args:
        raiz (NodoABB): Nodo raíz del árbol a persistir.
    """
    if raiz is None:
        return

    with open(ARCHIVO_INDICE_ABB, "wb") as f:
        pila = [raiz]
        while len(pila) > 0:
            nodo_actual = pila.pop()
            
            f.write(struct.pack("II", nodo_actual.id_asada, nodo_actual.posicion_fisica))
            
            if nodo_actual.der is not None:
                pila.append(nodo_actual.der)
            if nodo_actual.izq is not None:
                pila.append(nodo_actual.izq)

def cargar_abb_desde_binario():
    """Reconstruye el Árbol Binario de Búsqueda leyendo el archivo binario de índice.

    Lee iterativamente los bloques de 8 bytes hasta el final del archivo, 
    reinsertando cada registro para levantar el árbol en memoria RAM.

    Returns:
        NodoABB: La raíz del árbol binario de búsqueda reconstruido, o None si no existe.
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