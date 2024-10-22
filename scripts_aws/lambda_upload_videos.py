import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialisation des clients AWS
s3_client = boto3.client('s3')
ec2_client = boto3.client('ec2')

# Variables d'environnement
BUCKET_NAME = os.getenv('BUCKET_NAME')  # Nom du bucket S3
INSTANCE_ID = os.getenv('INSTANCE_ID')  # ID de l'instance EC2

# Fonction Lambda pour gérer le téléversement et démarrer l'instance EC2
def lambda_handler(event, context):
    try:
        # Récupérer les noms des vidéos envoyées
        video_names = event['video_names']  # Liste des noms de fichiers vidéo
        presigned_urls = generate_presigned_urls_for_videos(video_names)

        # Démarrer l'instance EC2 pour traiter les vidéos
        ec2_client.start_instances(InstanceIds=[INSTANCE_ID])

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': "Téléversement réussi. Traitement en cours.",
                'upload_urls': presigned_urls  # URLs pour téléverser les fichiers
            })
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erreur lors du traitement : {str(e)}")
        }

# Générer des URL pré-signées pour plusieurs vidéos
def generate_presigned_urls_for_videos(video_names):
    presigned_urls = []
    for video_name in video_names:
        try:
            # Générer une URL pré-signée pour chaque vidéo
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': BUCKET_NAME, 'Key': f'input/{video_name}'},
                ExpiresIn=3600  # URL valable pendant 1 heure
            )
            presigned_urls.append({
                'video_name': video_name,
                'upload_url': presigned_url
            })
        except ClientError as e:
            print(f"Erreur lors de la génération de l'URL pré-signée pour {video_name} : {str(e)}")
    
    return presigned_urls
