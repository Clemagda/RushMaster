import streamlit as st  # type: ignore
import os
import requests  # type: ignore
import time

# TODO: màj des boutons en fonctiond e l'état réel des instances.
# Tout fluidifier avec un bouton unique mais un affichage de progression des différents étapes

# Configuration URLs et informations
TRIGGER_LAMBDA_URL = "https://l02i7qlyzc.execute-api.eu-west-3.amazonaws.com/dev/trigger-eks"
UPLOAD_SERVICE_URL = "http://a1679451e08a945bfb3b1f27b32fd628-2060507120.eu-west-3.elb.amazonaws.com:5000/upload/"
PREPROCESSING_URL = "http://a886391d631da490d8c5429fb5b61ced-766592315.eu-west-3.elb.amazonaws.com:8000/preprocess/"
STOP_LAMBDA_URL = "https://czsnaevo48.execute-api.eu-west-3.amazonaws.com/dev"

# Initialiser les états dans la session
if 'environment_ready' not in st.session_state:
    st.session_state['environment_ready'] = False

if 'files_uploaded' not in st.session_state:
    st.session_state['files_uploaded'] = False

if 'preprocessing_done' not in st.session_state:
    st.session_state['preprocessing_done'] = False

if 'results_downloaded' not in st.session_state:
    st.session_state['results_downloaded'] = False

# Interface du frontend Streamlit
st.title("Application de Traitement de Rush Vidéo - Téléversement des Vidéos")

# Utilisateur peut sélectionner plusieurs fichiers
uploaded_files = st.file_uploader("Téléversez vos fichiers vidéo ici", type=[
                                  "mp4", "mov", "avi", "mkv"], accept_multiple_files=True)

# Préparation de l'environnement
if uploaded_files and not st.session_state['environment_ready']:
    if st.button("Préparer l'environnement de traitement"):
        with st.spinner("Préparation de l'environnement..."):
            # Appel de la fonction Lambda pour démarrer les pods
            response = requests.post(TRIGGER_LAMBDA_URL, json={
                                     "action": "start"})
            if response.status_code == 200:
                st.success("Environnement prêt ! Les pods ont été démarrés.")
                st.session_state['environment_ready'] = True

            else:
                st.error(
                    f"Erreur lors de l'initialisation des pods: {response.text}")

# Téléversement des fichiers (uniquement si l'environnement est prêt)
if st.session_state['environment_ready'] and not st.session_state['files_uploaded']:
    if st.button('Téléverser les fichiers pour le traitement'):
        all_uploaded = True
        for uploaded_file in uploaded_files:
            with st.spinner(f"Téléversement de {uploaded_file.name} en cours ..."):
                try:
                    files = {'file': (uploaded_file.name,
                                      uploaded_file, uploaded_file.type)}
                    upload_response = requests.post(
                        UPLOAD_SERVICE_URL, files=files)

                    if upload_response.status_code == 200:
                        st.success(
                            f"Fichier {uploaded_file.name} téléversé avec succès !")
                    else:
                        st.error(
                            f"Erreur lors du téléversement de {uploaded_file.name} : {upload_response.text}")
                        all_uploaded = False
                except Exception as e:
                    st.error(f"Erreur lors du téléversement : {e}")
                    all_uploaded = False

        if all_uploaded:
            st.session_state['files_uploaded'] = True

# Déclenchement du prétraitement (uniquement si les fichiers sont téléversés)
if st.session_state['files_uploaded'] and not st.session_state['preprocessing_done']:
    if st.button("Lancer le traitement"):
        with st.spinner("Patience, le traitement est en cours ..."):
            try:
                # 1h de traitement prévue
                response = requests.post(
                    PREPROCESSING_URL, timeout=3600)  # /preprocess/
                if response.status_code == 200:
                    st.success("Le traitement est terminé.")
                    st.session_state['preprocessing_done'] = True
                else:
                    st.error(
                        f"Erreur lors du déclenchement du service de prétraitement : {response.text}")
            except Exception as e:
                st.error(f"Erreur lors du déclenchement : {e}")

# Téléchargement du fichier Excel généré (uniquement si le prétraitement est terminé)
if st.session_state['preprocessing_done']:
    if os.path.exists("./shared/outputs/results.xlsx"):
        with open("./shared/outputs/results.xlsx", "rb") as file:
            st.download_button(
                label="Télécharger le fichier Excel généré",
                data=file,
                file_name="results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.session_state['results_downloaded'] = True
if st.session_state['results_downloaded']:
    if st.button("Arrêter l'environnement de traitement"):
        with st.spinner("Arrêt de l'environnement..."):
            stop_response = requests.post(
                STOP_LAMBDA_URL, json={"action": "stop"})
            if stop_response.status_code == 200:
                st.success("Environnement arrêté avec succès.")
            else:
                st.error(
                    f"Erreur lors de l'arrêt de l'environnement : {response.text}")
