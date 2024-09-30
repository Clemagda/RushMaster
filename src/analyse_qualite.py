# TODO: Elements à analyser :
# Netteté et détection de flou
# Sur et sous exposition (histogramme de luminosité)
# Stabilité et mouvements
# Detection de bruit
# Analyse qualité de l'audio (faible, saturé, bruits de fonds)
# Detection des niveaux sonores
# Detection de bruit ambiant
# Compression vidéo excessive: trop compressé = perte de qualité

import numpy as np
import cv2

#########################################
TODO:  # NETTETE ET DETECTION DE FLOU
    ##########################################

    # Descencdre vers 80 pour détecter des flous faibles et augmenter vers 150 les flous grossiers


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

##########################
# SUR et SOUS EXPOSITION
##########################


# STABILITE ET MOUVEMENTS (YOLOv5 ? )

# QUALITE DE L'AUDIO

# DETECTION DE BRUIT AMBIANT (DL)

# DETECTION DE COMPRESSION EXCESSIVE
