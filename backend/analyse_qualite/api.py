from fastapi import FastAPI, HTTPException
from analyse_qualite import run_quality_analysis 
from pydantic import BaseModel
import os

app = FastAPI()

# Modèle pour recevoir le chemin de fichier dans la requête JSON
class VideoPath(BaseModel):
    video_path: str

@app.get("/quality_analysis/healthcheck")
def healthcheck():
    return {"status": "healthy"}

@app.post("/quality_analysis/")
async def quality_analysis(video: VideoPath):
    input_video_path = video.video_path

    # Vérifier que le fichier existe
    if not os.path.exists(input_video_path):
        raise HTTPException(status_code=404, detail=f"Fichier non trouvé : {input_video_path}")

    try:
        # Appel de la fonction d'analyse de qualité
        quality_result = run_quality_analysis(input_video_path)

        # Retour des résultats
        return quality_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))