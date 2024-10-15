import argparse
import os
import torch
from slowfast_llava.llava.model.builder import load_pretrained_model
from slowfast_llava.llava.mm_utils import tokenizer_image_token, process_images, get_model_name_from_path
from slowfast_llava.llava.constants import IMAGE_TOKEN_INDEX
from dataset import load_video
from prompt import get_prompt
from moviepy.editor import VideoFileClip

"""Genère le résumé textuel d'une vidéos avec possibilité de sauvegarder la sortie dans un fichier.
Le résumé ne traite pas (encore) l'audio et se base sur les comportements et l'environnement des personnages. 

    Ex: "In this video, we see a man in a suit standing in an office environment.
    He appears to be in a conversation or presentation, as suggested by his gestures and the attentive expressions of the people around him.
    The office setting includes other individuals, some of whom are seated at desks, and there are various office items visible,
    such as a computer monitor and a handbag. The man in the suit is the central figure,
    and his actions and expressions suggest a professional context, possibly related to business or corporate matters"

Returns:
    Résumé textuel dans la console de commande. Ou sauvegarde dans un fichier .txt ou .csv
"""

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
def run_inference(video_path, model_path='liuhaotian/llava-v1.6-vicuna-7b', conv_mode='vicuna_v1',
                  model_base=None,
                  question="Describe this video in details",
                  num_frames=16,temperature=0.2,
                  top_p=None,num_beams=1,temporal_aggregation=None,output_dir='Outputs',output_name='generated_resume',rope_scaling_factor=1):
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
    # Charger le tokenizer, modèle et image processor
    model_path = os.path.expanduser(args.model_path)
    model_name =  get_model_name_from_path(model_path)
    tokenizer, model, image_processor, context_len = load_pretrained_model(
        model_path,
        args.model_base,
        model_name,
        device=torch.cuda.current_device(),
        device_map="cuda",
        rope_scaling_factor=args.rope_scaling_factor,
    )

    #num_frames =  get_total_frames(args.video_path)
    
    # Chargement des frames de la vidéo spécifique
    video_frames, sizes = load_video(args.video_path, num_frms=args.num_frames)

    # Génération du résumé
    summary = llava_inference(
        video_frames,
        args.question,
        args.conv_mode,
        model,
        tokenizer,
        image_processor,
        sizes,
        args.temperature,
        args.top_p,
        args.num_beams,
        args.temporal_aggregation,
    )

    # Afficher le résumé généré
    print(f"Résumé généré :\n{summary}")

    # Sauvegarder le résumé dans un fichier texte, si spécifié
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        output_path = os.path.join(args.output_dir, f"{args.output_name}.txt")
        with open(output_path, "w") as output_file:
            output_file.write(summary)
        print(f"Résumé sauvegardé dans : {output_path}")

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
    parser.add_argument("--num_frames", type=int, default=16, help="Nombre de frames à utiliser pour l'analyse") #Demo tourne sur 50 frames. OOM si utilisation max frames.
    parser.add_argument("--temperature", type=float, default=0.2, help="Température pour la génération de texte")
    parser.add_argument("--top_p", type=float, default=None, help="Paramètre top_p pour la génération")
    parser.add_argument("--num_beams", type=int, default=1, help="Nombre de beams pour la génération")
    parser.add_argument("--temporal_aggregation", type=str, default=None, help="Agrégation temporelle des frames")
    parser.add_argument("--output_dir", type=str, help="Répertoire pour sauvegarder le résumé")
    parser.add_argument("--output_name", type=str, help="Nom du fichier de sortie", required=False)
    parser.add_argument("--rope_scaling_factor", type=int, default=1, help="Facteur de scaling de rope")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_inference(args.video_path,
                  args.model_path,
                  args.conv_mode,
                  args.model_base,
                  args.question,
                  args.num_frames,
                  args.temperature,
                  args.top_p,
                  args.num_beams,
                  args.temporal_aggregation,
                  args.output_dir,
                  args.output_name,
                  args.rope_scaling_factor)
