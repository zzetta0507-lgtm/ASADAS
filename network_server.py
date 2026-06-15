import socket
import threading
import json
import bst_index
import file_manager
from config import SERVER_HOST, SERVER_PORT

raiz_arbol_memoria = None

def atender_cliente(conn, addr):
    """Gestiona de forma concurrente el ciclo de peticiones de un terminal cliente.

    Mantiene un canal síncrono para decodificar los strings JSON entrantes, 
    realizar las consultas en disco/ABB y responder de manera segura sin 
    bloquear el servidor central.

    Args:
        conn (socket.socket): Objeto socket que representa la conexión activa.
        addr (tuple): Dirección IP y puerto de origen del terminal remoto.
    """
    print(f"[CONEXIÓN] Canal establecido con el terminal: {addr}")
    global raiz_arbol_memoria
    
    try:
        while True:
            datos_bytes = conn.recv(1024)
            if not datos_bytes:
                break
                
            datos_recibidos = datos_bytes.decode('utf-8').strip()
            if not datos_recibidos:
                continue

            try:
                solicitud = json.loads(datos_recibidos)
            except json.JSONDecodeError:
                respuesta_error = {"status": "BAD_REQUEST", "message": "El protocolo distribuido requiere JSON válido."}
                conn.sendall(json.dumps(respuesta_error).encode('utf-8'))
                continue
            
            tipo_consulta = solicitud.get("tipo")
            
            if tipo_consulta == "BUSCAR_ID":
                try:
                    id_buscar = int(solicitud.get("id_asada"))
                    nodo = bst_index.buscar_en_abb(raiz_arbol_memoria, id_buscar)
                    
                    if nodo:
                        asada_info = file_manager.leer_registro_por_posicion(nodo.posicion_fisica)
                        conn.sendall(json.dumps({"status": "OK", "data": asada_info}).encode('utf-8'))
                    else:
                        conn.sendall(json.dumps({"status": "NOT_FOUND"}).encode('utf-8'))
                except (ValueError, TypeError):
                    conn.sendall(json.dumps({"status": "INVALID_ID"}).encode('utf-8'))
            else:
                conn.sendall(json.dumps({"status": "UNKNOWN_COMMAND"}).encode('utf-8'))
                
    except Exception:
        pass
    finally:
        conn.close()
        print(f"[DESCONEXIÓN] Canal cerrado con el cliente: {addr}")

def iniciar_servidor():
    """Inicializa el socket maestro del servidor y lo pone en modo escucha.

    Carga preventivamente el índice del ABB a la memoria RAM y levanta el bucle 
    de recepción asignando hilos independientes (daemon=True) para cada petición.
    """
    global raiz_arbol_memoria
    raiz_arbol_memoria = bst_index.cargar_abb_desde_binario()
    
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((SERVER_HOST, SERVER_PORT))
    servidor.listen()
    print(f"[SERVIDOR INICIADO] Escuchando en {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        try:
            conn, addr = servidor.accept()
            hilo = threading.Thread(target=atender_cliente, args=(conn, addr), daemon=True)
            hilo.start()
        except KeyboardInterrupt:
            break
    servidor.close()