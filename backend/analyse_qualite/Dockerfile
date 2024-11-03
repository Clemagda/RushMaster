# Utiliser une image de base pour Python et CUDA (si GPU requis)
FROM base_image:latest


# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le script et les dépendances spécifiques dans le conteneur
COPY _init_.py /app/_init_.py
COPY analyse_qualite.py /app/analyse_qualite.py
COPY requirements.txt /app/requirements.txt

# Copier et installer les dépendances
RUN python -m pip install --no-cache-dir -r requirements.txt

# Commande pour exécuter le script lorsque le conteneur démarre
CMD ["python", "analyse_qualite.py"]
