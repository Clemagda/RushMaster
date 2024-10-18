import csv
import os
from main_processing import process_video

def get_video_files_from_directory(input_dir):
    """
    Récupère tous les fichiers vidéo du dossier spécifié.

    Args:
        input_dir (str): Chemin du dossier contenant les fichiers vidéo.
        
    Returns:
        list: Liste des chemins des fichiers vidéo.
    """
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']  
    video_files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) 
                   if os.path.splitext(file)[1].lower() in video_extensions]
    return video_files

def create_csv_file(input_dir="Inputs", output_csv="Outputs/results.csv", output_dir="Outputs", language="en"):
    """
    Fusionne les résultats des trois scripts dans un fichier CSV.
    
    Args:
        video_files (list): Liste des chemins des fichiers vidéo.
        output_csv (str): Chemin du fichier CSV de sortie.
        output_dir (str): Répertoire où sauvegarder les résultats intermédiaires.
        language (str): Langue pour la transcription ('fr' pour français, 'en' pour anglais).
    """
    input_dir = "Inputs"
    video_files = get_video_files_from_directory(input_dir)
    
    with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        # Définition des en-têtes des colonnes
        fieldnames = ['video_id', 'quality_analysis', 'audio_transcription', 'video_summary']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        if csv_file.tell() ==0:
            writer.writeheader()

        # Parcourir chaque fichier vidéo
        for video in video_files:
            video_id = os.path.basename(video).split('.')[0]  # Utiliser le nom du fichier sans extension

            try:
                # Appeler les fonctions des scripts individuels
                video_output_dir = os.path.join(output_dir, video_id)
                os.makedirs(video_output_dir, exist_ok=True)
                results = process_video(video, output_dir, language="en")
                writer.writerow({
                    'video_id': video_id, **results
                })
            except Exception as e:
                print(f"Erreur lors du traitement de la video {video_id} : {e}")
                writer.writerow({
                    'video_id': video_id,
                    'quality_analysis': "Erreur.",
                    'audio_transcription': "Erreur.",
                    'video_summary': "Erreur."
                })
            
    print(f"Le rapport est disponible dans : {output_csv}")


if __name__ == "__main__":
    create_csv_file()
