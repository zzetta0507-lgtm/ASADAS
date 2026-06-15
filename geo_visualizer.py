import webbrowser
import os
from pyproj import Transformer
import folium

def transformar_coordenadas(crtm05_x, crtm05_y):
    """
    Convierte coordenadas oficiales de Costa Rica CRTM05 a WGS84 (Lat, Lon).
    """
    try:
        # EPSG:5367 es el código internacional para CRTM05
        # EPSG:4326 es el código internacional para WGS84 (Lat/Lon)
        transformer = Transformer.from_crs("EPSG:5367", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(crtm05_x, crtm05_y)
        return lat, lon
    except Exception as e:
        print(f"Error en conversión cartográfica: {e}")
        return None

def generar_mapa_asada(asada_data):
    """
    Genera un archivo HTML con la ubicación de la ASADA en OpenStreetMap y lo abre.
    """
    x = asada_data.get("coordenadaX")
    y = asada_data.get("coordenadaY")
    nombre = asada_data.get("operador", "ASADA sin nombre")
    
    if not x or not y:
        print("La ASADA no cuenta con coordenadas geográficas válidas.")
        return

    coordenadas_wgs84 = transformar_coordenadas(float(x), float(y))
    if coordenadas_wgs84:
        lat, lon = coordenadas_wgs84
        
        # Crear mapa centrado en la ASADA
        mapa = folium.Map(location=[lat, lon], zoom_start=14)
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{nombre}</b><br>ID: {asada_data.get('id_Asada')}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)
        
        # Guardar y ejecutar automáticamente en el navegador
        archivo_html = "mapa_asada.html"
        mapa.save(archivo_html)
        webbrowser.open("file://" + os.path.realpath(archivo_html))
        print("Mapa generado y desplegado con éxito.")