import os
import wave
import argparse
from vosk import Model, KaldiRecognizer
from moviepy.editor import VideoFileClip
import subprocess
import tempfile

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
def main():
    parser = argparse.ArgumentParser(description="Transcription audio d'une vidéo avec Vosk")
    parser.add_argument("--video_path", type=str, required=True, help="Chemin vers la vidéo à transcrire")
    parser.add_argument("--language", type=str, required=True, choices=['fr', 'en'], help="Langue de la vidéo ('fr' pour français, 'en' pour anglais)")
    parser.add_argument("--output_dir", type=str, default="Outputs", help="Répertoire pour sauvegarder la transcription")
    parser.add_argument("--output_name", type=str, required=True, help="Nom du fichier de transcription")

    args = parser.parse_args()

    # Sélectionner le modèle Vosk en fonction de la langue
    vosk_model_path = get_vosk_model_path(args.language)

    try:
        # Extraire l'audio de la vidéo dans un fichier temporaire
        print("Extraction de l'audio de la vidéo...")
        audio_output_path = extract_audio_from_video(args.video_path)

        # Convertir l'audio en mono et 16-bit PCM dans un fichier temporaire
        print("Conversion de l'audio en mono et 16-bit PCM...")
        audio_converted_path = convert_audio_to_mono(audio_output_path)

        # Transcrire l'audio converti
        print("Transcription de l'audio en cours...")
        transcription = transcribe_audio(audio_converted_path, vosk_model_path)

        # Afficher la transcription dans la console
        print(f"Transcription :\n{transcription}")

        # Sauvegarder la transcription dans un fichier texte
        output_path = os.path.join(args.output_dir, f"{args.output_name}.txt")
        with open(output_path, "w") as f:
            f.write(transcription)
        
        print(f"Transcription sauvegardée dans : {output_path}")

    finally:
        # Supprimer les fichiers temporaires après usage
        if os.path.exists(audio_output_path):
            os.remove(audio_output_path)
        if os.path.exists(audio_converted_path):
            os.remove(audio_converted_path)

# Fonction pour choisir le modèle Vosk en fonction de la langue
def get_vosk_model_path(language):
    if language == 'fr':
        return "Vosk/fr/vosk-model-small-fr-0.22/"
    elif language == 'en':
        return "Vosk/en/vosk-model-small-en-us-0.15/"
    else:
        raise ValueError("Langue non supportée. Choisissez 'fr' pour français ou 'en' pour anglais.")

if __name__ == "__main__":
    main()
