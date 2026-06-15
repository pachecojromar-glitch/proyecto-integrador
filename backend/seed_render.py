import requests

BASE_URL = "https://proyecto-integrador-cy02.onrender.com"

usuarios = [
    {"nombre": "Elian Jami", "usuario": "elianjami", "email": "elian@pinly.com", "password": "admin12345"},
    {"nombre": "Ana Paisajes", "usuario": "ana_paisajes", "email": "ana@pinly.com", "password": "ana123456"},
    {"nombre": "Dario Chef", "usuario": "chef_dario", "email": "dario@pinly.com", "password": "dario12345"},
]

for u in usuarios:
    r = requests.post(f"{BASE_URL}/usuarios/register", json=u)
    print(f"{u['usuario']}: {r.status_code} {r.json()}")