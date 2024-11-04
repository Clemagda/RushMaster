# Utiliser une image de base pour Python et CUDA (si GPU requis)
FROM base_image:latest


# Définir le répertoire de travail dans le conteneur
WORKDIR /frontend_app

# Copier le script et les dépendances spécifiques dans le conteneur
COPY frontend-st.py /frontend_app/frontend-st.py
COPY requirements.txt /frontend_app//requirements.txt

# Copier et installer les dépendances
RUN python -m pip install --no-cache-dir -r requirements.txt

# Commande pour exécuter le script lorsque le conteneur démarre
CMD ["streamlit", "run", "frontend-st.py"]
