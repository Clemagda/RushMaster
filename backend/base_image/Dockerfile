# Dockerfile de l'image de base
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# Désactiver les interactions et définir le fuseau horaire
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime && \
    echo "Europe/Paris" > /etc/timezone && \
    apt-get update && \
    apt-get install -y tzdata && \
    dpkg-reconfigure -f noninteractive tzdata

# Installer Python 3.10, pip, et les dépendances communes
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-distutils curl && \
    apt-get install nano && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installer pip pour Python 3.10
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# Définir Python 3.10 comme version par défaut
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Installer les dépendances communes
COPY requirements_base.txt .
RUN python -m pip install --no-cache-dir -r requirements_base.txt
