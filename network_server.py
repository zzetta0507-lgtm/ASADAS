import socket
import threading
import json
import bst_index
import file_manager
from config import SERVER_HOST, SERVER_PORT

# Variable global en memoria del servidor
raiz_arbol_memoria = None

def atender_cliente(conn, addr):
    """
    Hilo independiente para procesar las consultas de un cliente remoto de manera concurrente.
    """
    print(f"[CONEXIÓN] Cliente conectado desde {addr}")
    global raiz_arbol_memoria
    
    try:
        while True:
            datos_recibidos = conn.recv(1024).decode('utf-8')
            if not datos_recibidos:
                break
                
            solicitud = json.loads(datos_recibidos)
            tipo_consulta = solicitud.get("tipo")
            
            if tipo_consulta == "BUSCAR_ID":
                id_buscar = int(solicitud.get("id_asada"))
                # Buscar eficientemente en el ABB cargado en memoria
                nodo = bst_index.buscar_en_abb(raiz_arbol_memoria, id_buscar)
                
                if nodo:
                    # Recuperar datos directo desde el archivo secuencial binario
                    asada_info = file_manager.leer_registro_por_posicion(nodo.posicion_fisica)
                    conn.sendall(json.dumps({"status": "OK", "data": asada_info}).encode('utf-8'))
                else:
                    conn.sendall(json.dumps({"status": "NOT_FOUND"}).encode('utf-8'))
                    
            else:
                conn.sendall(json.dumps({"status": "UNKNOWN_COMMAND"}).encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Con el cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONEXIÓN] Conexión cerrada con {addr}")

def iniciar_servidor():
    global raiz_arbol_memoria
    # Cargar el árbol binario indexado a la memoria antes de aceptar conexiones
    raiz_arbol_memoria = bst_index.cargar_abb_desde_binario()
    
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((SERVER_HOST, SERVER_PORT))
    servidor.listen()
    print(f"[SERVIDOR INICIADO] Escuchando en {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        conn, addr = servidor.accept()
        # Creación del hilo independiente para el cliente concurrente
        hilo = threading.Thread(target=atender_cliente, args=(conn, addr))
        hilo.start()