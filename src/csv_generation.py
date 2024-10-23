
import os

from main_processing import process_video
from preprocessing import preprocess_video
import boto3 # type: ignore
from botocore.exceptions import ClientError # type: ignore
import pandas as pd # type: ignore

def is_cloud_environment():
    """
    Vérifie l'environnement via une variable d'environnement.
    Si ENVIRONMENT est défini sur "CLOUD", alors nous sommes sur le cloud (S3).
    Sinon, c'est un environnement local.
    """
    return os.getenv("ENVIRONMENT", "LOCAL") == "CLOUD"

s3 = boto3.client('s3') if is_cloud_environment() else None

def get_video_files_from_directory(input_dir_or_bucket):
    """
    Récupère tous les fichiers vidéo du dossier spécifié.

    Args:
        input_dir (str): Chemin du dossier contenant les fichiers vidéo.
        
    Returns:
        list: Liste des chemins des fichiers vidéo.
    """
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']  
    video_files = []

    if is_cloud_environment():
        try:
            # Lister les objets dans le bucket S3 (par exemple, préfixe 'input/')
            response = s3.list_objects_v2(Bucket=input_dir_or_bucket, Prefix='Inputs/')
            for obj in response.get('Contents', []):
                video_key = obj['Key']
                local_video_path = f"/tmp/{os.path.basename(video_key)}"
                
                # Télécharger chaque vidéo depuis S3 dans le répertoire temporaire
                try:
                    s3.head_object(Bucket=input_dir_or_bucket, Key=video_key)  # Vérifie si la vidéo existe dans S3
                    s3.download_file(input_dir_or_bucket, video_key, local_video_path)
                    video_files.append(local_video_path)
                except ClientError as e:
                    print(f"Le fichier {video_key} n'existe pas dans S3 ou n'a pas pu être téléchargé : {e}")
                    continue  

        except ClientError as e:
            print(f"Erreur lors de la récupération des fichiers depuis S3 : {e}")
    
    else:
    #Import local des vidéos
        video_files = [os.path.join(input_dir_or_bucket, file) for file in os.listdir(input_dir_or_bucket) 
                    if os.path.splitext(file)[1].lower() in video_extensions]
        
    return video_files

def create_csv_file(input_dir_or_bucket, output_csv, output_dir="Outputs", language="en"):
    """
    Fusionne les résultats des trois scripts dans un fichier CSV.
    
    Args:
        video_files (list): Liste des chemins des fichiers vidéo.
        output_csv (str): Chemin du fichier CSV de sortie.
        output_dir (str): Répertoire où sauvegarder les résultats intermédiaires.
        language (str): Langue pour la transcription ('fr' pour français, 'en' pour anglais).
    """
           
    video_files = get_video_files_from_directory(input_dir_or_bucket)
    results=[]

    #with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        # Définition des en-têtes des colonnes
     #   fieldnames = ['video_id', 'quality_analysis', 'audio_transcription', 'video_summary']
      #  writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        #if csv_file.tell() ==0:
         #   writer.writeheader()

        # Parcourir chaque fichier vidéo
    for video in video_files:
        video_id = os.path.basename(video).split('.')[0]  # Utiliser le nom du fichier sans extension

        try:     
            print(f"===Prétraitement de la vidéo ===")          
            temp_video = preprocess_video(video,output_path=f"temp/processed_{video_id}.mp4")
            print(f"=== prête ===")
            
            print(f"===Traitement de la vidéo ===")
            result = process_video(temp_video, output_dir, language="en")
            result['video_id'] = video_id
            results.append(result)
            os.remove(temp_video)
       
        except Exception as e:
            print(f"Erreur lors du traitement de la video  : {e}")

    if results:
        df = pd.DataFrame(results)
        output_path = output_csv 
        df.to_excel(output_path, index=False)
        print(f"Fichier Excel créé avec succès : {output_path}")
    else:
        print("Aucun résultat à enregistrer.")

        if is_cloud_environment():
            s3.upload_file(output_csv, input_dir_or_bucket,f'outputs/{os.path.basename(output_csv)}')
        
    print(f"Les résultats ont été sauvegardés dans {output_csv} (ou dans le bucket S3).")


if __name__ == "__main__":
    if is_cloud_environment():
        print("=====Execution dans un environnement Cloud=====")
    else:
        print("=====Execution dans un environnement local=====")

    input_dir_or_bucket = "Inputs" if not is_cloud_environment() else "data-rushmaster"
    output_csv = "Outputs/results.xlsx" if not is_cloud_environment() else "/tmp/results.xlsx"
    output_dir = "Outputs" if not is_cloud_environment() else "/tmp"
    language = "en"

    print("=====Traitement des vidéos=====")
    create_csv_file(input_dir_or_bucket, output_csv, output_dir, language)
