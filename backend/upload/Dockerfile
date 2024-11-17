# Utiliser une image de base pour Python et CUDA (si GPU requis)
FROM base-image:latest


# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le script et les dépendances spécifiques dans le conteneur
COPY . /app

EXPOSE 5000

# Commande pour exécuter le script lorsque le conteneur démarre
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]
