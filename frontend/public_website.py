import streamlit as st
from PIL import Image
import requests
import os

# Définition du style global
st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .main-header {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            margin-top: 20px;
        }
        .banner {
            text-align: center;
        }
        .banner img {
            width: 100%;
            max-height: 250px;
            object-fit: cover;
        }
        .content {
            text-align: center;
            padding: 20px;
        }
        .upload-section {
            text-align: center;
            padding: 30px;
        }
        .info-message {
            text-align: center;
            font-size: 18px;
            color: yellow;
            padding: 10px;
            background-color: #333;
            border-radius: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Charger le logo en bannière
logo_path = "frontend/logo_avec_nom.webp"  # Chemin vers l'image de la bannière
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, use_column_width=True)

# Présentation de l'entreprise
st.markdown('<div class="main-header">Bienvenue sur Dolly</div>',
            unsafe_allow_html=True)
st.write("""
Dolly est une entreprise innovante spécialisée dans l’intelligence artificielle appliquée au montage vidéo. Notre mission est de révolutionner le dérushage en automatisant l’analyse des rushs vidéo, permettant ainsi aux monteurs professionnels, studios et créateurs de contenu de gagner un temps précieux.
Grâce à une technologie avancée basée sur des modèles d’IA, Dolly identifie et extrait les moments clés d’une vidéo, générant un résumé structuré compatible avec les principaux logiciels de montage. Conçu comme une plateforme SaaS, notre service est scalable, sécurisé et adapté aux besoins des professionnels du secteur audiovisuel.
Notre objectif est de simplifier le processus de post-production tout en garantissant une qualité optimale et une expérience utilisateur fluide. En intégrant Dolly dans leur workflow, les monteurs vidéo peuvent se concentrer sur la partie créative, laissant l’IA gérer les tâches répétitives et chronophages.
Avec une vision ambitieuse et une approche technologique innovante, Dolly est prêt à redéfinir le futur du montage vidéo.
""")

st.markdown('<div class="content">', unsafe_allow_html=True)
st.header("Essayez l'application")
st.write("Téléversez vos vidéos et laissez notre IA faire le travail pour vous !")
st.markdown('</div>', unsafe_allow_html=True)

# Message d'information
st.markdown('<div class="info-message">Attention : L application est encore en cours de développement, certaines fonctionnalités peuvent ne pas être disponibles.', unsafe_allow_html=True)

# Intégration du script de test de l'application
TRIGGER_LAMBDA_URL = "https://h6x40qebq0.execute-api.eu-west-2.amazonaws.com/dev/trigger-eks"
UPLOAD_SERVICE_URL = "http://a63c5f5d9a4cb44b5becdd5e962cdc20-1151764598.eu-west-2.elb.amazonaws.com:5000/upload/"
PREPROCESSING_URL = "http://ac54083482f5e492990dfd3219018752-338662646.eu-west-2.elb.amazonaws.com:8000/preprocess/"
STOP_LAMBDA_URL = "https://czsnaevo48.execute-api.eu-west-3.amazonaws.com/dev"

# Interface
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_files = st.file_uploader("Téléversez vos fichiers vidéo", type=[
                                  "mp4", "mov", "avi", "mkv"], accept_multiple_files=True)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_files:
    if st.button("Démarrer le traitement"):
        st.success("Fichiers téléversés. Le traitement est en cours...")
        # Simuler un appel API de traitement
        response = requests.post(PREPROCESSING_URL, json={
                                 "user_id": "test_user"})
        if response.status_code == 200:
            st.success("Traitement terminé avec succès !")
        else:
            st.error("Une erreur est survenue lors du traitement.")
