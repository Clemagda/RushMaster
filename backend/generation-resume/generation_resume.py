import argparse
import os
import boto3 # type: ignore
import torch # type: ignore
from slowfast_llava.llava.model.builder import load_pretrained_model
from slowfast_llava.llava.mm_utils import tokenizer_image_token, process_images, get_model_name_from_path
from slowfast_llava.llava.constants import IMAGE_TOKEN_INDEX
from dataset import load_video
from prompt import get_prompt
from moviepy.editor import VideoFileClip # type: ignore

global_model= None
global_tokenizer= None
globale_image_processor = None
global_context_len = None


s3 = boto3.client("s3") if os.getenv("ENVIRONMENT", "LOCAL") == "CLOUD" else None

def download_model_files_from_s3(bucket_name, s3_model_prefix, local_model_path):
    """
    Télécharge tous les fichiers d'un répertoire dans un bucket S3 vers un répertoire local.
    
    Args:
        bucket_name (str): Le nom du bucket S3 (ex: "data-rushmaster").
        s3_model_prefix (str): Le chemin du répertoire contenant les fichiers du modèle dans S3 (ex: "utils/liuhaotian/llava-v1.6-civuna-7b").
        local_model_path (str): Le chemin local où stocker les fichiers téléchargés.
    """
    # Créer le répertoire local si nécessaire
    if not os.path.exists(local_model_path):
        os.makedirs(local_model_path)
    
    # Lister tous les fichiers dans le répertoire S3
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_model_prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3_file_path = obj['Key']
                local_file_path = os.path.join(local_model_path, os.path.basename(s3_file_path))
                print(f"Téléchargement de {s3_file_path} vers {local_file_path}")
                s3.download_file(bucket_name, s3_file_path, local_file_path)
        else:
            print(f"Aucun fichier trouvé dans {s3_model_prefix}")
    except Exception as e:
        print(f"Erreur lors du téléchargement des fichiers : {e}")

def load_model_once():
    """
    Charge le modèle SlowFast-LLaVA une seule fois et stocke les variables dans l'espace global.
    """
    global global_model, global_tokenizer, global_image_processor, global_context_len
    
    if global_model is None:
        print("===Chargement du modèle SlowFast-LLaVA...===")

        if os.getenv("ENVIRONMENT", "LOCAL") == "CLOUD":
            local_model_path = "/tmp/llava-v1.6-vicuna-7b"  # Chemin local sur l'instance EC2
            download_model_files_from_s3(
                bucket_name="data-rushmaster", 
                s3_model_prefix="utils/liuhaotian/llava-v1.6-vicuna-7b", 
                local_model_path=local_model_path
            )
            model_path = local_model_path
        else:
            model_path='liuhaotian/llava-v1.6-vicuna-7b'


        model_path = os.path.expanduser(model_path)
        model_name = get_model_name_from_path(model_path)
        
        global_tokenizer, global_model, global_image_processor, global_context_len = load_pretrained_model(
            model_path,
            model_base=None,
            model_name=model_name,
            device=torch.cuda.current_device(),
            device_map="cuda",
            rope_scaling_factor=1
        )
        print("===Modèle chargé avec succès.===")
    else:
        print("===Modèle déjà chargé, réutilisation du modèle en mémoire.===")

def get_total_frames(video_path):
    video = VideoFileClip(video_path)
    total_frames = int(video.fps * video.duration)
    return total_frames

# Fonction pour générer un résumé vidéo à partir d'une seule vidéo
def llava_inference(video_frames, 
                    question,
                    conv_mode,
                    model,
                    tokenizer,
                    image_processor, image_sizes, temperature, top_p, num_beams, temporal_aggregation):
    # Utiliser un prompt générique pour demander un résumé de la vidéo
    prompt = get_prompt(model, conv_mode, question)

    # Créer l'entrée texte à partir du prompt
    input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt").unsqueeze(0).cuda()

    # Préparer les frames de la vidéo pour le modèle
    image_tensor = process_images(video_frames, image_processor, model.config)

    # Générer le résumé à partir du modèle
    with torch.inference_mode():
        output_ids = model.generate(
            input_ids,
            images=image_tensor.to(dtype=torch.float16, device="cuda", non_blocking=True),
            image_sizes=image_sizes,
            do_sample=True if temperature > 0 else False,
            temperature=temperature,
            top_p=top_p,
            num_beams=num_beams,
            max_new_tokens=128,
            use_cache=True,
            temporal_aggregation=temporal_aggregation,
        )

    # Décoder la sortie et retourner le résumé textuel
    summary = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()
    return summary

