from fastapi import FastAPI, UploadFile, File, HTTPException
import os

app = FastAPI()

# Répertoire de destination pour les fichiers téléchargés sur EFS
UPLOAD_DIRECTORY = "/mnt/efs/inputs/"

# Vérifier que le répertoire existe, sinon le créer
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Créer le chemin complet pour enregistrer le fichier
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

        # Écrire le fichier sur le système de fichiers
        with open(file_location, "wb") as f:
            f.write(await file.read())

        return {"message": f"Fichier '{file.filename}' téléversé avec succès à l'emplacement {file_location}."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors du téléversement du fichier : {str(e)}")
