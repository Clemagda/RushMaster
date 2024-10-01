# TODO: Elements à analyser :

# Analyse qualité de l'audio (faible, saturé, bruits de fonds)
# Detection des niveaux sonores
# Detection de bruit ambiant
# Compression vidéo excessive: trop compressé = perte de qualité

from pymediainfo import MediaInfo
import moviepy.editor as mp
import librosa
import numpy as np
import cv2

###############################
# NETTETE ET DETECTION DE FLOU
###############################

# Descendre vers 80 pour détecter des flous faibles et augmenter vers 150 les flous grossiers


def detect_flou(video_path, seuil_flou=100.0):
    """Analyse les proportions de frames floues dans une vidéo et tag la vidéo si elle est majoritairement floue ou non.

    Args:
        video_path : chemin d'accès de la video 
        seuil_flou (float, optional): Seuil de détection du flou. Paramétrable de 80 à 150. 80 étant une detection stricte et 150 une detection grossière.  . Defaults to 100.0.

    Returns:
        tuple: True or False depending of the blurring with the proportion of blurred frames. 

    """
    # Ouvrir la vidéo avec OpenCV
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : Impossible de lire la vidéo.")
        return

    total_frames = 0
    frames_floues = 0

    while True:
        # Lire frame par frame
        ret, frame = cap.read()
        if not ret:
            break  # Fin de la vidéo

        total_frames += 1

        # Convertir en niveaux de gris pour l'analyse
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Appliquer la variance de la Laplacienne
        variance_laplacienne = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Si la variance est inférieure au seuil, la frame est considérée comme floue
        if variance_laplacienne < seuil_flou:
            frames_floues += 1

    # Calculer le pourcentage de frames floues
    pourcentage_floues = (frames_floues / total_frames) * \
        100 if total_frames > 0 else 0

    # Résultat global : la vidéo est-elle majoritairement floue ?
    video_majoritairement_floue = pourcentage_floues > 50

    # Afficher ou enregistrer le résultat
    print(f"Vidéo : {video_path}")
    print(f"Total frames : {total_frames}")
    print(
        f"Frames floues : {frames_floues} ({pourcentage_floues:.2f}% floues)")
    print(
        f"Vidéo majoritairement floue : {'Oui' if video_majoritairement_floue else 'Non'}")

    # Libérer les ressources
    cap.release()

    return video_majoritairement_floue, pourcentage_floues


# Exemple d'utilisation
video_path = "Data/KoNViD_1k_videos/3339962845_floue.mp4"
detect_flou(video_path, seuil_flou=100.0)

########################
# SUR et SOUS EXPOSITION
########################


def detect_exposition(video_path, seuil_concentration=70):
    """Detecte les défauts de sur et sous exposition. La fonction analyse la concentration de l'histogramme des valeurs de niveaux de gris des pixels et décide si l'exposition est déséquilibrée en fonction d'un seuil de detection défini.

    Args:
        video_path (_type_): chemin d'accès du fichier
        seuil_concentration (int, optional): seuil de concentration pour déterminer l'anomalie. Defaults to 70.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : Impossible de lire la vidéo.")
        return

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
        hist = hist / hist.sum()

        # Concentration des pixels dans les 10% inférieurs (pour sous-exposition)
        sous_exposition = hist[:25].sum() * 100  # Premier 10% des valeurs
        # Concentration des pixels dans les 10% supérieurs (pour surexposition)
        surexposition = hist[230:].sum() * 100  # Dernier 10% des valeurs

        # Vérifier la concentration
        if sous_exposition > seuil_concentration:
            frames_sous_exposees += 1
        elif surexposition > seuil_concentration:
            frames_surexposees += 1

    # Calculer les pourcentages de frames sous/surexposées
    pourcentage_sous_exposees = (
        frames_sous_exposees / total_frames) * 100 if total_frames > 0 else 0
    pourcentage_surexposees = (
        frames_surexposees / total_frames) * 100 if total_frames > 0 else 0

    print(f"Vidéo : {video_path}")
    print(f"Total frames : {total_frames}")
    print(
        f"Frames sous-exposées : {frames_sous_exposees} ({pourcentage_sous_exposees:.2f}%)")
    print(
        f"Frames surexposées : {frames_surexposees} ({pourcentage_surexposees:.2f}%)")

    cap.release()


detect_exposition(video_path, seuil_concentration=70)

############
# STABILITE
############


def detect_stabilite(video_path, seuil_mouvement=2.0):
    """Detecte la stabilité globale d'une vidéo

    Args:
        video_path (_type_): chemin d'accès au fichier
        seuil_mouvement (float, optional): Sensibilité de la détection de tremblements. un seuil bas entraîne une détection plus stricte. Defaults to 2.0. 
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : Impossible de lire la vidéo.")
        return

    ret, prev_frame = cap.read()
    if not ret:
        print("Erreur : Impossible de lire la première frame.")
        return

    # Convertir la première frame en niveaux de gris
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    total_frames = 0
    frames_instables = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1

        # Convertir la frame actuelle en niveaux de gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculer l'optical flow entre la frame précédente et la frame actuelle
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Calculer la magnitude des vecteurs de déplacement (intensité du mouvement)
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Calculer la magnitude moyenne pour voir si les mouvements sont importants
        magnitude_mean = np.mean(magnitude)

        # Si la magnitude moyenne dépasse un seuil, la frame est considérée comme instable
        if magnitude_mean > seuil_mouvement:
            frames_instables += 1

        # La frame actuelle devient la précédente pour la prochaine itération
        prev_gray = gray

    # Calculer le pourcentage de frames instables
    pourcentage_instables = (
        frames_instables / total_frames) * 100 if total_frames > 0 else 0
    video_instable = pourcentage_instables > 50

    print(f"Vidéo : {video_path}")
    print(f"Total frames : {total_frames}")
    print(
        f"Frames instables : {frames_instables} ({pourcentage_instables:.2f}% instables)")
    print(f" Video instable : {'Oui' if video_instable else 'Non'}")

    cap.release()


