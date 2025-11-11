# main.py
import os
import json
import uuid
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, ValidationError
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Logging básico (systemd recogerá estas salidas)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_s3")

app = FastAPI(title="API Personas -> S3")

# Obtener bucket desde variable de entorno (recomendado)
BUCKET_NAME = os.getenv("BUCKET_NAME", "ec2-jd")  # cambia por env var en la instancia

# Modelo de validación
class Persona(BaseModel):
    nombre: str = Field(..., min_length=1)
    edad: int = Field(..., ge=0, le=150)
    correo: EmailStr

# Cliente S3 (usará automáticamente credenciales del role o las credenciales configuradas en el host)
s3 = boto3.client("s3")

def count_objects_in_bucket(bucket_name: str) -> int:
    """Cuenta todos los objetos en el bucket (paginado)."""
    paginator = s3.get_paginator("list_objects_v2")
    total = 0
    try:
        for page in paginator.paginate(Bucket=bucket_name):
            total += page.get("KeyCount", 0)
    except ClientError as e:
        logger.exception("Error al listar objetos del bucket")
        raise
    return total

@app.post("/insert")
def insert_persona(persona: Persona):
    # Validación Pydantic ya se hizo antes de llegar aquí
    if BUCKET_NAME == "tu-bucket-aqui" or not BUCKET_NAME:
        logger.error("BUCKET_NAME no configurado. Define la variable de entorno BUCKET_NAME.")
        raise HTTPException(status_code=500, detail="Bucket no configurado en la aplicación.")

    file_id = str(uuid.uuid4())
    key = f"{file_id}.json"
    body = json.dumps(persona.dict(), ensure_ascii=False)

    try:
        # Intentar subir el objeto
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=body, ContentType="application/json")
        logger.info("Objeto subido a S3: %s/%s", BUCKET_NAME, key)

        # Contar archivos en el bucket
        total = count_objects_in_bucket(BUCKET_NAME)
        return {"archivos_totales": total, "archivo_subido": key}

    except ClientError as e:
        # Error de AWS (p. ej. permisos, bucket inexistente)
        logger.exception("Error de AWS al manipular S3: %s", e)
        raise HTTPException(status_code=502, detail=f"Error de S3: {e.response.get('Error', {}).get('Message', str(e))}")

    except BotoCoreError as e:
        # Otro error de boto
        logger.exception("Error BotoCore")
        raise HTTPException(status_code=502, detail="Error interno de AWS SDK")

    except Exception as e:
        # Catch-all (evitar 500 sin info)
        logger.exception("Error inesperado en /insert")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
