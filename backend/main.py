from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import create_all_tables
from app.routers import usuarios, pines, categorias, comentarios, likes

app = FastAPI(title="Pinly API", lifespan=create_all_tables)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(pines.router)
app.include_router(categorias.router)
app.include_router(comentarios.router)
app.include_router(likes.router)

@app.get("/")
def root():
    return {"message": "Pinly API funcionando"}