from fastapi import FastAPI, Form
from csv_generation import process_video

app = FastAPI()

@app.get("/generate-xlsx/healthcheck")
def healthcheck():
    return {"status": "healthy"}

@app.post("/generate-xlsx/")
async def generate_xlsx(user_id: str = Form(...)):
    """
    Appel pour générer le fichier Excel à partir des vidéos dans le dossier 'processed'.
    """
    try:
        process_video(user_id=user_id)
        return {"message": f"Fichier Excel généré avec succès pour l'utilisateur {user_id}."}
    except Exception as e:
        return {"error": f"Échec de la génération du fichier Excel pour l'utilisateur {user_id} : {str(e)}"}
