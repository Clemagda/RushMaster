import os
import subprocess
import cv2
import requests
import argparse


def preprocess_video(input_path, user_id, base_output_dir="/app/shared/processed", target_resolution=(336, 336)):
    """
    Pré-traite une seule vidéo en redimensionnant si nécessaire.
    """
    user_output_dir = os.path.join(base_output_dir, user_id)
    if not os.path.exists(user_output_dir):
        os.makedirs(user_output_dir)
    video_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(user_output_dir, f"processed_{video_name}.mp4")

    # Lire la vidéo avec OpenCV
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Original resolution: {width}x{height}")

    # Vérifier si un redimensionnement est nécessaire
    if (width, height) != target_resolution:
        print(
            f"Redimensionnement de la vidéo à {target_resolution[0]}x{target_resolution[1]}")
        cmd = [
            'ffmpeg', '-y', '-loglevel', 'panic', '-i', input_path, '-vf',
            f'scale={target_resolution[0]}:trunc(ow/a/2)*2',
            output_path
        ]
        subprocess.run(cmd)
    else:
        print("Pas de redimensionnement nécessaire, la vidéo est déjà à la bonne taille.")
        cmd = ['cp', input_path, output_path]
        subprocess.run(cmd)

    cap.release()
    print(f"Vidéo pré-traitée sauvegardée à {output_path}")
    return output_path


def preprocess_all_videos(user_id, base_input_dir="/app/shared/inputs", base_output_dir="/app/shared/processed"):
    """
    Traite toutes les vidéos dans le répertoire d'entrée et les sauvegarde dans le répertoire de sortie.
    """
    user_input_dir = os.path.join(base_input_dir, user_id)
    user_output_dir = os.path.join(base_output_dir, user_id)
    video_files = [f for f in os.listdir(user_input_dir) if f.endswith(
        ('.mp4', '.mov', '.avi', '.mkv'))]
    print(f"Vidéos trouvées pour le prétraitement : {video_files}")

    for video_file in video_files:
        input_path = os.path.join(user_input_dir, video_file)
        preprocess_video(input_path, user_id, base_output_dir)

    # Appel de l'API pour générer le fichier Excel une fois tous les fichiers traités
    try:
        response = requests.post(
            "http://csv-generation-service:8004/generate-xlsx/", json={"user_id": user_id})
        if response.status_code == 200:
            print("Génération du fichier Excel déclenchée avec succès.")
        else:
            print(
                f"Erreur lors du déclenchement de la génération Excel: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API de génération Excel : {e}")


if __name__ == "__main__":
    preprocess_all_videos()
