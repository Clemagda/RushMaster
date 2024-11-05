from fastapi import FastAPI, UploadFile, File
from transcription_audio import run_transcription
import tempfile
import os

app = FastAPI()

@app.post("/transcribe/")
async def transcribe_video(file: UploadFile = File(...), language: str = "en"):
    try:
        # Sauvegarder le fichier vidéo reçu temporairement
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_path = temp_video_file.name
        with open(temp_video_path, 'wb') as f:
            f.write(await file.read())

        # Transcrire l'audio
        transcription = run_transcription(temp_video_path, language)

        # Retourner la transcription
        return {"transcription": transcription}

    finally:
        # Nettoyer les fichiers temporaires
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
