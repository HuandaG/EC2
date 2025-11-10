from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import json
import uuid

app = FastAPI()

# Configura tu bucket
BUCKET_NAME = "nombre-de-tu-bucket"

# Cliente S3 (usa tus credenciales de AWS)
s3 = boto3.client('s3')

# Modelo de validación
class Persona(BaseModel):
    nombre: str
    edad: int
    correo: str

@app.post("/insert")
def insert_persona(persona: Persona):
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}.json"

    data = persona.dict()
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=json.dumps(data),
        ContentType='application/json'
    )

    # Contar archivos
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    total_archivos = response.get('KeyCount', 0)

    return {"archivos_totales": total_archivos}
