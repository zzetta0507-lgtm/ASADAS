import urllib.request
import json
from config import URL_ENDPOINT

def descargar_datos_asadas():
    """
    Se conecta al endpoint de ARESEP, descarga el contenido y fuerza
    el desempaquetado en cascada hasta extraer la lista de registros puros.
    """
    try:
        print("Conectando al endpoint de ARESEP...")
        req = urllib.request.Request(
            URL_ENDPOINT, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                datos_raw = response.read().decode('utf-8')
                objeto_actual = json.loads(datos_raw)
                
                # Bucle adaptativo de desempaquetado profundo (Deep Unwrapping)
                while isinstance(objeto_actual, str) or isinstance(objeto_actual, dict):
                    if isinstance(objeto_actual, str):
                        objeto_actual = json.loads(objeto_actual)
                    elif isinstance(objeto_actual, dict):
                        llaves = list(objeto_actual.keys())
                        
                        # Caso A: Envoltorio estándar de Web Service (WCF)
                        if len(llaves) == 1 and ("Result" in llaves[0] or "Obtener" in llaves[0]):
                            objeto_actual = objeto_actual[llaves[0]]
                        
                        # Caso B: Buscar dinámicamente si el objeto contiene el array de datos
                        else:
                            encontrado = False
                            for k in llaves:
                                if isinstance(objeto_actual[k], list):
                                    objeto_actual = objeto_actual[k]
                                    encontrado = True
                                    break
                            
                            if not encontrado:
                                break

                if isinstance(objeto_actual, list):
                    print(f"Descarga exitosa. Se detectaron {len(objeto_actual)} registros de ASADAS.")
                    return objeto_actual
                else:
                    print(f"Estructura inesperada tras el parseo: {type(objeto_actual)}")
                    return []
            else:
                print(f"Error al conectar con el API. Código de estado: {response.status}")
                return None
    except Exception as e:
        print(f"Error crítico durante la descarga/desempaquetado: {e}")
        return None

def verificar_modificacion_remota():
    """
    Simulación o verificación de metadatos para la sincronización incremental.
    """
    return "2026-06-15"