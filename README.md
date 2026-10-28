# QuoteFlow

QuoteFlow transforme une demande de prix au format CSV en soumission PDF, puis l'envoie par courriel. Le projet est un prototype en ligne de commande qui valide le flux métier avant le développement d'une interface graphique ou Web.

## Fonctionnalités

- Lecture d'un catalogue de produits et d'une demande au format CSV.
- Vérification des en-têtes, des fichiers non vides et des codes en double.
- Calcul du sous-total, de la TPS (5 %) et de la TVQ (9,975 %).
- Saisie et confirmation des coordonnées du client dans le terminal.
- Affichage du résumé, génération d'un PDF et envoi en pièce jointe par SMTP SSL.
- Tests unitaires pour la lecture CSV et les calculs de soumission.

## Future fonctionnalité
- Intégration avec un LLM pour détecter et construire un CSV à partir des demandes reçues depuis une boite courriel

## Prérequis

- Python 3.10 ou plus récent.
- Un compte courriel et ses paramètres SMTP si tu veux tester l'envoi réel.

## Installation

Depuis la racine du dépôt, crée et active un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate
```

Dans PowerShell, l'activation se fait avec :

```powershell
.venv\Scripts\Activate.ps1
```

Installe ensuite les dépendances :

```bash
python -m pip install -r requirements.txt
```

## Configuration du courriel

Copie le fichier d'exemple et renseigne les paramètres de votre fournisseur SMTP :

```bash
cp .env.example .env
```

Sous PowerShell :

```powershell
Copy-Item .env.example .env
```

Variables requises dans `.env` :

| Variable | Description |
| --- | --- |
| `SMTP_HOST` | Adresse du serveur SMTP, par exemple `smtp.gmail.com` |
| `SMTP_PORT` | Port SMTP avec SSL, souvent `465` |
| `SMTP_USERNAME` | Adresse courriel utilisée pour l'authentification et l'envoi |
| `SMTP_PASSWORD` | Mot de passe ou mot de passe d'application SMTP |

Le programme envoie le PDF à l'adresse saisie pendant l'exécution. Il utilise un envoi SMTP réel : pour une démonstration, veuillez privilégier une boîte de test ou un compte que vous contrôlez. Ne partagez jamais le fichier `.env` et ne le poussez pas dans Git.

## Données d'entrée

Les fichiers utilisés par défaut sont `data/catalogue.csv` et `data/demande.csv`. Ils doivent avoir exactement les en-têtes suivants :

`data/catalogue.csv` :

```csv
code,name,price
P001,Cahier grand format,3.49
P002,Stylo bleu,1.25
```

`data/demande.csv` :

```csv
code,quantity
P001,2
P002,5
```

Chaque code de produit de la demande doit exister dans le catalogue. Les fichiers d'exemple du dépôt contiennent une demande et un catalogue prêts à utiliser.

## Lancer l'application

À la racine du projet, avec l'environnement virtuel activé :

```bash
python -m src.main
```

Le programme demande le nom et le courriel du client, puis affiche un résumé à confirmer. Appuyez sur Entrée pour générer le PDF, puis de nouveau sur Entrée pour l'envoyer. Le fichier produit est enregistré sous `data/submission.pdf`. `Ctrl+C` annule proprement l'exécution.

## Tests

```bash
python -m unittest discover -s tests -p 't_*.py'
```

## Organisation du projet

```text
src/
	main.py                 Orchestration de la création d'une soumission
	models.py               Produits, lignes et calculs de soumission
	utils/
		csv_reader.py         Lecture et validation des fichiers CSV
		pdf_writer.py         Génération du PDF avec ReportLab
		mail_sender.py        Envoi du PDF par SMTP SSL
		load_env.py           Chargement de la configuration depuis .env
data/
	catalogue.csv           Catalogue d'exemple
	demande.csv             Demande d'exemple
tests/                    Tests unitaires
```

## Limites actuelles

- L'application est une CLI : elle ne comporte pas encore d'interface Web, d'API ni de base de données.
- Le catalogue et la demande sont lus depuis des chemins définis dans le code.
- Les coordonnées du client sont demandées à chaque exécution et les soumissions ne sont pas conservées dans un historique.
- La validation des données métier et la gestion des échecs d'envoi peuvent être renforcées.
- Le PDF utilise actuellement des libellés en anglais.

Ces limites permettent de garder le prototype centré sur la validation du flux principal : demande CSV, calculs, document PDF et envoi courriel.


