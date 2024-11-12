import os
import pandas as pd
import requests


OUTPUT_DIR = '/app/shared/outputs'
PROCESSED_DIR = '/app/shared/processed'


def process_video():
    """
    Fusionne les résultats des traitements vidéos dans un fichier Excel et l'upload dans le bucket S3.
    """
    video_files = [os.path.join(PROCESSED_DIR, f) for f in os.listdir(
        PROCESSED_DIR) if f.endswith(('.mp4', '.mov', '.avi', '.mkv'))]
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

            result = {
                "video_id": video_id,
                "Transcription audio": transcription_result,
                "Qualité": quality_result,
                "Résumé vidéo": resume_result
            }
            results.append(result)
        except Exception as e:
            print(f"Erreur lors du traitement de la video {video_id} : {e}")

    if results:
        df = pd.DataFrame(results)
        print(f"Apercu des resultats : {df.head()}")
        output_filename = os.path.join(OUTPUT_DIR, "results.xlsx")
        df.to_excel(output_filename, index=False)
    else:
        print("Aucun résultat à enregistrer.")


if __name__ == "__main__":
    print("===== Début du traitement des vidéos dans le bucket S3 =====")
    process_video()
    print("===== Fin du traitement =====")
