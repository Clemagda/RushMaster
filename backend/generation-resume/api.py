from fastapi import FastAPI, UploadFile, File
from generation_resume import run_inference
from pydantic import BaseModel
import tempfile
import os

app = FastAPI()

class VideoPath(BaseModel):
    video_path: str

@app.get("/generate_summary/healthcheck")
def healthcheck():
    return {"status": "healthy"}

@app.post("/generate_summary/")
async def generate_summary(video : VideoPath):
    input_video_path = video.video_path

    # Vérifier que le fichier existe
    if not os.path.exists(input_video_path):
        return {"error": "Fichier non trouvé", "path": input_video_path}

    # Appel de la fonction de génération de résumé
    summary = run_inference(input_video_path)

    # Retourner le résumé
    return {"summary": summary}