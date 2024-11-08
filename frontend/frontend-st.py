import streamlit as st
import os
import shutil
import requests

# Définir le répertoire local de téléversement
directory = 'shared/inputs'  # sera l'ARN du bucket S3

# Créer le répertoire si nécessaire
if not os.path.exists(directory):
    os.makedirs(directory)

# Interface du frontend Streamlit
st.title("Application de Traitement de Rush Vidéo - Téléversement des Vidéos")

# Utilisateur peut sélectionner plusieurs fichiers
uploaded_files = st.file_uploader("Téléversez vos fichiers vidéo ici", type=[
                                  "mp4", "mov", "avi", "mkv"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Créer le chemin de sortie pour chaque fichier téléversé
        output_path = os.path.join(directory, uploaded_file.name)

        # Écrire le fichier dans le répertoire ./shared/inputs
        with open(output_path, "wb") as out_file:
            # ecrit les fichiers de l'utilisateur dans le bucket S3 monté dans docker-compose
            shutil.copyfileobj(uploaded_file, out_file)

        st.success(f"Fichier téléversé avec succès : {uploaded_file.name}")

    # Bouton pour déclencher le prétraitement
    if st.button("Lancer le traitement"):
        with st.spinner("Patience, le traitement est en cours ..."):
            response = requests.post("http://localhost:8000/preprocess/")
            if response.status_code == 200:
                st.success(
                    "Le traitement est terminé.")
            else:
                st.error(
                    "Erreur lors du déclenchement du service de prétraitement.")

    # Bouton pour télécharger le fichier Excel généré
    if os.path.exists("./shared/outputs/results.xlsx"):
        with open("./shared/outputs/results.xlsx", "rb") as file:
            btn = st.download_button(
                label="Télécharger le fichier Excel généré",
                data=file,
                file_name="results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
