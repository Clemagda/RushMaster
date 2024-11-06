# Utiliser une image de base pour Python et CUDA (si GPU requis)
FROM base-image:latest

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le script et les dépendances spécifiques dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Commande pour exécuter le script lorsque le conteneur démarre
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
