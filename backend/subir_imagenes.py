import requests
import os

# Obtener token automáticamente
login = requests.post("http://127.0.0.1:8000/usuarios/login", json={
    "email": "elian@pinly.com",
    "password": "admin12345"
})
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Carpeta raíz donde están tus categorías
RUTA_BASE = r"C:\Users\pache\Downloads\proyecto"

# Mapeo de carpeta -> categoría en la app
CATEGORIAS = {
    "deportes": "Deportes",
    "ropa": "Ropa",
    "tecnologia": "Tecnologia",
    "videojuegos": "Videojuegos",
    "paisajes": "Paisajes",
}

extensiones_validas = (".jpg", ".jpeg", ".png", ".webp", ".gif")

for carpeta, categoria in CATEGORIAS.items():
    ruta_carpeta = os.path.join(RUTA_BASE, carpeta)
    
    if not os.path.exists(ruta_carpeta):
        print(f"[OMITIDA] Carpeta no encontrada: {ruta_carpeta}")
        continue

    imagenes = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(extensiones_validas)]
    print(f"\n {carpeta} — {len(imagenes)} imágenes")

    for imagen in imagenes:
        ruta_imagen = os.path.join(ruta_carpeta, imagen)
        nombre = os.path.splitext(imagen)[0]

        with open(ruta_imagen, "rb") as f:
            response = requests.post(
                "http://127.0.0.1:8000/pines/",
                headers=headers,
                files={"imagen": (imagen, f)},
                data={
                    "titulo": nombre[:50],
                    "categoria": categoria,
                    "descripcion": f"Imagen de {categoria.lower()}",
                    "es_publico": "true",
                }
            )

        if response.status_code == 201:
            print(f"  {imagen}")
        else:
            print(f"  {imagen} — {response.status_code}: {response.json()}")

print("\n Proceso terminado.")