#!/bin/bash
# Met à jour les paquets et installe Docker
apt-get update -y
apt-get install -y docker.io

# Démarre le service Docker
service docker start

# Connecte à Amazon ECR et télécharge l'image
aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin 851725364472.dkr.ecr.eu-west-3.amazonaws.com

# Télécharge la dernière version de votre image depuis ECR
docker pull 851725364472.dkr.ecr.eu-west-3.amazonaws.com/rushmaster-app

# Crée les répertoires locaux pour synchroniser les buckets S3
mkdir -p /mnt/s3/input /mnt/s3/output

# Synchronise les buckets S3 avec les répertoires locaux
aws s3 sync s3://data-rushmaster/Inputs/ /mnt/s3/input
aws s3 sync s3://data-rushmaster/Outputs/ /mnt/s3/output

# Lance le conteneur
docker run -d -e ENVIRONMENT="CLOUD" -v /mnt/s3/input:/app/input -v /mnt/s3/output:/app/output <votre-account-id>.dkr.ecr.<votre-region>.amazonaws.com/votre-image:latest

# Optionnel : Si des résultats sont générés, synchronise le répertoire de sortie local avec le bucket S3 après l'exécution du conteneur
aws s3 sync /mnt/s3/output s3://data-rushmaster/Outputs/