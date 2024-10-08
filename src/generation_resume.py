from transformers import AutoTokenizer,  AutoModelForCausalLM, LlamaTokenizer
import torch

# Lien du modèle :https://huggingface.co/Efficient-Large-Model/Llama-3-LongVILA-8B-128Frames/tree/main
#
# # Charger le modèle depuis le répertoire local
# Remplace par le chemin du dépôt cloné
model_path = "C:/Users/clema/Documents/RushMaster/Llama-3-LongVILA-8B-128Frames"
model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = LlamaTokenizer.from_pretrained(model_path)

# Ensuite, tu peux utiliser le modèle comme d'habitude
