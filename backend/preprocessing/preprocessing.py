import os
import subprocess
import requests

INPUT_DIRECTORY = "/app/shared/inputs"
PROCESSED_DIR = "/app/shared/processed"
TARGET_RESOLUTION = (224, 224)


def preprocess_all_videos(user_id: str):
    """
    Traite toutes les vidéos dans le répertoire d'entrée et les sauvegarde dans le répertoire de sortie.
    """
    user_input_dir = os.path.join(INPUT_DIRECTORY, user_id)
    user_processed_dir = os.path.join(PROCESSED_DIR, user_id)

    if not os.path.exists(user_input_dir):
        raise FileNotFoundError(
            "Le répertoire utilisateur {} est introuvable.".format(user_input_dir))

    os.makedirs(user_processed_dir, exist_ok=True)

    video_files = [f for f in os.listdir(user_input_dir) if f.endswith(
        ('.mp4', '.mov', '.avi', '.mkv'))]
    print(f"Vidéos trouvées pour le prétraitement : {video_files}")

    if not video_files:
        raise FileNotFoundError(
            f"Aucune vidéo trouvée dans le répertoire {user_input_dir}")

    for video_file in video_files:
        input_path = os.path.join(user_input_dir, video_file)
        video_name, video_ext = os.path.splitext(video_file)
        output_path = os.path.join(
            user_processed_dir, f"processed_{video_name}{video_ext}")

        cap = subprocess.run([
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
            "-of", "csv=p=0", input_path
        ], capture_output=True, text=True)

        if cap.returncode != 0:
            print(f"Erreur lors de l'analyse de la vidéo : {input_path}")
            continue

        width, height = map(int, cap.stdout.strip().split(','))
        print(f"Résolution originale : {width}x{height}")

        if (width, height) != TARGET_RESOLUTION:
            print("Redimensionnement de la vidéo à {} x {}".format(
                TARGET_RESOLUTION[0], TARGET_RESOLUTION[1]))

            cmd = [
                'ffmpeg', '-y', '-i', input_path, '-vf',
                f'scale={TARGET_RESOLUTION[0]}:trunc(ow/a/2)*2',
                output_path
            ]
            try:
                subprocess.run(cmd, check=True)
                print(f"Vidéo redimensionnée sauvegardée à {output_path}")
            except subprocess.CalledProcessError as e:
                print("Erreur lors du redimensionnement de la vidéo {} : {}".format(
                    input_path, e))
        else:
            print("Pas de redimensionnement nécessaire, copie de la vidéo.")
            try:
                subprocess.run(['cp', input_path, output_path], check=True)
                print(f"Vidéo copiée à {output_path}")
            except subprocess.CalledProcessError as e:
                print("Erreur lors de la copie de la vidéo {} : {}".format(
                    input_path, e))

    # Appel de l'API pour générer le fichier Excel une fois tous les fichiers traités
    try:
        payload = {
            "user_id": user_id,
            "processed_path": user_processed_dir
        }
        response = requests.post(
            "http://csv-generation-service:8004/generate-xlsx/",
            json=payload
        )
        response.raise_for_status()
        print('Génération du fichier Excel déclenchée avec succès.')
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du déclenchement de la génération Excel: {e}")
        raise RuntimeError(
            f"Erreur lors du déclenchement de la génération Excel: {e}")
