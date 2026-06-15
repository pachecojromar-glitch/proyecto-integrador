# script que puebla la base con datos iniciales
# se corre una sola vez despues de levantar la api por primera vez
# uso: python seed.py

from sqlmodel import Session, select

from db import engine
from models import Usuarios, Pines, Rol
from app.auth import hash_password


# usuarios iniciales, el primero es admin para poder defender el rol diferenciado
USUARIOS_INICIALES = [
    {
        "nombre": "Elian Jami",
        "usuario": "elianjami",
        "email": "elian@pinly.com",
        "password": "admin12345",  # se hashea antes de guardar, jamas se guarda en claro
        "bio": "Admin de Pinly, estudiante de Sistemas en UIDE.",
        "rol": Rol.ADMIN,
    },
    {
        "nombre": "Ana Paisajes",
        "usuario": "ana_paisajes",
        "email": "ana@pinly.com",
        "password": "ana123456",
        "bio": "Amante de los paisajes y la fotografia de naturaleza.",
        "rol": Rol.USER,
    },
    {
        "nombre": "Dario Chef",
        "usuario": "chef_dario",
        "email": "dario@pinly.com",
        "password": "dario12345",
        "bio": "Cocina casera, recetas faciles y comida ecuatoriana.",
        "rol": Rol.USER,
    },
]


# pines de prueba, las urls son placeholders hasta que el bucket S3 este listo
# despues del jueves estas urls se reemplazan por las reales del bucket
PINES_INICIALES = [
    {
        "titulo": "Atardecer en la montana",
        "descripcion": "Foto tomada en el cerro Atacazo al atardecer.",
        "tags": "viaje,paisaje,ecuador,atardecer",
        "categoria": "Viajes",
        "source": "https://picsum.photos/seed/pin1/600/800",
        "autor_usuario": "ana_paisajes",
    },
    {
        "titulo": "Receta de pasta casera",
        "descripcion": "Pasta italiana hecha en casa con harina y huevo.",
        "tags": "comida,pasta,italiana,receta",
        "categoria": "Comida",
        "source": "https://picsum.photos/seed/pin2/600/700",
        "autor_usuario": "chef_dario",
    },
    {
        "titulo": "Sala minimalista nordica",
        "descripcion": "Inspiracion para decorar una sala con estilo nordico.",
        "tags": "decoracion,minimalista,nordico,sala",
        "categoria": "Decoracion",
        "source": "https://picsum.photos/seed/pin3/600/750",
        "autor_usuario": "elianjami",
    },
    {
        "titulo": "Cachorro Husky",
        "descripcion": "Husky siberiano de dos meses jugando en la nieve.",
        "tags": "animales,perro,husky,mascota",
        "categoria": "Animales",
        "source": "https://picsum.photos/seed/pin4/600/600",
        "autor_usuario": "ana_paisajes",
    },
    {
        "titulo": "Ilustracion digital",
        "descripcion": "Trabajo de ilustracion digital hecho en Procreate.",
        "tags": "arte,ilustracion,digital,diseno",
        "categoria": "Arte",
        "source": "https://picsum.photos/seed/pin5/600/900",
        "autor_usuario": "elianjami",
    },
    {
        "titulo": "Setup gamer 2026",
        "descripcion": "Mi escritorio de trabajo y gaming actualizado.",
        "tags": "tecnologia,setup,gamer,pc",
        "categoria": "Tecnologia",
        "source": "https://picsum.photos/seed/pin6/600/750",
        "autor_usuario": "elianjami",
    },
    {
        "titulo": "Playa de Galapagos",
        "descripcion": "Atardecer en una playa virgen de las islas Galapagos.",
        "tags": "viaje,playa,ecuador,galapagos",
        "categoria": "Viajes",
        "source": "https://picsum.photos/seed/pin7/600/800",
        "autor_usuario": "ana_paisajes",
    },
    {
        "titulo": "Pastel de chocolate",
        "descripcion": "Pastel de chocolate con frosting de queso crema.",
        "tags": "comida,postre,chocolate,receta",
        "categoria": "Comida",
        "source": "https://picsum.photos/seed/pin8/600/700",
        "autor_usuario": "chef_dario",
    },
    {
        "titulo": "Jardin urbano vertical",
        "descripcion": "Ideas para hacer un jardin vertical en balcones pequenos.",
        "tags": "decoracion,jardin,plantas,vertical",
        "categoria": "Decoracion",
        "source": "https://picsum.photos/seed/pin9/600/800",
        "autor_usuario": "ana_paisajes",
    },
    {
        "titulo": "Logo design minimalista",
        "descripcion": "Proceso de creacion de un logo minimalista.",
        "tags": "arte,diseno,logo,branding",
        "categoria": "Arte",
        "source": "https://picsum.photos/seed/pin10/600/600",
        "autor_usuario": "elianjami",
    },
]


def poblar():
    with Session(engine) as session:
        # revisa si ya hay usuarios para no duplicar nada si el script se corre dos veces
        existentes = session.exec(select(Usuarios)).all()
        if existentes:
            print("La base de datos ya tiene usuarios, no se hace nada.")
            return

        # crea los usuarios primero, se necesitan los ids para asignar autores a los pines
        usuarios_creados = {}
        for datos in USUARIOS_INICIALES:
            nuevo = Usuarios(
                nombre=datos["nombre"],
                usuario=datos["usuario"],
                email=datos["email"],
                password=hash_password(datos["password"]),
                bio=datos["bio"],
                rol=datos["rol"],
            )
            session.add(nuevo)
            session.commit()
            session.refresh(nuevo)
            usuarios_creados[datos["usuario"]] = nuevo.id
            print(f"Usuario creado: {datos['usuario']} ({datos['rol'].value})")

        # ahora crea los pines, cada uno asociado a su autor por usuario_id
        for datos in PINES_INICIALES:
            autor_id = usuarios_creados.get(datos["autor_usuario"])
            if autor_id is None:
                print(f"Autor no encontrado para el pin: {datos['titulo']}")
                continue

            pin = Pines(
                titulo=datos["titulo"],
                descripcion=datos["descripcion"],
                tags=datos["tags"],
                categoria=datos["categoria"],
                source=datos["source"],
                usuario_id=autor_id,
                es_publico=True,
            )
            session.add(pin)

        session.commit()
        print(f"Listo, se agregaron {len(USUARIOS_INICIALES)} usuarios y {len(PINES_INICIALES)} pines.")


if __name__ == "__main__":
    poblar()