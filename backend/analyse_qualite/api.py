from fastapi import FastAPI, UploadFile, File, HTTPException
from analyse_qualite import run_quality_analysis  # Fonction principale d'analyse de qualité
import tempfile
import os

app = FastAPI()

@app.post("/quality_analysis/")
async def quality_analysis(file: UploadFile = File(...)):
    try:
        # Enregistrement du fichier vidéo temporairement
        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video_path = temp_video_file.name
        with open(temp_video_path, 'wb') as f:
            f.write(await file.read())
        
        # Appel de la fonction d'analyse de qualité
        quality_result = run_quality_analysis(temp_video_path)

        # Retour des résultats au format JSON
        return quality_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Suppression du fichier temporaire
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
