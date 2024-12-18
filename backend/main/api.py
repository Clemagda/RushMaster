from fastapi import FastAPI, HTTPException
from csv_generation import generate_xlsx, CSVGenerationRequest
import os

app = FastAPI()


@app.get("/generate-xlsx/healthcheck")
def healthcheck():
    return {"status": "healthy"}


@app.post("/generate-xlsx/")
async def generate_xlsx_api(payload: dict):
    """
    Appel pour générer le fichier Excel à partir des vidéos dans le dossier 'processed'.
    """
    user_id = payload.get("user_id")
    processed_path = payload.get("processed_path")

    if not user_id or not processed_path:
        raise HTTPException(
            status_code=400, detail="Les champs 'user_id' et 'processed_path' sont obligatoires.")

    processed_path = processed_path.strip()

    if not os.path.exists(processed_path):
        raise HTTPException(
            status_code=404, detail="Le chemin {} est introuvable.".format(processed_path))

    try:
        # Préparer la requête pour le service de génération
        csv_request = CSVGenerationRequest(
            user_id=user_id, processed_path=processed_path)
        output_file = generate_xlsx(csv_request)

        if output_file:
            return {"message": f"Fichier Excel généré avec succès pour l'utilisateur {user_id}.", "file_path": output_file}
        else:
            return {"message": "Aucun résultat à enregistrer."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Échec de la génération du fichier Excel : {str(e)}")
