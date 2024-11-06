from fastapi import FastAPI
from csv_generation import process_video

app = FastAPI()

@app.get("/generate-xlsx/healthcheck")
def healthcheck():
    return {"status": "healthy"}

@app.post("/generate-xlsx/")
async def generate_xlsx():
    """
    Appel pour générer le fichier Excel à partir des vidéos dans le dossier 'processed'.
    """
    try:
        process_video()
        return {"message": "Excel file generated successfully."}
    except Exception as e:
        return {"error": f"Failed to generate Excel file: {str(e)}"}
