import pandas as pd
import argparse
def csv_to_excel(input_csv, output_excel):
    """
    Convertit un fichier CSV en fichier Excel (.xlsx).
    
    Args:
        input_csv (str): Chemin vers le fichier CSV d'entrée.
        output_excel (str): Chemin pour sauvegarder le fichier Excel de sortie.
    
    Returns:
        None: Le fichier Excel est généré à l'emplacement spécifié.
    """
    try:
        # Lire le fichier CSV en utilisant pandas
        df = pd.read_csv(input_csv)

        # Sauvegarder en format Excel (.xlsx)
        df.to_excel(output_excel, index=False, engine='openpyxl')
        
        print(f"Conversion réussie ! Fichier Excel sauvegardé dans : {output_excel}")
    
    except Exception as e:
        print(f"Erreur lors de la conversion du CSV en Excel : {e}")

# Exemple d'utilisation

if __name__=="__main__":

    input_csv = "Outputs/results.csv"  # Chemin du fichier CSV
    output_excel = "Outputs/results.xlsx"  # Chemin du fichier Excel de sortie

    csv_to_excel(input_csv, output_excel)

