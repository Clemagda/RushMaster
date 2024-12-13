from fastapi import FastAPI, Form  # type: ignore
from preprocessing import preprocess_all_videos

app = FastAPI()


@app.get("/preprocess/healthcheck")
def healthcheck():
    return {"status": "healthy"}


@app.post("/preprocess/")
async def preprocess_videos(user_id: str = Form(...)):
    """
    Endpoint pour traiter toutes les vidéos dans le répertoire d'entrée.
    Appelle également l'API de génération de fichier Excel une fois le traitement terminé.
    """
    try:
        preprocess_all_videos(user_id=user_id)  # Appel de la fonction pour traiter toutes les vidéos
        return {"message": f"Toutes les vidéos pour l'utilisateur {user_id} ont été prétraitées et la génération Excel a été déclenchée."}
    except Exception as e:
        return {"error": f"Échec du prétraitement ou de la génération Excel pour l'utilisateur {user_id} : {str(e)}"}
