import argparse
import cv2 # type: ignore
import os
import tempfile
import subprocess
import boto3

s3 = boto3.client('s3', region_name='eu-west-3')  # Ajuste la région si nécessaire
bucket_name = "data-rushmaster"
processed_prefix = "processed/"

def save_to_s3(local_video_path, video_name):
    s3_key = f"{processed_prefix}{video_name}"
    s3.upload_file(local_video_path, bucket_name, s3_key)
    print(f"Vidéo {video_name} sauvegardée dans S3 à {s3_key}")

def preprocess_video(input_path, output_path=None, target_resolution=(336, 336)):

    if output_path is None:
        if os.getenv("ENVIRONMENT", "LOCAL") == "CLOUD":
            output_dir = "/tmp"  # Utiliser le répertoire temporaire dans le cloud
        else:
            output_dir = "temp"  # Utiliser "temp" en local
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
        # Créer le chemin de la vidéo prétraitée
        video_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"processed_{video_name}.mp4")
    
    # Lire la vidéo avec OpenCV
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Original resolution: {width}x{height}")

    # Vérifier si un redimensionnement est nécessaire
    if (width, height) != target_resolution:
        print(f"Redimensionnement de la vidéo à {target_resolution[0]}x{target_resolution[1]}")
        # Utiliser FFmpeg pour redimensionner la vidéo
        cmd = [
            'ffmpeg', '-y', '-loglevel','panic', '-i', input_path, '-vf', 
            f'scale={target_resolution[0]}:trunc(ow/a/2)*2',
            output_path
        ]
        subprocess.run(cmd)
    else:
        print("Pas de redimensionnement nécessaire, la vidéo est déjà à la bonne taille.")
        cmd = ['cp', input_path, output_path]
        subprocess.run(cmd)

    cap.release()

    video_name = os.path.basename(output_path)
    save_to_s3(output_path, video_name)
    clean_temp_file(output_path)



def clean_temp_file(file_path):
    """
    Supprimer un fichier temporaire après utilisation.
    
    Args:
        file_path (str): Chemin du fichier temporaire à supprimer.
    """
    try:
        os.remove(file_path)
        print(f"Fichier temporaire supprimé : {file_path}")
    except OSError as e:
        print(f"Erreur lors de la suppression du fichier temporaire : {e}")


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Preprocess video for action recognition")
    parser.add_argument("--input_video", type=str, required=True, help="Path to the input video")

    return parser.parse_args()

if __name__ == "__main__":
    args=parse_args()
    output_path = "Outputs/processed.mp4"
    preprocess_video(args.input_video, output_path=output_path)
