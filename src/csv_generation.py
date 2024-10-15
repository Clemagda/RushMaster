import csv
import os
from analyse_qualite import run_quality_analysis  # Import de la fonction d'analyse de la qualité
from generation_resume import run_inference  # Import de la fonction de génération de résumé
from transcription_audio import transcribe_audio  # Import de la fonction de transcription audio

def create_csv_output(video_files, output_csv, output_dir, language="en"):
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
        fieldnames = ['video_id', 'quality_analysis', 'audio_transcription', 'video_resume']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Écrire les en-têtes
        writer.writeheader()

        # Parcourir chaque fichier vidéo
        for video in video_files:
            video_id = os.path.basename(video).split('.')[0]  # Utiliser le nom du fichier sans extension

            # Appeler les fonctions des scripts individuels
            quality_analysis = run_quality_analysis(video)  # Appel de l'analyse de la qualité
            audio_transcription = transcribe_audio(video, language)  # Appel de la transcription audio
            video_resume = run_inference(video, output_dir, video_id)  # Appel de la génération de résumés

            # Écrire les résultats dans une ligne du CSV
            writer.writerow({
                'video_id': video_id,
                'quality_analysis': quality_analysis,
                'audio_transcription': audio_transcription,
                'video_resume': video_resume
            })

    print(f"Les résultats ont été fusionnés et sauvegardés dans : {output_csv}")

# Exemple d'utilisation
def main():
    video_files = [
        "/path/to/video1.mp4",
        "/path/to/video2.mp4",
        "/path/to/video3.mp4"
    ]

    # Chemin du fichier CSV de sortie
    output_csv = "Outputs/results.csv"
    output_dir = "Outputs"

    # Langue pour la transcription ('fr' pour français, 'en' pour anglais)
    language = "en"

    # Créer le fichier CSV de sortie
    create_csv_output(video_files, output_csv, output_dir, language)

if __name__ == "__main__":
    main()
