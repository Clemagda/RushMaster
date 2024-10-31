
import os

from main_processing import process_video
from preprocessing import preprocess_video
import boto3 # type: ignore
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError # type: ignore
import pandas as pd # type: ignore


s3 = boto3.client('s3', region_name='eu-west-3')

INPUT_BUCKET_NAME = 'data-rushmaster'
OUTPUT_BUCKET_NAME = 'data-rushmaster'
INPUT_PREFIX = "Inputs/"
OUTPUT_PREFIX = "Outputs/"

def get_video_files_from_s3():
    """
    Récupère tous les fichiers vidéo du bucket S3 spécifié et les télécharge localement.
    Returns:
        list: Liste des chemins des fichiers vidéo téléchargés.
    """
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    video_files = []

    try:
        # Lister les objets dans le bucket S3 avec le préfixe défini
        response = s3.list_objects_v2(Bucket=INPUT_BUCKET_NAME, Prefix=INPUT_PREFIX)
        for obj in response.get('Contents', []):
            video_key = obj['Key']
            if any(video_key.endswith(ext) for ext in video_extensions):
                # Créer /tmp si nécessaire
                if not os.path.exists('/tmp'):
                    os.makedirs('/tmp')
                
                local_video_path = f"/tmp/{os.path.basename(video_key)}"
                
                # Télécharger chaque vidéo depuis S3 dans le répertoire temporaire
                print(f"Téléchargement de {video_key} vers {local_video_path}")
                try:
                    s3.download_file(INPUT_BUCKET_NAME, video_key, local_video_path)
                    video_files.append(local_video_path)
                except ClientError as e:
                    print(f"Erreur lors du téléchargement de {video_key} : {e}")
                    continue
    except ClientError as e:
        print(f"Erreur lors de la récupération des fichiers depuis S3 : {e}")
    
    return video_files

def save_results_to_s3(dataframe, output_filename):
    """
    Enregistre les résultats du traitement dans un fichier Excel, puis le télécharge dans le bucket S3.
    
    Args:
        dataframe (pd.DataFrame): Le DataFrame contenant les résultats.
        output_filename (str): Nom du fichier Excel de sortie.
    """
    output_path = f'/tmp/{output_filename}'
    print(f"Enregistrement des résultats dans {output_path}")

    # Enregistrer dans un fichier Excel localement avant de l'envoyer à S3
    with pd.ExcelWriter(output_path) as writer:
        dataframe.to_excel(writer, index=False)

    # Charger le fichier dans S3
    try:
        print(f"Téléversement de {output_filename} vers S3 : {OUTPUT_BUCKET_NAME}/{OUTPUT_PREFIX}{output_filename}")
        s3.upload_file(output_path, OUTPUT_BUCKET_NAME, f'{OUTPUT_PREFIX}{output_filename}')
        print(f"Fichier de résultats téléversé avec succès dans S3 : {OUTPUT_BUCKET_NAME}/{OUTPUT_PREFIX}{output_filename}")
    except ClientError as e:
        print(f"Erreur lors du téléversement du fichier de résultats dans S3 : {e}")

def create_csv_file(language="en"):
    """
    Fusionne les résultats des traitements vidéos dans un fichier Excel et l'upload dans le bucket S3.
    """
    video_files = get_video_files_from_s3()
    results = []

    for video in video_files:
        video_id = os.path.basename(video).split('.')[0]  # Utiliser le nom du fichier sans extension

        try:
            print(f"=== Prétraitement de la vidéo {video_id} ===")
            temp_video = preprocess_video(video)
            print(f"Prétraitement de {video_id} terminé, traitement en cours...")

            result = process_video(temp_video, '/tmp', language=language)
            result['video_id'] = video_id
            results.append(result)
            os.remove(temp_video)
            print(f"Traitement de {video_id} terminé.")

        except Exception as e:
            print(f"Erreur lors du traitement de la vidéo {video_id} : {e}")

    if results:
        df = pd.DataFrame(results)
        save_results_to_s3(df, "results.xlsx")
        print("Fichier Excel créé et téléversé avec succès.")
    else:
        print("Aucun résultat à enregistrer.")

if __name__ == "__main__":
    print("===== Début du traitement des vidéos dans le bucket S3 =====")
    create_csv_file(language="en")
    print("===== Fin du traitement =====")