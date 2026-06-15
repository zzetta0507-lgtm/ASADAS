import os
import threading
import api_client
import file_manager
import bst_index
import geo_lists
import geo_visualizer
import network_server

# ==============================================================================
# PALETA DE COLORES ANSI & COMPONENTES ASCII
# ==============================================================================
CLR_RESET  = "\033[0m"
CLR_NEON   = "\033[38;5;51m"   # Ciano brillante
CLR_VERDE  = "\033[38;5;82m"   # Verde éxito
CLR_AZUL   = "\033[38;5;27m"   # Azul corporativo
CLR_ROJO   = "\033[38;5;196m"  # Rojo alerta
CLR_GRIS   = "\033[38;5;244m"  # Gris tenue

BANNER_ASCII = f"""{CLR_NEON}
  _____ _     _   _ _____ ___  ____   ____ ____  
 / ___/| |   | | | | ___ / _ \|  _ \ / ___|  _ \ 
| |    | |   | | | | ___| |_| | |_) | |   | |_) |
| |___ | |___| |_| | |__|  _  |  __/| |___|  _ < 
 \____\|_____|\___/|____|_| |_|_|    \____|_| \_\\
{CLR_GRIS}==================================================
 [ SISTEMA GEOGRÁFICO DE ASADAS DE COSTA RICA ]
=================================================={CLR_RESET}"""

SEP_LINE = f"{CLR_GRIS}--------------------------------------------------{CLR_RESET}"

