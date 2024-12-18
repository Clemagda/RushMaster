import os
import pandas as pd
import requests


OUTPUT_DIR = '/app/shared/outputs'
PROCESSED_DIR = '/app/shared/processed'


class CSVGenerationRequest:
    def __init__(self, user_id: str, processed_path: str):
        self.user_id = user_id
        self.processed_path = processed_path.strip()


def generate_xlsx(request: CSVGenerationRequest):
    """
    Fusionne les résultats des traitements vidéos dans un fichier Excel et l'upload dans le bucket S3.
    """
    user_id = request.user_id
    processed_path = request.processed_path

    if not os.path.exists(processed_path):
        raise FileNotFoundError(f"Le chemin {processed_path} est introuvable.")

    try:
        # Vérification des fichiers dans le répertoire traité
        files = os.listdir(processed_path)
        if not files:
            raise FileNotFoundError(
                "Aucun fichier trouvé dans {}.".format(processed_path))
        print('Fichiers trouvés pour {} : {}'.format(user_id, files))

        video_files = [os.path.join(processed_path, f) for f in files if f.endswith(
            (".mp4", ".mov", ".avi", ".mkv"))]
        results = []

        for video_path in video_files:
            video_id = os.path.basename(video_path).split('.')[0]

            try:
                print(f"=== Prétraitement de la vidéo {video_id} ===")
                response_transcription = requests.post(
                    "http://transcription-audio-service:8002/transcribe", json={"video_path": video_path})
                print(
                    f"Réponse transcription audio - Statut: {response_transcription.status_code}, Contenu: {response_transcription.text}")
                transcription_result = response_transcription.json().get("transcription", "N/A")

                # 2. Appel de l'API d'analyse qualité
                print(f"=== Analyse qualité de la vidéo {video_id} ===")
                response_quality = requests.post(
                    "http://analyse-qualite-service:8001/quality_analysis", json={"video_path": video_path})
                print(
                    f"Réponse analyse qualité - Statut: {response_quality.status_code}, Contenu: {response_quality.text}")
                quality_result = response_quality.json() if response_quality.status_code == 200 else {
                    "error": "Quality analysis failed"}

                # 3. Appel de l'API de génération de résumé
                print(f"=== Génération du résumé de la vidéo {video_id} ===")
                response_summary = requests.post(
                    "http://generation-resume-service:8003/generate_summary", json={"video_path": video_path})
                print(
                    f"Réponse génération de résumé - Statut: {response_summary.status_code}, Contenu: {response_summary.text}")
                resume_result = response_summary.json().get(
                    "summary", "N/A") if response_summary.status_code == 200 else "N/A"

                results.append({
                    "video_id": video_id,
                    "Transcription audio": transcription_result,
                    "Qualité": quality_result,
                    "Résumé vidéo": resume_result
                })

            except Exception as e:
                print("Erreur lors du traitement de la video {} : {}".format(
                    video_id, e))

        if results:
            df = pd.DataFrame(results)
            print(f"Apercu des resultats : {df.head()}")
            output_filename = os.path.join(
                OUTPUT_DIR, f"{user_id}_results.xlsx")
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            df.to_excel(output_filename, index=False)
            print(f"Fichier excel genere : {output_filename}")
            return output_filename
        else:
            print("Aucun résultat à enregistrer.")
    except Exception as e:
        print(f"Erreur lors du traitement des vidéos : {e}")
        raise RuntimeError(f"Erreur lors du traitement des vidéos : {e}")


if __name__ == "__main__":
    print("===== Début du traitement =====")
    # Exemple d'utilisation
    request = CSVGenerationRequest(
        user_id="test_user",
        processed_path="{}/test_user.".format(PROCESSED_DIR)
    )
    try:
        generate_xlsx(request)
    except Exception as e:
        print(f"Erreur générale : {e}")
    print("===== Fin du traitement =====")
