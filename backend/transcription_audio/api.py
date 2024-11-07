from fastapi import FastAPI, UploadFile, File
from transcription_audio import run_transcription
from pydantic import BaseModel
import tempfile
import os

app = FastAPI()

class VideoPath(BaseModel):
    video_path: str
    language: str = "en"

@app.get("/transcribe/healthcheck")
def healthcheck():
    return {"status": "healthy"}

@app.post("/transcribe/")
async def transcribe_video(video: VideoPath):
    input_video_path = video.video_path
    language = video.language

    # Assurez-vous que le fichier existe
    if not os.path.exists(input_video_path):
        return {"error": "Fichier non trouvé", "path": input_video_path}

    # Appeler la fonction de transcription
    transcription = run_transcription(input_video_path, language)

    # Retourner la transcription
    return {"transcription": transcription}
