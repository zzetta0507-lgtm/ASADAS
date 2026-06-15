import socket
import json

# Configuración de red que apunta al servidor central distribuido
SERVIDOR_IP = "127.0.0.1"
SERVIDOR_PUERTO = 5000

def ejecutar_consulta():
    print("\n=== SCRIPT DE PRUEBA: CLIENTE REMOTO TCP/IP ===")
    id_a_buscar = input("Introduce el id_Asada que deseas solicitar al servidor: ").strip()
    
    if not id_a_buscar:
        print("[CLIENTE] Error: No introdujiste ningún identificador.")
        return
        
    try:
        id_numerico = int(id_a_buscar)
    except ValueError:
        print("[CLIENTE] Error: El ID debe ser un número entero puro.")
        return

    # 1. Crear el conector del Socket de baja capa
    print(f"[CLIENTE] Intentando establecer conexión con {SERVIDOR_IP}:{SERVIDOR_PUERTO}...")
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 2. Conectarse activamente al canal abierto por el servidor de hilos
        cliente.connect((SERVIDOR_IP, SERVIDOR_PUERTO))
        print("[CLIENTE] ¡Conexión establecida con éxito!")
        
        # 3. Estructurar el paquete de datos bajo el protocolo JSON acordado
        peticion = {
            "tipo": "BUSCAR_ID",
            "id_asada": id_numerico
        }
        
        # 4. Serializar y codificar el JSON en bytes UTF-8 antes de inyectarlo a la red
        datos_bytes = json.dumps(peticion).encode('utf-8')
        print(f"[CLIENTE] Enviando paquete de datos por red: {peticion}")
        cliente.sendall(datos_bytes)
        
        # 5. Quedar a la espera (Bloqueante) de la respuesta del servidor central
        print("[CLIENTE] Esperando respuesta del servidor de base de datos...")
        respuesta_bytes = cliente.recv(4096)
        
        if not respuesta_bytes:
            print("[CLIENTE] Advertencia: El servidor cerró el canal sin enviar bytes.")
            return
            
        # 6. Decodificar la trama de bytes y parsear el JSON de respuesta
        respuesta = json.loads(respuesta_bytes.decode('utf-8'))
        estado = respuesta.get("status")
        
        print("\n==================================================")
        print("          RESPUESTA DEL SERVIDOR CENTRAL          ")
        print("==================================================")
        
        if estado == "OK":
            asada = respuesta.get("data")
            print(f" -> ID ASADA : {asada.get('id_Asada')}")
            print(f" -> Operador : {asada.get('operador')}")
            print(f" -> Ubicación: {asada.get('provincia')}, {asada.get('canton')}, {asada.get('distrito')}")
            print(f" -> Teléfono : {asada.get('telefono', 'No registrado')}")
        elif estado == "NOT_FOUND":
            print(f" -> [NOT_FOUND]: El id_Asada {id_numerico} no existe en las estructuras binarias.")
        else:
            print(f" -> Estado inesperado: {estado}")
        print("==================================================")
        
    except ConnectionRefusedError:
        print("\n[CLIENTE] ERROR CRÍTICO: Conexión rechazada.")
        print("Verifica que en la pantalla izquierda del servidor esté activo el mensaje '[SERVIDOR INICIADO]'.")
    except Exception as e:
        print(f"\n[CLIENTE] Ocurrió una anomalía inesperada: {e}")
    finally:
        # 7. Liberar el puerto local del sistema operativo de forma limpia
        cliente.close()
        print("[CLIENTE] Conexión cerrada y recursos liberados.")

if __name__ == "__main__":
    ejecutar_consulta()