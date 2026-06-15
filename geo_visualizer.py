import webbrowser
import os
from pyproj import Transformer
import folium

def transformar_coordenadas(crtm05_x, crtm05_y):
    """Transforma coordenadas planas del modelo nacional CRTM05 a geocéntricas WGS84.

    Utiliza algoritmos cartográficos matemáticos provistos por la biblioteca 
    pyproj para realizar la proyección de puntos geográficos.

    Args:
        crtm05_x (float): Coordenada en el eje X (Este) bajo el estándar EPSG:5367.
        crtm05_y (float): Coordenada en el eje Y (Norte) bajo el estándar EPSG:5367.

    Returns:
        tuple: Pareja de floats (latitud, longitud) en el sistema global EPSG:4326, 
               o None si falla.
    """
    try:
        transformer = Transformer.from_crs("EPSG:5367", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(crtm05_x, crtm05_y)
        return lat, lon
    except Exception as e:
        print(f"Error durante la conversión cartográfica: {e}")
        return None

def generar_mapa_asada(asada_data):
    """Renderiza una vista interactiva de OpenStreetMap centrada en la ASADA.

    Calcula la posición global WGS84, inicializa una plantilla HTML mediante folium, 
    inyecta un marcador dinámico y ordena la apertura automática en el navegador web.

    Args:
        asada_data (dict): Diccionario extendido con las propiedades de la ASADA.
    """
    x = asada_data.get("coordenadaX")
    y = asada_data.get("coordenadaY")
    nombre = asada_data.get("operador", "ASADA sin Nombre Identificado")
    
    if not x or not y:
        print("El registro seleccionado carece de coordenadas geoespaciales válidas.")
        return

    coordenadas_wgs84 = transformar_coordenadas(float(x), float(y))
    if coordenadas_wgs84:
        lat, lon = coordenadas_wgs84
        
        mapa = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{nombre}</b><br>ID: {asada_data.get('id_Asada')}<br>Distrito: {asada_data.get('distrito')}",
            icon=folium.Icon(color="blue", icon="cloud")
        ).add_to(mapa)
        
        archivo_html = "mapa_asada_dinamico.html"
        mapa.save(archivo_html)
        
        webbrowser.open("file://" + os.path.realpath(archivo_html))
        print("Localización visualizada de forma exitosa en OpenStreetMap.")