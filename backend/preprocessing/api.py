from fastapi import FastAPI, UploadFile, File
from preprocessing import preprocess_video
from pydantic import BaseModel
import tempfile
import os

app = FastAPI()

class VideoPath(BaseModel):
    video_path: str

@app.get("/preprocess/healthcheck")
def healthcheck():
    return {"status": "healthy"}

@app.post("/preprocess/")
async def preprocess_video_endpoint(video: VideoPath):
    # Sauvegarder temporairement le fichier vidéo reçu
    input_video_path = video.video_path

    if not os.path.exists(input_video_path):
        return {"error": "Fichier non trouvé", "path": input_video_path}

    # Appeler la fonction de prétraitement
    processed_video_path = preprocess_video(input_video_path)

    return {"message": "Vidéo prétraitée avec succès", "processed_video_path": processed_video_path}