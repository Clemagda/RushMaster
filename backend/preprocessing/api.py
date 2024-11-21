from fastapi import FastAPI  # type: ignore
from preprocessing import preprocess_all_videos

app = FastAPI()


@app.get("/preprocess/healthcheck")
def healthcheck():
    return {"status": "healthy"}


@app.post("/preprocess/")
async def preprocess_videos():
    """
    Endpoint pour traiter toutes les vidéos dans le répertoire d'entrée.
    Appelle également l'API de génération de fichier Excel une fois le traitement terminé.
    """
    try:
        preprocess_all_videos()  # Appel de la fonction pour traiter toutes les vidéos
        return {"message": "Toutes les vidéos ont été prétraitées et la génération Excel a été déclenchée."}
    except Exception as e:
        return {"error": f"Échec du prétraitement ou de la génération Excel : {str(e)}"}
