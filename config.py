# ==============================================================================
# CONFIGURACIÓN GENERAL DEL SISTEMA CENTRAL
# ==============================================================================

"""Módulo de configuración centralizada para el sistema de ASADAS.

Define los endpoints remotos, las rutas de los archivos binarios y los
parámetros de red para la comunicación distribuida mediante sockets.
"""

URL_ENDPOINT = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IA/Asadas.svc/ObtenerInformacionUbicacionAsadas"

ARCHIVO_PRINCIPAL = "asadas_principal.bin"
ARCHIVO_INDICE_ABB = "asadas_indice_abb.bin"
ARCHIVO_GEOGRAFICO = "asadas_geografico.bin"

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000