import api_client
import file_manager
import bst_index
import geo_lists
import geo_visualizer
import network_server
import threading

def sincronizar_sistema():
    """
    Consulta los datos remotos de ARESEP y regenera las tres estructuras binarias.
    """
    print("Iniciando proceso de sincronización incremental...")
    
    datos_json = api_client.descargar_datos_asadas()
    if not datos_json:
        print("No se pudieron obtener registros válidos del endpoint.")
        return

    # 1. Archivo Binario Principal
    print("Escribiendo archivo binario principal...")
    mapa_posiciones = file_manager.guardar_registros_secuenciales(datos_json)
    
    # 2. Índice ABB Iterativo
    print("Construyendo y guardando índice ABB...")
    raiz = None
    for id_asada, pos in mapa_posiciones.items():
        raiz = bst_index.insertar_nodo_iterativo(raiz, id_asada, pos)
    bst_index.guardar_abb_binario(raiz)
    
    # 3. Estructura Geográfica Enlazada
    print("Construyendo jerarquía geográfica...")
    estructura_geo = geo_lists.construir_estructura_jerarquica(datos_json, mapa_posiciones)
    geo_lists.guardar_geografia_binario(estructura_geo)
    print("¡Estructuras binarias actualizadas con éxito!")

def menu():
    while True:
        print("\n--- SISTEMA GEOGRÁFICO DE ASADAS CR ---")
        print("1. Sincronizar / Actualizar datos del Endpoint")
        print("2. Buscar ASADA por ID (Local) y ver en Mapa")
        print("3. Iniciar Servidor de Sockets Distribuido")
        print("4. Consultar ASADAS por División Política (Jerárquico)")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            sincronizar_sistema()
            
        elif opcion == "2":
            try:
                id_buscar = int(input("Ingrese el id_Asada a buscar: "))
                raiz = bst_index.cargar_abb_desde_binario()
                nodo = bst_index.buscar_en_abb(raiz, id_buscar)
                if nodo:
                    asada = file_manager.leer_registro_por_posicion(nodo.posicion_fisica)
                    print(f"Encontrada: {asada.get('operador')} | Ubicación: {asada.get('distrito')}")
                    geo_visualizer.generar_mapa_asada(asada)
                else:
                    print("La ASADA consultada no se encuentra registrada localmente.")
            except ValueError:
                print("Por favor, introduzca un identificador numérico válido.")
                
        elif opcion == "3":
            srv_thread = threading.Thread(target=network_server.iniciar_servidor, daemon=True)
            srv_thread.start()
            
        elif opcion == "4":
            # CARGAR LA ESTRUCTURA DESDE EL ARCHIVO BINARIO GEOGRÁFICO
            estructura_geo = geo_lists.cargar_geografia_desde_binario()
            if not estructura_geo:
                print("No hay datos geográficos locales. Sincronice el sistema primero (Opción 1).")
                continue
            
            try:
                # ---- COMBO 1: PROVINCIAS ----
                provincias = sorted(list(estructura_geo.keys()))
                print("\n=== SELECCIONE UNA PROVINCIA ===")
                for idx, prov in enumerate(provincias, 1):
                    print(f"  {idx}. {prov}")
                
                sel_p = int(input("Seleccione el número de Provincia: ")) - 1
                if sel_p < 0 or sel_p >= len(provincias):
                    print("Selección fuera de rango.")
                    continue
                provincia_sel = provincias[sel_p]
                
                # ---- COMBO 2: CANTONES (Filtrado por la Provincia seleccionada) ----
                cantones = sorted(list(estructura_geo[provincia_sel].keys()))
                print(f"\n=== CANTONES DE {provincia_sel} ===")
                for idx, cant in enumerate(cantones, 1):
                    print(f"  {idx}. {cant}")
                    
                sel_c = int(input("Seleccione el número de Cantón: ")) - 1
                if sel_c < 0 or sel_c >= len(cantones):
                    print("Selección fuera de rango.")
                    continue
                canton_sel = cantones[sel_c]
                
                # ---- COMBO 3: DISTRITOS (Filtrado por el Cantón seleccionado) ----
                distritos = sorted(list(estructura_geo[provincia_sel][canton_sel].keys()))
                print(f"\n=== DISTRITOS DE {canton_sel} ===")
                for idx, dist in enumerate(distritos, 1):
                    print(f"  {idx}. {dist}")
                    
                sel_d = int(input("Seleccione el número de Distrito: ")) - 1
                if sel_d < 0 or sel_d >= len(distritos):
                    print("Selección fuera de rango.")
                    continue
                distrito_sel = distritos[sel_d]
                
                # ---- DESPLIEGUE FINAL DE ASADAS DEL DISTRITO ----
                lista_asadas = estructura_geo[provincia_sel][canton_sel][distrito_sel]
                print(f"\n==================================================")
                print(f" ASADAS EN DISTRITO: {distrito_sel} ({len(lista_asadas)} encontradas)")
                print(f"==================================================")
                
                for item in lista_asadas:
                    # Uso obligatorio de direccionamiento directo en bytes para extraer detalles extendidos
                    detalles = file_manager.leer_registro_por_posicion(item["posicion_fisica"])
                    if detalles:
                        print(f" -> [ID: {item['id_asada']}] {detalles.get('operador')}")
                        print(f"    Contacto: {detalles.get('telefono', 'N/A')} | Correo: {detalles.get('correo', 'N/A')}\n")
                print(f"==================================================")
                
            except (ValueError, IndexError):
                print("\n[ERROR] Entrada inválida. Debe digitar únicamente el número de la opción.")
                
        elif opcion == "5":
            print("Cerrando el sistema central. Hasta luego.")
            break

if __name__ == "__main__":
    menu()