from transformers import AutoTokenizer,  AutoModelForCausalLM, LlamaTokenizer
import torch

# Lien du modèle

# Remplace par le chemin du dépôt cloné
model_path = "C:/Users/clema/Documents/RushMaster/Llama-3-LongVILA-8B-128Frames"
model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = LlamaTokenizer.from_pretrained(model_path)

# ----------------------------------
# Normalement, LongVILA est kle modèle que je cherche, optimisé pour les vidéos longues.
# Il est cendé me permettre directement de faire la génération de résumé "clefs en main" comme n'importe quel modèle.
# Cela reste à tester, c'est pour ça que je me bats encore avec HF
# ----------------------------------


# ------------
# Modèles potentiels :
# - SlowFast