# Fonction principale pour exécuter l'inférence et générer le résumé pour une seule vidéo
def run_inference(video_path, conv_mode='vicuna_v1',
                  question="Describe this video in details",num_frames=50,
                  frames_auto=False, temperature=0.2,
                  top_p=None,num_beams=1,temporal_aggregation=None,rope_scaling_factor=1,output_dir='Outputs'): #,output_name='generated_resume'
    """
    Génère un résumé vidéo en utilisant un modèle pré-entraîné à partir d'une seule vidéo.

    Args:
        video_path (str): Chemin vers la vidéo à analyser.
        model_path (str): Chemin vers le modèle pré-entraîné à utiliser pour l'inférence (par défaut 'liuhaotian/llava-v1.6-vicuna-7b').
        conv_mode (str): Mode de conversation à utiliser avec le modèle (par défaut 'vicuna_v1').
        model_base (str or None): Base de modèle à utiliser, si applicable (par défaut None).
        question (str): Question à poser au modèle pour générer le résumé vidéo (par défaut "Describe this video in details").
        num_frames (int): Nombre total de frames à utiliser pour l'analyse vidéo (par défaut 16).
        temperature (float): Température pour l'échantillonnage lors de la génération du résumé (par défaut 0.2).
        top_p (float or None): Valeur du paramètre top-p pour le tri des résultats d'inférence (par défaut None).
        num_beams (int): Nombre de faisceaux à utiliser pour la recherche de faisceaux (beam search) lors de la génération du résumé (par défaut 1).
        temporal_aggregation (str or None): Méthode d'agrégation temporelle des frames vidéo (par défaut None).
        output_dir (str): Répertoire où sauvegarder le résumé généré (par défaut 'Outputs').
        output_name (str): Nom du fichier de sortie pour le résumé (par défaut 'generated_resume').
        rope_scaling_factor (float): Facteur de mise à l'échelle pour le positionnement relatif (rope scaling) (par défaut 1).

    Raises:
        FileNotFoundError: Si le chemin de la vidéo ou du modèle n'existe pas.
        ValueError: Si une erreur survient lors du chargement des frames vidéo ou du modèle.

    Returns:
        None: La fonction affiche le résumé généré dans la console et le sauvegarde dans un fichier texte si `output_dir` est spécifié.

    Steps:
        1. Charge le modèle pré-entraîné, le tokenizer et l'image processor.
        2. Charge les frames de la vidéo spécifiée.
        3. Génère un résumé vidéo en utilisant l'inférence du modèle et une question spécifique.
        4. Affiche le résumé généré dans la console.
        5. Sauvegarde le résumé dans un fichier texte si le chemin de sortie est fourni.

    Example:
        run_inference("video.mp4", model_path="liuhaotian/llava-v1.6-vicuna-7b", question="Describe the actions in this video", num_frames=20)
    """    
    load_model_once()
    global global_model, global_tokenizer, global_image_processor, global_context_len
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print("===Chargement de la vidéo===")
    if frames_auto is True:
        num_frames =  get_total_frames(video_path)
  
    
    # Chargement des frames de la vidéo spécifique
    video_frames, sizes = load_video(video_path, num_frms=num_frames)
    print("===Frames chargées===")
    print("===Generation du résumé===")
    # Génération du résumé
    summary = llava_inference(
        video_frames,
        question,
        conv_mode,
        global_model,
        global_tokenizer,
        global_image_processor,
        sizes,
        temperature,
        top_p,
        num_beams,
        temporal_aggregation,
    )

    # Afficher le résumé généré
    print(f"Résumé généré :\n{summary}")

    return summary  

# Parser des arguments pour la ligne de commande
def parse_args():
    """
    Parse les arguments de la ligne de commande.
    """
    parser = argparse.ArgumentParser(description="Générer un résumé vidéo pour une seule vidéo.")
    parser.add_argument("--video_path", help="Chemin vers la vidéo", required=True)
    parser.add_argument("--model_path", type=str, default='liuhaotian/llava-v1.6-vicuna-7b', help="Chemin vers le modèle LLaVA")
    parser.add_argument("--conv_mode", type=str, default="vicuna_v1")
    parser.add_argument("--model_base", type=str, default=None, help="Base du modèle")
    parser.add_argument("--question", type=str, default="Describe this video in details")
    parser.add_argument("--num_frames", type=int, default=50, help="Nombre de frames à utiliser pour l'analyse") #Demo tourne sur 50 frames. OOM si utilisation max frames.
    parser.add_argument("--temperature", type=float, default=0.2, help="Température pour la génération de texte")
    parser.add_argument("--top_p", type=float, default=None, help="Paramètre top_p pour la génération")
    parser.add_argument("--num_beams", type=int, default=1, help="Nombre de beams pour la génération")
    parser.add_argument("--temporal_aggregation", type=str, default=None, help="Agrégation temporelle des frames")
    parser.add_argument("--frames_auto", type=bool, default=False, help="Nombre de frames à utiliser pour l'analyse")
    parser.add_argument("--rope_scaling_factor", type=int, default=1, help="Facteur de scaling de rope")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_inference(args.video_path,
                  args.conv_mode,
                  args.question,
                  args.num_frames,
                  args.frames_auto,
                  args.temperature,
                  args.top_p,
                  args.num_beams,
                  args.temporal_aggregation,
                  args.rope_scaling_factor
                  )