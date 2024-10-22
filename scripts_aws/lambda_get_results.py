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

# Générer une URL pré-signée pour télécharger RESULTS.CSV depuis le répertoire Outputs/
def lambda_handler(event, context):
    try:
        # Vérifier si le fichier RESULTS.CSV est disponible
        results_key = 'Outputs/RESULTS.CSV'
        s3_client.head_object(Bucket=BUCKET_NAME, Key=results_key)  # Vérifie la présence du fichier

        # Générer une URL pré-signée pour le fichier CSV
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': results_key},
            ExpiresIn=3600  # URL valable pendant 1 heure
        )

        # Arrêter l'instance EC2 après le téléchargement
        stop_ec2_instance()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': "Le fichier results.csv est prêt.",
                'download_url': presigned_url  # URL pour télécharger le fichier CSV
            })
        }

    except ClientError as e:
        # Si le fichier n'est pas encore disponible, retourner un message
        if e.response['Error']['Code'] == '404':
            return {
                'statusCode': 404,
                'body': json.dumps("Le fichier results.csv n'est pas encore prêt.")
            }
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erreur lors de la vérification : {str(e)}")
        }

# Arrêter l'instance EC2 après le traitement
def stop_ec2_instance():
    try:
        ec2_client.stop_instances(InstanceIds=[INSTANCE_ID])
        print(f"Instance EC2 {INSTANCE_ID} arrêtée.")
    except ClientError as e:
        print(f"Erreur lors de l'arrêt de l'instance EC2 : {str(e)}")
