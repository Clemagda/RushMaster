import csv
import os
from analyse_qualite import run_quality_analysis  
from generation_resume import run_inference  
from transcription_audio import run_transcription

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

def create_csv_output(video_files, output_csv, output_dir="Outputs", language="en"):
    """
    Fusionne les résultats des trois scripts dans un fichier CSV.
    
    Args:
        video_files (list): Liste des chemins des fichiers vidéo.
        output_csv (str): Chemin du fichier CSV de sortie.
        output_dir (str): Répertoire où sauvegarder les résultats intermédiaires.
        language (str): Langue pour la transcription ('fr' pour français, 'en' pour anglais).
    """
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
                quality_analysis = run_quality_analysis(video) 
                audio_transcription = run_transcription(video, language)  
                video_resume = run_inference(video)  

                if not quality_analysis:
                    quality_analysis = "Erreur lors de l'analyse de la qualité"
                if not audio_transcription:
                    audio_transcription = "Erreur lors de la transcription audio"
                if not video_resume:
                    video_resume = "Erreur lors de la génération du résumé vidéo"

                # Écrire les résultats dans une ligne du CSV
                writer.writerow({
                    'video_id': video_id,
                    'quality_analysis': quality_analysis,
                    'audio_transcription': audio_transcription,
                    'video_summary': video_resume
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

# Exemple d'utilisation
def create_csv_file(input_dir="Inputs", output_dir="Outputs", output_csv="Outputs/results.csv", language="en"):
    video_files = get_video_files_from_directory(input_dir)
    
    create_csv_output(video_files, output_csv, output_dir, language)

if __name__ == "__main__":
    create_csv_file()
