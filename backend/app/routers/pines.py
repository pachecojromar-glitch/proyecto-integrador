import uuid

import boto3
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import func, select

from app.auth import get_current_user, get_optional_user
from app.config import settings
from db import SessionDep
from models import (
    Comentarios,
    Likes,
    Pines,
    PinesPublic,
    Usuarios,
)

router = APIRouter(prefix="/pines", tags=["Pines"])


s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def _pin_visible_filter():
    return (Pines.deleted_at == None) & (Pines.es_publico == True)  # noqa: E712


def _serializar_pin(pin: Pines, session: SessionDep, usuario_actual: Usuarios | None) -> dict:
    likes_count = session.exec(
        select(func.count(Likes.id)).where(Likes.pin_id == pin.id)
    ).one()

    comentarios_count = session.exec(
        select(func.count(Comentarios.id)).where(Comentarios.pin_id == pin.id)
    ).one()

    dio_like = False
    if usuario_actual:
        like_existente = session.exec(
            select(Likes).where(
                (Likes.pin_id == pin.id) & (Likes.usuario_id == usuario_actual.id)
            )
        ).first()
        dio_like = like_existente is not None

    return {
        "id": pin.id,
        "titulo": pin.titulo,
        "descripcion": pin.descripcion,
        "tags": pin.tags,
        "categoria": pin.categoria,
        "source": pin.source,
        "es_publico": pin.es_publico,
        "created_at": pin.created_at,
        "autor": pin.autor,
        "likes_count": likes_count,
        "comentarios_count": comentarios_count,
        "dio_like": dio_like,
    }


@router.get("/", response_model=list[PinesPublic])
def listar_pines(
    session: SessionDep,
    categoria: str | None = None,
    buscar: str | None = None,
    usuario: str | None = None,
    usuario_actual: Usuarios | None = Depends(get_optional_user),
):
    query = select(Pines).where(_pin_visible_filter())

    if categoria:
        query = query.where(Pines.categoria == categoria)

    if buscar:
        like_pattern = f"%{buscar.lower()}%"
        query = query.where(
            func.lower(Pines.titulo).like(like_pattern)
            | func.lower(Pines.descripcion).like(like_pattern)
            | func.lower(Pines.tags).like(like_pattern)
        )

    if usuario:
        usuario_db = session.exec(
            select(Usuarios).where(Usuarios.usuario == usuario.lower())
        ).first()
        if not usuario_db:
            return []
        query = query.where(Pines.usuario_id == usuario_db.id)

    pines = session.exec(query).all()

    from random import sample
    if not categoria and not buscar and not usuario and len(pines) > 1:
        pines = sample(pines, len(pines))

    return [_serializar_pin(p, session, usuario_actual) for p in pines]


@router.get("/{pin_id}", response_model=PinesPublic)
def obtener_pin(
    pin_id: int,
    session: SessionDep,
    usuario_actual: Usuarios | None = Depends(get_optional_user),
):
    pin = session.get(Pines, pin_id)

    if not pin or pin.deleted_at is not None or not pin.es_publico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El pin no fue encontrado",
        )

    return _serializar_pin(pin, session, usuario_actual)


@router.post("/", response_model=PinesPublic, status_code=status.HTTP_201_CREATED)
def crear_pin(
    session: SessionDep,
    usuario_actual: Usuarios = Depends(get_current_user),
    titulo: str = Form(...),
    categoria: str = Form(...),
    descripcion: str | None = Form(None),
    tags: str | None = Form(None),
    es_publico: bool = Form(True),
    imagen: UploadFile = File(...),
):
    s3_key = f"Publicaciones/{uuid.uuid4()}-{imagen.filename}"

    s3.upload_fileobj(
        imagen.file,
        settings.S3_BUCKET_NAME,
        s3_key,
    ExtraArgs={"ContentType": imagen.content_type or "image/jpeg"}
    )

    url_publica = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
        ExpiresIn=3600
    )

    pin = Pines(
        titulo=titulo,
        descripcion=descripcion,
        tags=tags,
        categoria=categoria,
        source=url_publica,
        es_publico=es_publico,
        usuario_id=usuario_actual.id,
    )
    session.add(pin)
    session.commit()
    session.refresh(pin)
    return _serializar_pin(pin, session, usuario_actual)