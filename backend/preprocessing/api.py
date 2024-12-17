from fastapi import FastAPI, Form  # type: ignore
from preprocessing import preprocess_all_videos
from pydantic import BaseModel

app = FastAPI()


class PreprocessRequest(BaseModel):
    user_id: str


@app.get("/preprocess/healthcheck")
def healthcheck():
    return {"status": "healthy"}


@app.post("/preprocess/")
async def preprocess_all_videos(request: PreprocessRequest):
    """
    Endpoint pour traiter toutes les vidéos dans le répertoire d'entrée.
    Appelle également l'API de génération de fichier Excel une fois le traitement terminé.
    """

    user_id = request.user_id

    try:
        # Appel de la fonction pour traiter toutes les vidéos
        preprocess_all_videos(user_id=user_id)
        return {"message": f"Toutes les vidéos pour l'utilisateur {user_id} ont été prétraitées et la génération Excel a été déclenchée."}
    except Exception as e:
        return {"error": f"Échec du prétraitement ou de la génération Excel pour l'utilisateur {user_id} : {str(e)}"}
