from fastapi import FastAPI, UploadFile, File
from preprocessing import preprocess_video
import tempfile
import os

app = FastAPI()

@app.post("/preprocess/")
async def preprocess_video_endpoint(file: UploadFile = File(...)):
    # Sauvegarder temporairement le fichier vidéo reçu
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_video_path = temp_video_file.name
    with open(temp_video_path, 'wb') as f:
        f.write(await file.read())
    
    # Lancer le prétraitement
    preprocess_video(temp_video_path)

    # Supprimer le fichier temporaire après prétraitement
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)

    return {"message": "Vidéo prétraitée et sauvegardée dans le bucket S3"}
