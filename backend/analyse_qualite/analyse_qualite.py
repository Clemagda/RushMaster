import subprocess
import numpy as np 
import cv2
import librosa 
import moviepy.editor as mp 
import os
from pymediainfo import MediaInfo 
import argparse
import tempfile
from moviepy.editor import VideoFileClip 

###############################
# NETTETE ET DETECTION DE FLOU
###############################

# Descendre vers 80 pour détecter des flous faibles et augmenter vers 150 les flous grossiers
def detect_flou(video_path, seuil_flou=100.0):
    """
    Analyse les proportions de frames floues dans une vidéo et renvoie le résultat.

    Args:
        video_path : chemin d'accès de la vidéo
        seuil_flou (float, optional): Seuil de détection du flou. Paramétrable de 80 à 150. Defaults to 100.0.

    Returns:
        tuple: Boolean (True si floue majoritairement), et pourcentage des frames floues.
    """
    clip = VideoFileClip(video_path)
    total_frames = int(clip.fps * clip.duration)
    frames_floues = 0

    for frame in clip.iter_frames():
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance_laplacienne = cv2.Laplacian(gray, cv2.CV_64F).var()

        if variance_laplacienne < seuil_flou:
            frames_floues += 1

    pourcentage_floues = (frames_floues / total_frames) * 100 if total_frames > 0 else 0
    clip.reader.close()

    return frames_floues > total_frames / 2, pourcentage_floues

########################
# COMPRESSION EXCESSIVE
########################


def get_bitrate(video_path):
    """
    Récupère le bitrate de la vidéo en utilisant MediaInfo.

    Args:
        video_path : chemin de la vidéo

    Returns:
        Bitrate en bits par seconde (bps) ou None si non trouvé.
    """
    # Obtenir les informations sur la vidéo
    media_info = MediaInfo.parse(video_path)
    for track in media_info.tracks:
        if track.track_type == "Video":
            return track.bit_rate

    return None

def get_bitrate_ffmpeg(video_path):
    """
    Utilise ffmpeg pour obtenir le bitrate d'une vidéo.

    Args:
        video_path : chemin de la vidéo

    Returns:
        Bitrate en bits par seconde (bps) ou None si non trouvé.
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", video_path],
            stderr=subprocess.PIPE,
            text=True
        )
        for line in result.stderr.splitlines():
            if "bitrate:" in line:
                bitrate_str = line.split("bitrate:")[1].strip()
                bitrate_value = int(bitrate_str.split(" ")[0])
                return bitrate_value * 1000  # Convertir en bps
    except Exception as e:
        print(f"Erreur lors de l'obtention du bitrate : {str(e)}")
        return None
# =====================================================
# Valeurs de références pour la compression d'une vidéo
# 720p (HD) : 1 500 - 3 000 kbps
# 1080p(Full HD): 3 000 - 6 000 kbps
# 4K(Ultra HD): 8 000 - 15 000 kbps
# ======================================================

def detect_compression_excessive(video_path):
    """
    Détecte si la vidéo est trop compressée en comparant son bitrate avec des seuils de référence selon sa résolution.

    Args:
        video_path : chemin de la vidéo

    Returns:
        Boolean : True si la vidéo est trop compressée, sinon False.
    """
    bitrate = get_bitrate_ffmpeg(video_path)
    width, height = get_resolution(video_path)

    if width is None or height is None:
        return False

    # Déterminer le seuil de bitrate selon la résolution
    if height <= 720:
        seuil_bitrate = 1500  # 1500 kbps pour 720p
    elif height <= 1080:
        seuil_bitrate = 3000  # 3000 kbps pour 1080p
    elif height <= 2160:
        seuil_bitrate = 8000  # 8000 kbps pour 4K
    else:
        return False

    return int(bitrate) > seuil_bitrate * 1000

########################
# SUR et SOUS EXPOSITION
########################


def detect_exposition(video_path, seuil_surexpose=230, seuil_sousexpose=30):
    """
    Détecte si la vidéo est sous-exposée ou surexposée.

    Args:
        video_path (str): Chemin vers la vidéo.
        seuil_surexpose (int): Seuil pour détecter la surexposition (de 0 à 255).
        seuil_sous_expose (int): Seuil pour détecter la sous-exposition (de 0 à 255).

    Returns:
        dict: Pourcentage de frames sous-exposées et surexposées.
    """
    clip = VideoFileClip(video_path)
    total_pixels = 0
    total_frames = 0
    frames_surexposees = 0
    frames_sousexposees = 0

    for frame in clip.iter_frames():
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        total_pixels += gray.size
        total_frames += 1

        # Calcul des pixels surexposés et sous-exposés
        frames_surexposees += np.sum(gray > seuil_surexpose)
        frames_sousexposees += np.sum(gray < seuil_sousexpose)

    if total_frames == 0 or total_pixels == 0:
        return {'pourcentage_surexposees': 0, 'pourcentage_sousexposees': 0}

    # Calculer les pourcentages en divisant par le nombre total de pixels
    pourcentage_surexposees = (frames_surexposees / total_pixels) * 100
    pourcentage_sousexposees = (frames_sousexposees / total_pixels) * 100

    clip.reader.close()

    return {
        'pourcentage_surexposees': pourcentage_surexposees,
        'pourcentage_sousexposees': pourcentage_sousexposees
    }


############
# STABILITE
############


def detect_stabilite(video_path, seuil_stabilite=2.0):
    """
    Détecte la stabilité de la vidéo en analysant l'écart entre les mouvements d'image.

    Args:
        video_path : chemin de la vidéo
        seuil_stabilite : seuil d'écart entre les mouvements pour juger de la stabilité

    Returns:
        Boolean : True si la vidéo est stable, sinon False
    """
    clip = VideoFileClip(video_path)
    prev_gray = None
    stable = True

    for frame in clip.iter_frames():
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            # Calculer l'Optical Flow (Flux optique)
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

            # Si les mouvements sont trop brusques, la vidéo n'est pas stable
            if np.mean(mag) > seuil_stabilite:
                stable = False
                break

        prev_gray = gray

    clip.reader.close()
    return stable

def get_resolution(video_path):
    """
    Récupère la résolution (largeur et hauteur) de la vidéo.

    Args:
        video_path : chemin de la vidéo

    Returns:
        tuple : (largeur, hauteur) de la vidéo ou None si non trouvé
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, None

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap.release()

    return int(width), int(height)
