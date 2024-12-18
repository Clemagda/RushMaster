from fastapi import FastAPI, Form, HTTPException  # type: ignore
from preprocessing import preprocess_all_videos
from pydantic import BaseModel
import asyncio
import logging


# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()


class PreprocessRequest(BaseModel):
    user_id: str


@app.get("/preprocess/healthcheck")
def healthcheck():
    return {"status": "healthy"}


@app.post("/preprocess/")
async def preprocess_endpoint(request: PreprocessRequest):
    """
    Endpoint pour traiter toutes les vidéos dans le répertoire d'entrée.
    Appelle également l'API de génération de fichier Excel une fois le traitement terminé.
    """

    user_id = request.user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id est obligatoire.")
    logger.info(f"Prétraitement déclenché pour user_id : {user_id}")

    try:
        await asyncio.to_thread(preprocess_all_videos, user_id)
        return {"message": f"Toutes les vidéos pour l'utilisateur {user_id} ont été prétraitées et la génération Excel a été déclenchée."}
    except Exception as e:
        logger.error(f"Erreur pour user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Une erreur s'est produite lors du prétraitement des vidéos.")
