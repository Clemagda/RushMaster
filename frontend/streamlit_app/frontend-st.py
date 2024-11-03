import streamlit as st
import requests
import boto3
import os
import json

# Variables de configuration
LAMBDA_URL = 'https://eggktw3gpi.execute-api.eu-west-3.amazonaws.com/Prod/upload'
BUCKET_NAME = 'data-rushmaster'

# Interface Streamlit pour le téléversement
st.title("Téléversement de Vidéos")
uploaded_files = st.file_uploader("Choisissez les vidéos", accept_multiple_files=True, type=["mp4", "avi", "mov"])

if st.button("Téléverser"):
    if uploaded_files:
        # Liste des noms de fichiers
        file_names = [file.name for file in uploaded_files]

        # Appel de la fonction Lambda pour obtenir des URLs présignées
        response = requests.post(LAMBDA_URL, json={"video_names": file_names})
        if response.status_code == 200:
            data = response.json()
            body_content = json.loads(data['body'])
        
            print('Réponse complète:',data)
            st.write('Réponse reçue:',data)
            presigned_urls = body_content['upload_urls']

            # Téléverse chaque fichier via les URLs présignées
            for i, file in enumerate(uploaded_files):
                url = presigned_urls[i]['upload_url']
                files = {'file': file}
                print(f"Uploading to URL: {url}")
                result = requests.put(url, data=file)
                print(f"Status Code: {result.status_code}")
                print(f"Response Headers: {result.headers}")
                print(f"Response Content: {result.text}")
                if result.status_code == 200:
                    st.write(f"{file.name} téléversé avec succès.")
                else:
                    st.write(f"Échec du téléversement de {file.name}")
                    

        else:
            st.write("Erreur lors de la génération des URLs présignées.")
            st.write(response.status_code, response.json())
    else:
        st.write("Veuillez sélectionner des fichiers à téléverser.")

