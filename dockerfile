# Utiliser une image de base avec CUDA
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04

# Configurer debconf pour éviter les questions interactives pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Prédéfinir le fuseau horaire
RUN ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime && \
    echo "Europe/Paris" > /etc/timezone

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

# Configurer le fuseau horaire
RUN dpkg-reconfigure -f noninteractive tzdata

# Installer wheel pour la construction des packages Python
RUN pip install wheel

# Créer un environnement de travail
WORKDIR /workspace

# Installer Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH="/opt/conda/bin:${PATH}"

# Initialiser Conda
RUN /opt/conda/bin/conda init bash

# Copier les fichiers du projet local dans le conteneur
COPY . /workspace

# Créer le répertoire temporaire pour les fichiers de travail
RUN mkdir -p /tmp

#Déinifition du PYTHON PATH pour inclure le repertoire workspace
ENV PYTHONPATH="/workspace"

# Créer l'environnement Conda et installer les dépendances
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda create -n sf_llava python=3.10.12 -y && \
    echo 'conda activate sf_llava' >> ~/.bashrc"

# Définir le SHELL pour que toutes les instructions utilisent conda
SHELL ["conda", "run", "-n", "sf_llava", "/bin/bash", "-c"]

# Activer l'environnement Conda, installer pip et opencv-python-headless
RUN conda install pip -y
RUN pip install opencv-python-headless

# Installer torch, torchvision, torchaudio depuis l'index PyTorch
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Installer les autres dépendances requises du projet
RUN pip install -r /workspace/requirements.txt

# Installer d'autres dépendances requises
RUN pip install vosk boto3 moviepy
RUN pip install 'git+https://github.com/huggingface/transformers' 'git+https://github.com/facebookresearch/fvcore'

# Définir le point d'entrée pour activer l'environnement et lancer le script
ENTRYPOINT ["/bin/bash", "-c", "source /opt/conda/etc/profile.d/conda.sh && conda activate sf_llava && echo 'Conda environment activated'"]

CMD [ "python", "/workspace/src/csv_generation.py" ]

