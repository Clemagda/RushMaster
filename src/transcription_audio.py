import os
import wave
import argparse
from vosk import Model, KaldiRecognizer
from moviepy.editor import VideoFileClip
import subprocess
import tempfile
import logging

logging.getLogger('vosk').setLevel(logging.ERROR)

# Fonction pour extraire l'audio d'une vidéo dans un fichier temporaire
def extract_audio_from_video(video_path):
    """
    Extrait l'audio d'une vidéo et retourne le chemin vers un fichier audio temporaire.
    
    Args:
        video_path (str): Chemin vers la vidéo.
    
    Returns:
        str: Chemin vers le fichier temporaire contenant l'audio extrait.
    """
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_output_path = temp_audio_file.name
    temp_audio_file.close()

    # Extraction de l'audio avec MoviePy
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_output_path, codec='pcm_s16le')

    return audio_output_path

# Fonction pour convertir l'audio en mono et 16-bit PCM dans un fichier temporaire
def convert_audio_to_mono(audio_input_path):
    """
    Convertit un fichier audio en mono et 16-bit PCM, en utilisant un fichier temporaire.
    
    Args:
        audio_input_path (str): Chemin du fichier audio extrait.
    
    Returns:
        str: Chemin vers le fichier audio temporaire converti en mono et 16-bit PCM.
    """
    temp_audio_converted = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_converted_path = temp_audio_converted.name
    temp_audio_converted.close()

    # Conversion avec ffmpeg
    command = [
        "ffmpeg", "-y",  # Ecraser le fichier s'il existe déjà
        "-i", audio_input_path,
        "-ac", "1",  # Convertir en mono
        "-ar", "16000",  # Taux d'échantillonnage recommandé par Vosk (16 kHz)
        "-sample_fmt", "s16",  # 16-bit PCM
        audio_converted_path
    ]
    subprocess.run(command, check=True)

    return audio_converted_path

# Fonction pour transcrire l'audio en texte avec Vosk
def transcribe_audio(audio_path, vosk_model_path):
    """
    Transcrit un fichier audio en texte en utilisant Vosk.
    
    Args:
        audio_path (str): Chemin vers le fichier audio converti (WAV).
        vosk_model_path (str): Chemin vers le modèle Vosk.
    
    Returns:
        str: Transcription textuelle de l'audio.
    """
    # Charger le modèle Vosk
    model = Model(vosk_model_path)
    
    # Ouvrir l'audio en mode lecture
    wf = wave.open(audio_path, "rb")
    
    # Vérifier que le fichier est au format 16-bit PCM et mono
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise ValueError("Le fichier audio doit être en format WAV avec 1 canal (mono) et 16-bit PCM.")

    # Initialiser Vosk avec le modèle et le taux d'échantillonnage
    recognizer = KaldiRecognizer(model, wf.getframerate())

    transcription = []
    
    # Lire les frames de l'audio et transcrire
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            transcription.append(result)
        else:
            recognizer.PartialResult()

    wf.close()

    # Retourner la transcription complète
    return ' '.join(transcription)



# Fonction principale pour gérer l'extraction, conversion et transcription
def run_transcription(video_path, language='en', output_dir="Outputs", output_name="audio_transcripted"):   
    """
    Fonction principale pour gérer l'extraction, la conversion et la transcription de l'audio d'une vidéo.

    Cette fonction prend en entrée un fichier vidéo, extrait l'audio, le convertit en un format compatible 
    (mono et 16-bit PCM), puis effectue la transcription de l'audio en utilisant un modèle Vosk spécifique à la langue.
    La transcription est ensuite sauvegardée dans un fichier texte.

    Args:
        video_path (str): Le chemin vers le fichier vidéo à traiter.
        language (str): La langue utilisée pour la transcription. Par défaut 'en' (anglais).
                        Utilise 'fr' pour le français ou toute autre langue supportée par le modèle Vosk.
        output_dir (str): Le répertoire où sauvegarder le fichier texte contenant la transcription. 
                          Par défaut "Outputs".
        output_name (str): Le nom du fichier de sortie (sans extension) qui contiendra la transcription.
                           Par défaut "audio_transcripted".
    
    Raises:
        FileNotFoundError: Si le fichier vidéo ou le modèle Vosk pour la langue sélectionnée est introuvable.
        Exception: Pour toute erreur durant l'extraction, la conversion ou la transcription de l'audio.
    
    Returns:
        None: La fonction affiche et sauvegarde la transcription, mais ne retourne pas de valeur.

    Steps:
        1. Sélectionne le modèle Vosk approprié en fonction de la langue.
        2. Extrait l'audio du fichier vidéo et le sauvegarde temporairement.
        3. Convertit l'audio extrait en mono et en 16-bit PCM.
        4. Transcrit l'audio converti en texte.
        5. Affiche la transcription dans la console.
        6. Sauvegarde la transcription dans un fichier texte situé dans `output_dir` avec le nom `output_name.txt`.

    Example:
        run_transcription("video.mp4", language='fr', output_dir="Transcriptions", output_name="video1_transcript")
    """
    # Sélectionner le modèle Vosk en fonction de la langue
    print("#=== Transcription audio...===")
    vosk_model_path = get_vosk_model_path(language)

    try:
        # Extraire l'audio de la vidéo dans un fichier temporaire
        print("Extraction de l'audio de la vidéo...")
        audio_output_path = extract_audio_from_video(video_path)

        # Convertir l'audio en mono et 16-bit PCM dans un fichier temporaire
        print("Conversion de l'audio en mono et 16-bit PCM...")
        audio_converted_path = convert_audio_to_mono(audio_output_path)

        # Transcrire l'audio converti
        print("Transcription de l'audio en cours...")
        transcription = transcribe_audio(audio_converted_path, vosk_model_path)

        # Afficher la transcription dans la console
        print(f"Transcription :\n{transcription}")

        # Sauvegarder la transcription dans un fichier texte
        output_path = os.path.join(output_dir, f"{output_name}.txt")
        with open(output_path, "w") as f:
            f.write(transcription)
        
        print(f"Transcription sauvegardée dans : {output_path}")

    finally:
        # Supprimer les fichiers temporaires après usage
        if os.path.exists(audio_output_path):
            os.remove(audio_output_path)
        if os.path.exists(audio_converted_path):
            os.remove(audio_converted_path)
    return {"transcript": transcription, "transcription_path":output_path}

# Fonction pour choisir le modèle Vosk en fonction de la langue
def get_vosk_model_path(language):
    if language == 'fr':
        return "Vosk/fr/vosk-model-small-fr-0.22/"
    elif language == 'en':
        return "Vosk/en/vosk-model-small-en-us-0.15/"
    else:
        raise ValueError("Langue non supportée. Choisissez 'fr' pour français ou 'en' pour anglais.")

def parse_args():
    parser = argparse.ArgumentParser(description="Transcription audio d'une vidéo avec Vosk")
    parser.add_argument("--video_path", type=str, required=True, help="Chemin vers la vidéo à transcrire")
    parser.add_argument("--language", type=str, required=True, choices=['fr', 'en'],default='en', help="Langue de la vidéo ('fr' pour français, 'en' pour anglais)")
    parser.add_argument("--output_dir", type=str, default="Outputs", help="Répertoire pour sauvegarder la transcription")
    parser.add_argument("--output_name", type=str, required=True, help="Nom du fichier de transcription")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_transcription(args.video_path,
                      args.language,
                      args.output_dir,
                      args.output_name)
