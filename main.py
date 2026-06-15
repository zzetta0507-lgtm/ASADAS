import api_client
import file_manager
import bst_index
import geo_lists
import geo_visualizer
import network_server
import threading

def sincronizar_sistema():
    """
    Ejecuta la actualización incremental y regenera por completo las 
    3 estructuras binarias si se detectan cambios remotos.
    """
    print("Iniciando proceso de sincronización incremental...")
    # Lógica de verificación
    fecha_remota = api_client.verificar_modificacion_remota()
    
    # Descarga de datos abiertos de ARESEP
    datos_json = api_client.descargar_datos_asadas()
    if not datos_json:
        print("No se pudieron obtener datos nuevos.")
        return

    # 1. Regenerar Archivo Binario Principal
    print("Escribiendo archivo binario principal...")
    mapa_posiciones = file_manager.guardar_registros_secuenciales(datos_json)
    
    # 2. Regenerar Índice del Árbol Binario de Búsqueda (ABB)
    print("Construyendo y guardando índice ABB...")
    raiz = None
    for id_asada, pos in mapa_posiciones.items():
        raiz = bst_index.insertar_nodo(raiz, id_asada, pos)
    bst_index.guardar_abb_binario(raiz)
    
    # 3. Regenerar Estructura Geográfica Enlazada
    print("Construyendo jerarquía geográfica...")
    estructura_geo = geo_lists.construir_estructura_jerarquica(datos_json, mapa_posiciones)
    geo_lists.guardar_geografia_binario(estructura_geo)
    
    print("¡Sincronización y regeneración de estructuras completada con éxito!")

def menu():
    while True:
        print("\n--- SISTEMA GEOGRÁFICO DE ASADAS CR ---")
        print("1. Sincronizar / Actualizar datos del Endpoint")
        print("2. Buscar ASADA por ID (Local) y ver en Mapa")
        print("3. Iniciar Servidor de Sockets Distribuido")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            sincronizar_sistema()
        elif opcion == "2":
            id_buscar = int(input("Ingrese el id_Asada a buscar: "))
            raiz = bst_index.cargar_abb_desde_binario()
            nodo = bst_index.buscar_en_abb(raiz, id_buscar)
            if nodo:
                asada = file_manager.leer_registro_por_posicion(nodo.posicion_fisica)
                print(f"Encontrada: {asada.get('operador')} | Ubicación: {asada.get('distrito')}")
                geo_visualizer.generar_mapa_asada(asada)
            else:
                print("ASADA no registrada.")
        elif opcion == "3":
            # Iniciar el servidor de sockets en un hilo secundario para no bloquear el menú
            srv_thread = threading.Thread(target=network_server.start_server, daemon=True)
            srv_thread.start()
        elif opcion == "4":
            break

if __name__ == "__main__":
    menu()