####################
# QUALITE DE L'AUDIO
####################

def check_video_readable(video_path):
    """
    Vérifie que la vidéo peut être lue et que les frames sont accessibles.

    Args:
        video_path (str): Chemin de la vidéo à analyser.

    Returns:
        bool: True si la vidéo peut être lue, sinon False.
    """
    try:
        # Essaye d'ouvrir la vidéo avec MoviePy
        clip = VideoFileClip(video_path)
        clip.reader.close()  # Fermer le lecteur après vérification
        return True
    except Exception as e:
        print(f"Erreur lors de la lecture de la vidéo : {str(e)}")
        return False

def analyser_niveaux_sonores(video_path, seuil_faible=-30.0, seuil_sature=-3.0):
    """
    Analyse les niveaux sonores d'une vidéo et renvoie le pourcentage de frames audio trop faibles ou saturées.

    Args:
        video_path (str): Chemin d'accès à la vidéo.
        seuil_faible (float, optional): Seuil de volume faible en dB. Defaults to -30.0.
        seuil_sature (float, optional): Seuil de saturation en dB. Defaults to -3.0.

    Returns:
        dict: Pourcentage des frames audio trop faibles et saturées.
    """
    # Extraire l'audio de la vidéo
    clip = mp.VideoFileClip(video_path)

    if clip.audio is None:
        return {'error': 'Aucun audio détecté'}

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        audio_path = temp_audio_file.name
    
    try:
        clip.audio.write_audiofile(audio_path)   

    
        # Charger l'audio avec Librosa
        y, sr = librosa.load(audio_path)
   
        # Calculer les niveaux sonores (dB)
        rms = librosa.feature.rms(y=y)
        db = librosa.amplitude_to_db(rms, ref=np.max)

        # Analyser les niveaux faibles ou saturés
        frames_faibles = (db < seuil_faible).sum()
        frames_satures = (db > seuil_sature).sum()

        total_frames = len(db[0])
        pourcentage_faible = (frames_faibles / total_frames) * 100
        pourcentage_sature = (frames_satures / total_frames) * 100

    # Retourner un résumé des résultats sans impressions inutiles
        return {
            'pourcentage_faible': pourcentage_faible,
            'pourcentage_sature': pourcentage_sature,
            'total_frames_audio': total_frames
        }
    except Exception as e:
        return {'error': f"Erreur lors du chargement de l'audio : {str(e)}"}

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)



