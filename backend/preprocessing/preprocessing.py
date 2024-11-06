import argparse
import cv2 # type: ignore
import os
import subprocess

def preprocess_video(input_path='/app/shared/inputs', output_dir="/app/shared/processed", target_resolution=(336, 336)):

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
    print(f"VIdéo pré-traitée sauvegardée à {output_path}")
    return output_path

def parse_args():
    parser = argparse.ArgumentParser(description="Preprocess video for action recognition")
    parser.add_argument("--input_video", type=str, required=True, help="Path to the input video")
    parser.add_argument("--output_video", type=str, default='/app/shared/processed/processed_video.mp4', help="Path to save the processed video")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    preprocess_video(args.input_video, output_path=args.output_video)
