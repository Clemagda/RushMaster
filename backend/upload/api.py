from fastapi import FastAPI, UploadFile, File, HTTPException, Form
import os
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Répertoire de destination pour les fichiers téléchargés sur EFS
BASE_DIRECTORY = "/app/shared/inputs"


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...)):
    try:
        user_directory = os.path.join(BASE_DIRECTORY, user_id)

        # Créer le répertoire de l'utilisateur s'il n'existe pas
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)

        logger.info(f"Répertoire utilisateur : {user_directory}")

        # Créer le chemin complet pour enregistrer le fichier
        file_location = os.path.join(user_directory, file.filename)

        # Écrire le fichier sur le système de fichiers
        with open(file_location, "wb") as f:
            f.write(await file.read())

        logger.info(f"Fichier '{file.filename}' téléversé avec succès à l'emplacement {file_location}.")

        return {"message": f"Fichier '{file.filename}' téléversé avec succès à l'emplacement {file_location}."}

    except Exception as e:
        logger.error(f"Erreur lors du téléversement du fichier : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléversement du fichier : {str(e)}")
