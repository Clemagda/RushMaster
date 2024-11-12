import streamlit as st
import os
import shutil
import requests
import boto3
from botocore.exceptions import NoCredentialsError

# Configuration AWS
AWS_ACCESS_KEY = 'AKIA4MTWJVT4IFGAESJ7'
AWS_SECRET_KEY = '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'
BUCKET_NAME = 'data-rushmaster'

# Initialiser le client S3
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_SECRET_KEY)


# Interface du frontend Streamlit
st.title("Application de Traitement de Rush Vidéo - Téléversement des Vidéos")

# Utilisateur peut sélectionner plusieurs fichiers
uploaded_files = st.file_uploader("Téléversez vos fichiers vidéo ici", type=[
                                  "mp4", "mov", "avi", "mkv"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            # Téléverser chaque fichier sur S3
            s3.upload_fileobj(uploaded_file, BUCKET_NAME,
                              f"Inputs/{uploaded_file.name}")
            st.success(
                f"Fichier téléversé avec succès sur S3 : {uploaded_file.name}")
        except NoCredentialsError:
            st.error(
                "Les informations d'identification AWS sont manquantes ou incorrectes.")
        except Exception as e:
            st.error(f"Erreur lors du téléversement : {e}")

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
