import webbrowser
import os
from pyproj import Transformer
import folium

def transformar_coordenadas(crtm05_x, crtm05_y):
    """
    Realiza la conversión oficial matemática de coordenadas planas CRTM05 a WGS84.
    """
    try:
        # EPSG:5367 -> Código Geográfico de CRTM05 (Costa Rica)
        # EPSG:4326 -> Código Geográfico de WGS84 (Global Lat/Lon)
        transformer = Transformer.from_crs("EPSG:5367", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(crtm05_x, crtm05_y)
        return lat, lon
    except Exception as e:
        print(f"Error durante la conversión cartográfica: {e}")
        return None

def generar_mapa_asada(asada_data):
    """
    Genera dinámicamente un documento HTML embebiendo OpenStreetMap y lo abre de forma automática.
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
        
        # Inicialización del mapa en folium centrado en la ASADA consultada
        mapa = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{nombre}</b><br>ID: {asada_data.get('id_Asada')}<br>Distrito: {asada_data.get('distrito')}",
            icon=folium.Icon(color="blue", icon="cloud")
        ).add_to(mapa)
        
        archivo_html = "mapa_asada_dinamico.html"
        mapa.save(archivo_html)
        
        # Despliegue automático en el browser del sistema operativo
        webbrowser.open("file://" + os.path.realpath(archivo_html))
        print("Localización visualizada de forma exitosa en OpenStreetMap.")