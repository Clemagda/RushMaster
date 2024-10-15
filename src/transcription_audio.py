import os
import wave
import argparse
from vosk import Model, KaldiRecognizer
import subprocess
from moviepy.editor import VideoFileClip


# Fonction pour extraire l'audio d'une vidéo
def extract_audio_from_video(video_path, audio_output_path):
    """
    Extrait l'audio d'une vidéo et le sauvegarde sous forme de fichier WAV.
    
    Args:
        video_path (str): Chemin vers la vidéo.
        audio_output_path (str): Chemin pour sauvegarder l'audio extrait.
    """
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_output_path, codec='pcm_s16le')

def convert_audio_to_mono(audio_input_path, audio_output_path):
    """
    Convertit un fichier audio en format WAV avec 1 canal (mono) et 16-bit PCM.
    
    Args:
        audio_input_path (str): Chemin du fichier audio d'entrée.
        audio_output_path (str): Chemin pour sauvegarder l'audio converti.
    """
    command = [
        "ffmpeg", "-i", audio_input_path,
        "-ac", "1",  # Convertir en mono
        "-ar", "16000",  # Taux d'échantillonnage recommandé par Vosk (16 kHz)
        "-sample_fmt", "s16",  # 16-bit PCM
        audio_output_path
    ]
    subprocess.run(command, check=True)

# Fonction pour transcrire l'audio en texte avec Vosk
def transcribe_audio(audio_path, vosk_model_path):
    """
    Transcrit un fichier audio en texte en utilisant Vosk.
    
    Args:
        audio_path (str): Chemin vers le fichier audio (WAV).
        vosk_model_path (str): Chemin vers le modèle Vosk.
    
    Returns:
        str: Transcription textuelle de l'audio.
    """
    # Charger le modèle Vosk
    model = Model(vosk_model_path)
    
    # Ouvrir l'audio en mode lecture
    wf = wave.open(audio_path, "rb")
    
    # Vérifier que le fichier est au format 16-bit PCM
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

def get_vosk_model_path(language):
    """
    Sélectionne le chemin du modèle Vosk en fonction de la langue choisie.
    
    Args:
        language (str): Langue choisie ('fr' pour français, 'en' pour anglais).
    
    Returns:
        str: Chemin vers le modèle Vosk correspondant.
    """
    if language == 'fr':
        # Modèle pour le français
        return "Vosk/fr/vosk-model-small-fr-0.22"
    elif language == 'en':
        # Modèle pour l'anglais
        return "Vosk/en/vosk-model-small-en-us-0.15"
    else:
        raise ValueError("Langue non supportée. Choisissez 'fr' pour français ou 'en' pour anglais.")

# Fonction principale pour gérer l'extraction et la transcription
def main():
    parser = argparse.ArgumentParser(description="Transcription audio d'une vidéo avec Vosk")
    parser.add_argument("--video_path", type=str, required=True, help="Chemin vers la vidéo à transcrire")
    parser.add_argument("--output_dir", type=str, default=".", help="Répertoire pour sauvegarder la transcription")
    parser.add_argument("--language", type=str, required=True, choices=['fr', 'en'], help="Langue de la vidéo ('fr' pour français, 'en' pour anglais)")
    parser.add_argument("--output_name", type=str, required=True, help="Nom du fichier de transcription")

    args = parser.parse_args()

    vosk_model_path = get_vosk_model_path(args.language)

    # Chemin pour sauvegarder l'audio extrait
    audio_output_path = os.path.join(args.output_dir, "audio_extracted.wav")
    audio_converted_path = os.path.join(args.output_dir, "audio_converted.wav")
    
    # Extraire l'audio de la vidéo
    print("Extraction de l'audio de la vidéo...")
    extract_audio_from_video(args.video_path, audio_output_path)

    # Convertir l'audio en mono et 16-bit PCM
    print("Conversion de l'audio en mono et 16-bit PCM...")
    convert_audio_to_mono(audio_output_path, audio_converted_path)

    # Transcrire l'audio extrait
    print("Transcription de l'audio en cours...")
    transcription = transcribe_audio(audio_converted_path, vosk_model_path)

    # Afficher la transcription dans la console
    print(f"Transcription :\n{transcription}")

    # Sauvegarder la transcription dans un fichier texte
    output_path = os.path.join(args.output_dir, f"{args.output_name}.txt")
    with open(output_path, "w") as f:
        f.write(transcription)
    
    print(f"Transcription sauvegardée dans : {output_path}")

if __name__ == "__main__":
    main()