# Exemple d'utilisation
video_path = "Data/KoNViD_1k_videos/3321308714.mp4"
detect_stabilite(video_path, seuil_mouvement=0.5)

# QUALITE DE L'AUDIO
video_path_audio = "Data/KoNViD_1k_videos/3359662128.mp4"

# Analyse des niveaux sonores


def analyser_niveaux_sonores(video_path, seuil_faible=-30.0, seuil_sature=-3.0):
    # Extraire l'audio de la vidéo
    clip = mp.VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    if audio_path is None:
        print('Aucun audio détecté')
    else:
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

        print(f"Vidéo : {video_path}")
        print(f"Total frames audio : {total_frames}")
        print(f"Frames audio trop faibles : {pourcentage_faible:.2f}%")
        print(f"Frames audio saturées : {pourcentage_sature:.2f}%")


# Exemple d'utilisation
analyser_niveaux_sonores(
    video_path_audio, seuil_faible=-30.0, seuil_sature=-3.0)


# FIXME: DETECTION DE COMPRESSION EXCESSIVE

# Extraction du bitrate de la vidéo


def get_bitrate_mediainfo(video_path):
    # Obtenir les informations sur la vidéo
    media_info = MediaInfo.parse(video_path)

    # Parcourir les pistes pour trouver la piste vidéo
    for track in media_info.tracks:
        if track.track_type == "Video":
            return track.bit_rate  # Retourne le bitrate en bits par seconde

    return "Bitrate non trouvé"


# Exemple d'utilisation

bitrate = get_bitrate_mediainfo(video_path)
print(f"Bitrate de la vidéo : {bitrate} bps")

# =====================================================
# Valeurs de références pour la compression d'une vidéo
# 720p (HD) : 1 500 - 3 000 kbps
# 1080p(Full HD): 3 000 - 6 000 kbps
# 4K(Ultra HD): 8 000 - 15 000 kbps
# ======================================================


def get_resolution(video_path):
    media_info = MediaInfo.parse(video_path)
    for track in media_info.tracks:
        if track.track_type == "Video":
            return track.width, track.height
    return None, None


def detect_compression_excessive(video_path):
    # Obtenir le bitrate
    bitrate = get_bitrate_mediainfo(video_path)

    # Obtenir la résolution
    width, height = get_resolution(video_path)

    if width is None or height is None:
        print("Impossible de déterminer la résolution de la vidéo.")
        return

    # Déterminer le seuil de bitrate selon la résolution
    if height <= 720:
        seuil_bitrate = 1500  # 1500 kbps pour 720p
    elif height <= 1080:
        seuil_bitrate = 3000  # 3000 kbps pour 1080p
    elif height <= 2160:
        seuil_bitrate = 8000  # 8000 kbps pour 4K
    else:
        print("Résolution non prise en charge.")
        return

    # Comparer le bitrate avec le seuil
    # Convertir kbps en bps pour comparaison
    if bitrate and int(bitrate) < seuil_bitrate * 1000:
        print(
            f"Compression excessive détectée : Bitrate {bitrate} bps trop faible pour {height}p.")
    else:
        print(
            f"La compression semble correcte : Bitrate {bitrate} bps pour {height}p.")

# Exemple d'utilisation


detect_compression_excessive(video_path)
