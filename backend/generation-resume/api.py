from fastapi import FastAPI, UploadFile, File
from generation_resume import run_inference  
import tempfile
import os

app = FastAPI()

@app.get("/generate_summary/healthcheck")
def healthcheck():
    return {"status": "healthy"}

@app.post("/generate_summary/")
async def generate_summary(file: UploadFile = File(...)):
    try:
        # Sauvegarde temporaire du fichier vidéo reçu
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_path = temp_video_file.name
        with open(temp_video_path, 'wb') as f:
            f.write(await file.read())
        
        # Appel de la fonction de génération de résumé
        summary = run_inference(temp_video_path)

        # Renvoie le résumé sous forme de JSON
        return {"summary": summary}

    finally:
        # Nettoyage du fichier temporaire
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
