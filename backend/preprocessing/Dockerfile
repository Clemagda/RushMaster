# Utiliser une image de base pour Python et CUDA (si GPU requis)
FROM base_image:latest


# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le script et les dépendances spécifiques dans le conteneur
COPY preprocessing.py /app/preprocessing.py
COPY _init_.py /app/_init_.py
COPY requirements_preprocessing.txt /app/requirements_preprocessing.txt

# Copier et installer les dépendances
RUN python -m pip install --no-cache-dir -r requirements_preprocessing.txt

# Commande pour exécuter le script lorsque le conteneur démarre
CMD ["python", "preprocessing.py"]