def limpiar_pantalla():
    """Limpia la consola según el sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')

def sincronizar_sistema():
    """Consulta los datos remotos de ARESEP y regenera las tres estructuras."""
    print(f"\n{CLR_NEON}[*]{CLR_RESET} Iniciando proceso de sincronización incremental...")
    
    datos_json = api_client.descargar_datos_asadas()
    if not datos_json:
        print(f"\n{CLR_ROJO}[X] Error:{CLR_RESET} No se pudieron obtener registros válidos.")
        input(f"\n{CLR_GRIS}Presione [Enter] para continuar...{CLR_RESET}")
        return

    print(f" {CLR_AZUL}>>{CLR_RESET} Escribiendo archivo binario principal...")
    mapa_posiciones = file_manager.guardar_registros_secuenciales(datos_json)
    
    print(f" {CLR_AZUL}>>{CLR_RESET} Construyendo y guardando índice ABB...")
    raiz = None
    for id_asada, pos in mapa_posiciones.items():
        raiz = bst_index.insertar_nodo_iterativo(raiz, id_asada, pos)
    bst_index.guardar_abb_binario(raiz)
    
    print(f" {CLR_AZUL}>>{CLR_RESET} Construyendo jerarquía geográfica...")
    estructura_geo = geo_lists.construir_estructura_jerarquica(datos_json, mapa_posiciones)
    geo_lists.guardar_geografia_binario(estructura_geo)
    
    print(f"\n{CLR_VERDE}[+]{CLR_RESET} ¡Estructuras binarias actualizadas con éxito!")
    input(f"\n{CLR_GRIS}Presione [Enter] para regresar al menú principal...{CLR_RESET}")

def menu():
    while True:
        limpiar_pantalla()
        print(BANNER_ASCII)
        print(f" {CLR_NEON}[1]{CLR_RESET} Sincronizar / Actualizar datos del Endpoint")
        print(f" {CLR_NEON}[2]{CLR_RESET} Buscar ASADA por ID (Local) y ver en Mapa")
        print(f" {CLR_NEON}[3]{CLR_RESET} Iniciar Servidor de Sockets Distribuidor")
        print(f" {CLR_NEON}[4]{CLR_RESET} Consultar ASADAS por División Política")
        print(f" {CLR_NEON}[5]{CLR_RESET} Salir")
        print(SEP_LINE)
        opcion = input(f"{CLR_NEON}Seleccione una opción >> {CLR_RESET}").strip()
        
        if opcion == "1":
            limpiar_pantalla()
            print(BANNER_ASCII)
            sincronizar_sistema()
            
        elif opcion == "2":
            limpiar_pantalla()
            print(BANNER_ASCII)
            print(f"{CLR_NEON}=== BÚSQUEDA LOCAL POR IDENTIFICADOR ==={CLR_RESET}\n")
            try:
                id_buscar = int(input(f"{CLR_AZUL}Ingrese el id_Asada a buscar >> {CLR_RESET}"))
                raiz = bst_index.cargar_abb_desde_binario()
                nodo = bst_index.buscar_en_abb(raiz, id_buscar)
                if nodo:
                    asada = file_manager.leer_registro_por_posicion(nodo.posicion_fisica)
                    print(SEP_LINE)
                    print(f"{CLR_VERDE}[+] ASADA ENCONTRADA:{CLR_RESET} {asada.get('operador')}")
                    print(f"{CLR_GRIS}    Ubicación:{CLR_RESET} {asada.get('distrito')}")
                    print(SEP_LINE)
                    geo_visualizer.generar_mapa_asada(asada)
                else:
                    print(f"\n{CLR_ROJO}[!] La ASADA consultada no existe localmente.{CLR_RESET}")
            except ValueError:
                print(f"\n{CLR_ROJO}[X] Error: Por favor introduzca un número entero.{CLR_RESET}")
            input(f"\n{CLR_GRIS}Presione [Enter] para regresar...{CLR_RESET}")
                
        elif opcion == "3":
            print(f"\n{CLR_NEON}[*]{CLR_RESET} Desplegando hilos de red en segundo plano...")
            srv_thread = threading.Thread(target=network_server.iniciar_servidor, daemon=True)
            srv_thread.start()
            input(f"\n{CLR_VERDE}[+]{CLR_RESET} Servidor activo. Presione [Enter] para continuar...")
            
        elif opcion == "4":
            estructura_geo = geo_lists.cargar_geografia_desde_binario()
            if not estructura_geo:
                print(f"\n{CLR_ROJO}[!] No hay datos locales. Sincronice el sistema primero.{CLR_RESET}")
                input(f"\n{CLR_GRIS}Presione [Enter] para continuar...{CLR_RESET}")
                continue
            
            try:
                # ---- COMBO 1: PROVINCIAS ----
                limpiar_pantalla()
                print(BANNER_ASCII)
                provincias = sorted(list(estructura_geo.keys()))
                print(f"{CLR_NEON}=== SELECCIONE UNA PROVINCIA ==={CLR_RESET}")
                for idx, prov in enumerate(provincias, 1):
                    print(f"  {CLR_AZUL}[{idx}]{CLR_RESET} {prov}")
                
                sel_p = int(input(f"\n{CLR_NEON}Número de Provincia >> {CLR_RESET}")) - 1
                if sel_p < 0 or sel_p >= len(provincias):
                    raise IndexError
                provincia_sel = provincias[sel_p]
                
                # ---- COMBO 2: CANTONES ----
                limpiar_pantalla()
                print(BANNER_ASCII)
                cantones = sorted(list(estructura_geo[provincia_sel].keys()))
                print(f"{CLR_NEON}=== CANTONES DE {provincia_sel} ==={CLR_RESET}")
                for idx, cant in enumerate(cantones, 1):
                    print(f"  {CLR_AZUL}[{idx}]{CLR_RESET} {cant}")
                    
                sel_c = int(input(f"\n{CLR_NEON}Número de Cantón >> {CLR_RESET}")) - 1
                if sel_c < 0 or sel_c >= len(cantones):
                    raise IndexError
                canton_sel = cantones[sel_c]
                
                # ---- COMBO 3: DISTRITOS ----
                limpiar_pantalla()
                print(BANNER_ASCII)
                distritos = sorted(list(estructura_geo[provincia_sel][canton_sel].keys()))
                print(f"{CLR_NEON}=== DISTRITOS DE {canton_sel} ==={CLR_RESET}")
                for idx, dist in enumerate(distritos, 1):
                    print(f"  {CLR_AZUL}[{idx}]{CLR_RESET} {dist}")
                    
                sel_d = int(input(f"\n{CLR_NEON}Número de Distrito >> {CLR_RESET}")) - 1
                if sel_d < 0 or sel_d >= len(distritos):
                    raise IndexError
                distrito_sel = distritos[sel_d]
                
                # ---- DESPLIEGUE FINAL ----
                limpiar_pantalla()
                print(BANNER_ASCII)
                lista_asadas = estructura_geo[provincia_sel][canton_sel][distrito_sel]
                print(f"{CLR_VERDE}=== ASADAS EN DISTRITO: {distrito_sel} ({len(lista_asadas)}) ==={CLR_RESET}")
                
                for item in lista_asadas:
                    detalles = file_manager.leer_registro_por_posicion(item["posicion_fisica"])
                    if detalles:
                        print(f" {CLR_NEON}-->{CLR_RESET} {CLR_VERDE}[ID: {item['id_asada']}]{CLR_RESET} {detalles.get('operador')}")
                        print(f"     {CLR_GRIS}Tel:{CLR_RESET} {detalles.get('telefono', 'N/A')} | {CLR_GRIS}Email:{CLR_RESET} {detalles.get('correo', 'N/A')}\n")
                print(SEP_LINE)
                input(f"\n{CLR_GRIS}Presione [Enter] para regresar al menú principal...{CLR_RESET}")
                
            except (ValueError, IndexError):
                print(f"\n{CLR_ROJO}[X] Error: Selección inválida o fuera de rango.{CLR_RESET}")
                input(f"\n{CLR_GRIS}Presione [Enter] para continuar...{CLR_RESET}")
                
        elif opcion == "5":
            print(f"\n{CLR_AZUL}[INFO] Cerrando el sistema central. Hasta luego.{CLR_RESET}\n")
            break

if __name__ == "__main__":
    menu()