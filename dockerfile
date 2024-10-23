# Utiliser une image de base avec CUDA
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04

# Installer les dépendances de base
RUN apt-get update && apt-get install -y \
    wget \
    git \
    curl \
    zip \
    unzip \
    ffmpeg \
    python3-pip \
    python3-dev \
    libsndfile1 \
    libgl1-mesa-glx

# Créer un environnement de travail
WORKDIR /workspace

# Installer Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH="/opt/conda/bin:${PATH}"

# Copier les fichiers du projet local dans le conteneur
COPY . /workspace

# Créer l'environnement Conda et installer les dépendances
RUN conda create -n sf_llava python=3.10.12 -y && \
    conda init bash && \
    echo "conda activate sf_llava" >> ~/.bashrc && \
    /bin/bash -c "source ~/.bashrc && \
    conda install pip && \
    pip install -r /workspace/requirements.txt"

# Activer l'environnement conda dans chaque commande Docker
SHELL ["conda", "run", "-n", "sf_llava", "/bin/bash", "-c"]

# Installer d'autres dépendances requises
RUN pip install vosk boto3 moviepy torch torchvision torchaudio
RUN pip install 'git+https://github.com/huggingface/transformers' 'git+https://github.com/facebookresearch/fvcore' slowfast_llava

# Spécifier les variables d'environnement pour distinguer les environnements Cloud/Local
ENV ENVIRONMENT="CLOUD"

# Définir le point d'entrée de l'application
CMD ["python", "src/csv_generation.py"]
