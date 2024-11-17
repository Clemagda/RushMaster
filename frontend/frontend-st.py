import streamlit as st
import os
import requests
import time

# Configuration URLs et informations
TRIGGER_LAMBDA_URL = "https://<API-ID>.execute-api.<region>.amazonaws.com/dev/trigger-eks"
UPLOAD_SERVICE_URL = "http://<LOADBALANCER-URL>/upload"

# Interface du frontend Streamlit
st.title("Application de Traitement de Rush Vidéo - Téléversement des Vidéos")

# Utilisateur peut sélectionner plusieurs fichiers
uploaded_files = st.file_uploader("Téléversez vos fichiers vidéo ici", type=[
                                  "mp4", "mov", "avi", "mkv"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Préparer l'environnement de traitement"):
        with st.spinner("Préparation de l'environnement..."):
            response = requests.post(TRIGGER_LAMBDA_URL, json={
                                     "user_id": "user123"})
            if response.status_code == 200:
                st.success("Environnement prêt ! Les pods ont été démarrés.")
            else:
                st.error(
                    f"Erreur lors de l'initialisation des pods: {response.text}")
            # Attendre que les pods soient opérationnels (temps à adapter)
            time.sleep(20)

    if st.button('Téléverser les fichiers pour le traitement'):
        for uploaded_file in uploaded_files:
            with st.spinner(f"Téléversement de {uploaded_file.name} en cours ..."):
                try:
                    files = {'file': uploaded_file.getvalue()}
                    headers = {'user-id': "user123",
                               'file-name': uploaded_file.name}
                    upload_response = requests.post(
                        UPLOAD_SERVICE_URL, files=files, headers=headers)

                    if upload_response.status_code == 200:
                        st.success(
                            f"Fichier {uploaded_file.name} téléversé avec succès !")
                    else:
                        st.error(
                            f"Erreur lors du téléversement de {uploaded_file.name} : {upload_response.text}")
                except Exception as e:
                    st.error(f"Erreur lors du téléversement : {e}")

    # Bouton pour déclencher le prétraitement
    if st.button("Lancer le traitement"):
        with st.spinner("Patience, le traitement est en cours ..."):
            response = requests.post(
                f"http://{UPLOAD_SERVICE_URL}/preprocess/")
            if response.status_code == 200:
                st.success(
                    "Le traitement est terminé.")
            else:
                st.error(
                    f"Erreur lors du déclenchement du service de prétraitement : {response.text}")

    # Bouton pour télécharger le fichier Excel généré
    if os.path.exists("./shared/outputs/results.xlsx"):
        with open("./shared/outputs/results.xlsx", "rb") as file:
            btn = st.download_button(
                label="Télécharger le fichier Excel généré",
                data=file,
                file_name="results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
