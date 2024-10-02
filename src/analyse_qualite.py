# TODO: Créer tests automatisés pour vérifier fonctionnement du script. Et si possible ajouter workflow github avant de passer au script d'anallyse des doublons.


import cv2
import numpy as np
import librosa
import moviepy.editor as mp
import os
from pymediainfo import MediaInfo

video_path_audio = "Data/KoNViD_1k_videos/3359662128.mp4"
video_path = "Data/KoNViD_1k_videos/3339962845_floue.mp4"


###############################
# NETTETE ET DETECTION DE FLOU
###############################

# Descendre vers 80 pour détecter des flous faibles et augmenter vers 150 les flous grossiers
def detect_flou(video_path, seuil_flou=100.0):
    """
    Analyse les proportions de frames floues dans une vidéo et renvoie le résultat.

    Args:
        video_path : chemin d'accès de la video
        seuil_flou (float, optional): Seuil de détection du flou. Paramétrable de 80 à 150. Defaults to 100.0.

    Returns:
        tuple: Boolean (True si floue majoritairement), et pourcentage des frames floues.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, 0

    total_frames = 0
    frames_floues = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance_laplacienne = cv2.Laplacian(gray, cv2.CV_64F).var()

        if variance_laplacienne < seuil_flou:
            frames_floues += 1

    pourcentage_floues = (frames_floues / total_frames) * \
        100 if total_frames > 0 else 0
    cap.release()

    return frames_floues > total_frames/2, pourcentage_floues

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

# =====================================================
# Valeurs de références pour la compression d'une vidéo
# 720p (HD) : 1 500 - 3 000 kbps
# 1080p(Full HD): 3 000 - 6 000 kbps
# 4K(Ultra HD): 8 000 - 15 000 kbps
# ======================================================


def get_resolution(video_path):
    """
    Récupère la résolution de la vidéo.

    Args:
        video_path : chemin de la vidéo

    Returns:
        Tuple (width, height) ou (None, None) si non trouvé.
    """
    media_info = MediaInfo.parse(video_path)
    for track in media_info.tracks:
        if track.track_type == "Video":
            return track.width, track.height
    return None, None


def detect_compression_excessive(video_path):
    """
    Détecte si la vidéo est trop compressée en comparant son bitrate avec des seuils de référence selon sa résolution.

    Args:
        video_path : chemin de la vidéo

    Returns:
        Boolean : True si la vidéo est trop compressée, sinon False.
    """
    bitrate = get_bitrate(video_path)
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


def detect_exposition(video_path, seuil_concentration=70):
    """
    Détecte les frames sous- et surexposées dans une vidéo en fonction de la concentration
    des pixels dans les parties sombres et claires de l'histogramme.

    Args:
        video_path (str): Chemin d'accès de la vidéo.
        seuil_concentration (int, optional): Seuil de concentration pour déclencher une alerte d'exposition. Defaults to 70.

    Returns:
        dict: Pourcentage de frames sous-exposées et surexposées, avec le total des frames.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {'error': "Impossible de lire la vidéo."}

    total_frames = 0
    frames_sous_exposees = 0
    frames_surexposees = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Fin de la vidéo

        total_frames += 1

        # Convertir la frame en niveaux de gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculer l'histogramme des niveaux de gris (256 bins pour les valeurs de 0 à 255)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

        # Normaliser l'histogramme
        hist /= hist.sum()

        # Concentration des pixels dans les 10% inférieurs (pour sous-exposition)
        sous_exposition = hist[:25].sum() * 100  # Premier 10% des valeurs
        # Concentration des pixels dans les 10% supérieurs (pour surexposition)
        surexposition = hist[230:].sum() * 100  # Dernier 10% des valeurs

        # Vérifier la concentration
        if sous_exposition > seuil_concentration:
            frames_sous_exposees += 1
        elif surexposition > seuil_concentration:
            frames_surexposees += 1

    pourcentage_sous_exposees = (
        frames_sous_exposees / total_frames) * 100 if total_frames > 0 else 0
    pourcentage_surexposees = (
        frames_surexposees / total_frames) * 100 if total_frames > 0 else 0

    cap.release()

    # Retourner les résultats sans impressions inutiles
    return {
        'pourcentage_sous_exposees': pourcentage_sous_exposees,
        'pourcentage_surexposees': pourcentage_surexposees,
        'total_frames': total_frames
    }


############
# STABILITE
############


def detect_stabilite(video_path, seuil_mouvement=2.0):
    """
     Détecte si la vidéo est instable en utilisant l'Optical Flow pour repérer les mouvements brusques.

     Args:
         video_path : chemin de la vidéo
         seuil_mouvement (float, optional): Seuil pour la détection de mouvements brusques. Defaults to 2.0.

     Returns:
         tuple: Boolean (True si instable majoritairement), et pourcentage de frames instables.
     """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, 0

    ret, prev_frame = cap.read()
    if not ret:
        return None, 0

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    total_frames = 0
    frames_instables = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        magnitude_mean = np.mean(magnitude)

        if magnitude_mean > seuil_mouvement:
            frames_instables += 1

        prev_gray = gray

    pourcentage_instables = (
        frames_instables / total_frames) * 100 if total_frames > 0 else 0
    cap.release()

    return frames_instables > total_frames/2, pourcentage_instables

####################
# QUALITE DE L'AUDIO
####################


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
    audio_path = "temp_audio.wav"

    if clip.audio is None:
        return {'error': 'Aucun audio détecté'}

    # Extraire l'audio en fichier WAV
    clip.audio.write_audiofile(audio_path)

    try:
        # Charger l'audio avec Librosa
        y, sr = librosa.load(audio_path)
    except Exception as e:
        return {'error': f"Erreur lors du chargement de l'audio : {str(e)}"}
    finally:
        # Supprimer le fichier audio temporaire après l'analyse
        if os.path.exists(audio_path):
            os.remove(audio_path)

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