def run_quality_analysis(video_path, seuil_flou=100.0, seuil_faible=-30.0, seuil_sature=-3.0, seuil_stabilite=2.0, seuil_surexpose=230, seuil_sousexpose=30):
    """
    Effectue une analyse complète de la qualité d'une vidéo en évaluant plusieurs paramètres : flou, stabilité, exposition, compression, et audio.

    Args:
        video_path (str): Chemin vers la vidéo à analyser.
        seuil_flou (float): Seuil de détection du flou (par défaut 100.0, valeurs recommandées entre 80 et 150).
        seuil_faible (float): Seuil de volume faible en dB pour l'analyse audio (par défaut -30.0 dB).
        seuil_sature (float): Seuil de saturation audio en dB pour l'analyse audio (par défaut -3.0 dB).
        seuil_stabilite (float): Seuil de détection de la stabilité basé sur les flux optiques (par défaut 2.0).
        seuil_surexpose (int): Seuil de détection de la surexposition en intensité (par défaut 230).
        seuil_sousexpose (int): Seuil de détection de la sous-exposition en intensité (par défaut 30).

    Raises:
        FileNotFoundError: Si la vidéo spécifiée est introuvable ou ne peut pas être lue.
        ValueError: Si une erreur se produit lors de l'analyse des paramètres de qualité.

    Returns:
        None: La fonction affiche les résultats de chaque analyse (flou, stabilité, exposition, compression, et audio) dans la console, mais ne retourne pas de valeur.

    Steps:
        1. Vérifie que la vidéo est lisible.
        2. Analyse le pourcentage de frames floues et détermine si la vidéo est floue selon le seuil fourni.
        3. Évalue la stabilité de la vidéo en fonction du seuil de stabilité.
        4. Analyse l'exposition de la vidéo et affiche les pourcentages de frames surexposées et sous-exposées.
        5. Vérifie si la vidéo présente une compression excessive.
        6. Analyse les niveaux sonores de la vidéo pour déterminer les pourcentages de frames ayant un audio trop faible ou saturé.

    Example:
        run_quality_analysis("video.mp4", seuil_flou=120.0, seuil_faible=-25.0, seuil_stabilite=1.5)
    """
    # Vérification que la vidéo peut être lue
    if not check_video_readable(video_path):
        return  # Arrête le script si la vidéo ne peut pas être lue

    # Analyse du flou
    print("\n=== Analyse du flou ===")
    resultat_flou, pourcentage_flou = detect_flou(video_path, seuil_flou=seuil_flou)
    print(f"Résultat : {'Flou' if resultat_flou else 'Non flou'}, {pourcentage_flou:.2f}% des frames floues.")

    # Analyse de la stabilité
    print("\n=== Analyse de la stabilité ===")
    resultat_stabilite = detect_stabilite(video_path, seuil_stabilite=seuil_stabilite)
    print(f"Vidéo stable : {'Oui' if resultat_stabilite else 'Non'}.")

    # Analyse de l'exposition
    print("\n=== Analyse de l'exposition ===")
    resultats_exposition = detect_exposition(video_path, seuil_surexpose=seuil_surexpose, seuil_sousexpose=seuil_sousexpose)
    if 'error' in resultats_exposition:
        print(resultats_exposition['error'])
    else:
        print(f"Frames surexposées : {resultats_exposition['pourcentage_surexposees']:.2f}%")
        print(f"Frames sous-exposées : {resultats_exposition['pourcentage_sousexposees']:.2f}%")

    # Analyse de la compression
    print("\n=== Analyse de la compression ===")
    resultat_compression = detect_compression_excessive(video_path)
    print(f"Vidéo trop compressée : {'Oui' if resultat_compression else 'Non'}.")

    # Analyse de l'audio
    print("\n=== Analyse des niveaux sonores ===")
    resultats_audio = analyser_niveaux_sonores(video_path, seuil_faible=seuil_faible, seuil_sature=seuil_sature)
    if 'error' in resultats_audio:
        print(resultats_audio['error'])
        audio_results=None
    
    else:
        print(f"Frames audio faibles : {resultats_audio['pourcentage_faible']:.2f}%")
        print(f"Frames audio saturées : {resultats_audio['pourcentage_sature']:.2f}%")
        audio_results = {
            "pourcentage_faible": resultats_audio['pourcentage_faible'],
            "pourcentage_sature": resultats_audio['pourcentage_sature']
        }
        
    return {
        "Flou": 'Floue' if resultat_flou else 'Non flou',
        "Pourcentage_flou": pourcentage_flou,
        "Stabilite": 'Stable' if resultat_stabilite else 'Instable',
        "Frames_surexposees": resultats_exposition.get('pourcentage_surexposees', None),
        "Frames_sousexposees": resultats_exposition.get('pourcentage_sousexposees', None),
        "Compression": 'Excessive' if resultat_compression else 'OK',
        "Audio": audio_results
    }

def parse_args():
    """
    Parse les arguments de la ligne de commande.
    """   
    parser = argparse.ArgumentParser(description="Analyse complète de la qualité d'une vidéo")
    parser.add_argument("--video_path", type=str, required=True, help="Chemin vers la vidéo à analyser")
    parser.add_argument("--seuil_flou", type=float, default=100.0, help="Seuil de détection du flou (80 à 150)")
    parser.add_argument("--seuil_faible", type=float, default=-30.0, help="Seuil de volume faible en dB")
    parser.add_argument("--seuil_sature", type=float, default=-3.0, help="Seuil de saturation en dB")
    parser.add_argument("--seuil_stabilite", type=float, default=2.0, help="Seuil de détection de la stabilité (moyenne des flux optiques)")
    parser.add_argument("--seuil_surexpose", type=int, default=230, help="Seuil pour la surexposition")
    parser.add_argument("--seuil_sousexpose", type=int, default=30, help="Seuil pour la sous-exposition")
    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()
    run_quality_analysis(
        args.video_path,
        args.seuil_flou,
        args.seuil_faible,
        args.seuil_sature,
        args.seuil_stabilite,
        args.seuil_surexpose,
        args.seuil_sousexpose
    )