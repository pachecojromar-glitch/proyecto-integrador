import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzgxNTU1NTQzLCJpYXQiOjE3ODE1NDQ3NDN9.0kPTbRxnftKxW-GMJiQw1w-qbF85HBuu_CTQuvoMV4s"

headers = {"Authorization": f"Bearer {token}"}

files = {"imagen": open(r"C:\Users\pache\Downloads\proyecto\deportes\Especial fotográfico_ los mejores matadores de la historia de la NBA (anterior a los 90).jpg", "rb")}

data = {
    "titulo": "Pin de prueba S3",
    "categoria": "Tecnologia",
    "descripcion": "Prueba de subida a S3",
    "es_publico": "true",
}

response = requests.post("http://127.0.0.1:8000/pines/", headers=headers, files=files, data=data)
print(response.status_code)
print(response.json())