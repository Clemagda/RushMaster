# TODO: Elements à analyser :


# Detection de bruit dans l'image
# Analyse qualité de l'audio (faible, saturé, bruits de fonds)
# Detection des niveaux sonores
# Detection de bruit ambiant
# Compression vidéo excessive: trop compressé = perte de qualité

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

# TODO: QUALITE DE L'AUDIO

# DETECTION DE BRUIT AMBIANT (DL)

# DETECTION DE COMPRESSION EXCESSIVE
