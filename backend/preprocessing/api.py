from fastapi import FastAPI, UploadFile, File
from preprocessing import preprocess_video
import tempfile
import os

app = FastAPI()

@app.post("/preprocess/")
async def preprocess_video_endpoint(file: UploadFile = File(...)):
    # Sauvegarder temporairement le fichier vidéo reçu
    input_video_path = f"/app/shared/inputs/{file.filename}"

    with open(input_video_path, 'wb') as f:
        f.write(await file.read())

    processed_video_path = preprocess_video(input_video_path)
    return {"message": "Vidéo pretraitee avec succes",
            "processed_video_path": processed_video_path}