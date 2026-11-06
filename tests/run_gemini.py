

import dotenv
import os
import json

from src.constants.env_keys import keys
from src.utils.gemini import make_gemini_client, make_request
from src.utils.csv_reader import read_catalogue

def main():
    client = make_gemini_client()
    catalogue = read_catalogue()
    catalogue_reduit = {
        code: product["name"] 
        for code, product in catalogue.items()
    }
    catalogue_str = json.dumps(catalogue_reduit, ensure_ascii=False)
    test_email = """
    Bonjour,
    Je voudrais obtenir un devis pour les produits suivants :
    100 agendas, 50 stylos et 200 feuilles de papier.
    Je voulais aussi te parler de 1 règle importante que j'ai vue récemment. Elle est très utile pour les calculs de surface.
    Merci d'avance.
    """
    response = make_request(client, test_email, catalogue_str)
    print("Gemma 4: " + response)

main()