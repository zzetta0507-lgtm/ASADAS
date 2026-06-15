# ==============================================================================
# CONFIGURACIÓN GENERAL DEL SISTEMA CENTRAL
# ==============================================================================

# Endpoint oficial de datos abiertos provisto por ARESEP
URL_ENDPOINT = "https://datos.aresep.go.cr/ws.datosabiertos/Services/IA/Asadas.svc/ObtenerInformacionUbicacionAsadas"

# Definición de los 3 archivos binarios exigidos por el diseño físico
ARCHIVO_PRINCIPAL = "asadas_principal.bin"
ARCHIVO_INDICE_ABB = "asadas_indice_abb.bin"
ARCHIVO_GEOGRAFICO = "asadas_geografico.bin"

# Parámetros para la red distribuida por Sockets TCP/IP
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000