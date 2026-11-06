# QuoteFlow

QuoteFlow transforme les demandes de prix reçues par Gmail en soumissions PDF. L'application repère les courriels susceptibles de contenir une demande, utilise Gemma 4 pour associer les produits du catalogue et leurs quantités, calcule les taxes, puis envoie ou met en attente le PDF.

## Fonctionnement

1. QuoteFlow lit `data/catalogue.csv` et recherche les courriels récents correspondant aux mots-clés de demande de prix et aux noms de produits du catalogue.
2. Le contenu d'un courriel repéré est envoyé à l'API Gemini, au modèle Gemma 4 configuré par le projet. Le modèle propose des codes produit et des quantités; QuoteFlow vérifie sa réponse et utilise les prix du catalogue local.
3. QuoteFlow construit la soumission, calcule le sous-total, la TPS (5 %) et la TVQ (9,975 %), puis génère un PDF dans `data/`.
4. Appuyez sur Entrée dans les 10 secondes pour envoyer le PDF immédiatement. Si le délai expire, le PDF et les informations nécessaires sont ajoutés à `data/pending_sends.txt`.
5. Pour envoyer ultérieurement les PDF en attente, lancez le programme d'envoi différé. Les entrées envoyées sont retirées de la file; les échecs y restent pour une nouvelle tentative.

Les identifiants Gmail déjà traités sont conservés dans `data/processed_ids.txt` afin de ne pas reproposer les mêmes messages. Les CSV temporaires utilisés pour lire les lignes extraites sont supprimés après traitement.

> **Important :** le programme différé envoie toutes les entrées de la file sans demander une nouvelle confirmation. N'ajoutez donc à cette file que des soumissions que vous êtes prêt à envoyer.

## Prérequis

- Python 3.12 ou plus récent (la syntaxe utilisée dans le point d'entrée requiert Python 3.12+).
- Un compte Google pour accéder à Gmail et Google AI Studio.
- Un compte d'envoi courriel et ses paramètres SMTP. Pour Gmail, utilisez un mot de passe d'application lorsque votre compte le permet; n'utilisez pas votre mot de passe Google habituel.

## Installation

Depuis la racine du dépôt, créez et activez un environnement virtuel.

Sous Windows PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
New-Item -ItemType Directory -Force tmp
```

Sous macOS/Linux :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p tmp
```

## Configurer la clé API Gemini avec Google AI Studio

La clé utilisée ici est une **clé API de Google AI Studio**. Elle est distincte de l'autorisation OAuth Gmail et des identifiants SMTP.

1. Connectez-vous à [Google AI Studio](https://aistudio.google.com/).
2. Ouvrez la page [API keys](https://aistudio.google.com/api-keys), choisissez ou créez un projet Google Cloud, puis créez une clé API.
3. Copiez la clé et gardez-la privée. Ne la publiez pas dans un dépôt Git, une capture d'écran ou un courriel.
4. À la racine du projet, copiez le modèle de configuration :

	 ```powershell
	 Copy-Item .env.example .env
	 ```

	 Sous macOS/Linux, utilisez `cp .env.example .env`.

5. Ouvrez `.env` et ajoutez une ligne avec votre clé :

	GEMINI_API_KEY=votre_cle_api_google_ai_studio

Remplacez également les valeurs SMTP d'exemple par les paramètres réels de votre compte d'envoi.

Le niveau gratuit de l'API Gemini offre l'accès à certains modèles et quotas; la disponibilité, les limites et les conditions peuvent changer. La page tarifaire Google indique actuellement Gemma 4 sans frais d'entrée et de sortie via son API. Vérifiez la [tarification en vigueur](https://ai.google.dev/gemini-api/docs/pricing) et la [disponibilité des modèles](https://ai.google.dev/gemini-api/docs/models) pour votre compte et votre région.

**Confidentialité :** selon les conditions du niveau gratuit, les données soumises peuvent être utilisées par Google pour améliorer ses produits. Évitez les courriels contenant des informations personnelles ou confidentielles lors de vos essais. Consultez les [conditions Gemini API](https://ai.google.dev/gemini-api/terms) avant un usage réel.

### Pourquoi Gemma 4?

Gemma 4 est recommandé pour ce prototype d'extraction de texte : il est instruction-tuned, prend en charge les tâches multilingues et le modèle Gemma 4 A4B est conçu pour une inférence efficace. Le code actuel utilise `gemma-4-26b-a4b-it` dans [src/utils/gemini.py](src/utils/gemini.py). La famille Gemma 4 comprend plusieurs variantes; confirmez que ce modèle précis est proposé et utilisable avec la clé et le point d'accès de votre compte dans [Google AI Studio](https://aistudio.google.com/) avant de changer la configuration. Les réponses du modèle sont toujours validées par l'application et ne doivent pas être considérées comme une décision finale sans vérification humaine.

## Configurer Gmail (lecture des demandes)

QuoteFlow utilise l'API Gmail avec une autorisation **lecture seule**. La clé Gemini ne donne pas accès à la boîte Gmail.

1. Dans la [console Google Cloud](https://console.cloud.google.com/), créez ou sélectionnez un projet et activez **Gmail API**.
2. Configurez l'écran de consentement OAuth. Si l'application est en mode test, ajoutez le compte Gmail que vous utiliserez comme utilisateur test.
3. Créez des identifiants OAuth de type **Application de bureau** et téléchargez le fichier JSON.
4. Placez-le sous le nom `data/client_secret.json`.
5. Au premier lancement, un navigateur s'ouvrira pour autoriser l'accès Gmail en lecture seule. Le jeton est ensuite conservé dans `data/gmail_oauth_token.json`.

Les identifiants et jetons Gmail sont ignorés par Git grâce à `.gitignore`. Ne les ajoutez jamais au dépôt. L'accès OAuth et la clé Gemini sont deux configurations séparées.

Consultez le [guide Gmail API pour Python](https://developers.google.com/workspace/gmail/api/quickstart/python) et la documentation [Google AI Studio sur les clés API](https://ai.google.dev/gemini-api/docs/api-key).

## Configurer l'envoi SMTP

Renseignez les paramètres SMTP dans le même fichier `.env` :

| Variable | Description |
| --- | --- |
| `SMTP_HOST` | Serveur SMTP, par exemple `smtp.gmail.com` |
| `SMTP_PORT` | Port SSL, souvent `465` |
| `SMTP_USERNAME` | Adresse qui enverra les soumissions |
| `SMTP_PASSWORD` | Mot de passe d'application ou identifiant SMTP fourni par le service |
| `GEMINI_API_KEY` | Clé API créée dans Google AI Studio |

Pour un compte Gmail, l'envoi SMTP doit être autorisé pour le compte. Activez la validation en deux étapes et créez un mot de passe d'application si cette option est disponible. Utilisez une boîte de test que vous contrôlez avant tout envoi à un client.

## Catalogue

Le catalogue lu par le traitement des courriels est `data/catalogue.csv`. Comme le dossier `data/` est ignoré par Git, après un clone, créez ce dossier et le fichier de catalogue s'ils ne sont pas déjà présents. Le fichier doit contenir exactement les colonnes suivantes :

```csv
code,name,price
P001,Cahier grand format,3.49
P002,Stylo bleu,1.25
```

Les codes sont les références fiables utilisées pour créer la soumission; les prix viennent toujours de ce catalogue, pas de la réponse du modèle. `data/demande.csv` est conservé comme exemple d'entrée du lecteur CSV, mais le flux Gmail actuel extrait les lignes du courriel.

## Lancer QuoteFlow

Depuis la racine du projet, avec l'environnement virtuel activé et `.env` configuré :

```powershell
python -m src.main
```

Le programme recherche les messages récents (jusqu'à 10 jours selon la requête définie dans le code), affiche les courriels repérés et traite les demandes une par une. Lors de la première utilisation, complétez aussi l'autorisation Google dans le navigateur.

- **Entrée dans les 10 secondes :** envoi immédiat par SMTP.
- **Aucune entrée avant le délai :** ajout du PDF à la file d'envoi différé.
- **Annulation :** `Ctrl+C` interrompt le programme.

Les PDF sont enregistrés dans `data/`. La file d'envoi différé se trouve dans `data/pending_sends.txt`.

### Envoyer la file différée

Depuis la racine du projet :

```powershell
python -m src.send_pending
```

Cette commande envoie les entrées en attente sans autre confirmation. Si un envoi échoue, l'entrée correspondante reste dans la file pour réessai. Après succès, le message Gmail associé est ajouté au suivi des messages traités.

## Tests

Les tests unitaires locaux peuvent être lancés sans appeler Gmail, Gemini ou SMTP :

```powershell
python -m unittest discover -s tests -p "t_*.py"
```

## Structure du projet

```text
src/
	main.py                 Orchestration du traitement des courriels
	send_pending.py         Envoi des PDF différés
	models.py               Produits, lignes et calculs de soumission
	utils/
		csv_reader.py         Lecture et validation du catalogue/demande CSV
		csv_maker.py          Création d'un CSV temporaire depuis les lignes extraites
		gemini.py             Appel à Gemma 4 via l'API Gemini
		gmail_check.py        OAuth Gmail, récupération et filtrage des messages
		pdf_writer.py         Génération du PDF avec ReportLab
		mail_sender.py        Envoi par SMTP SSL
		pending_sends.py      File locale des envois différés
		load_env.py           Chargement des paramètres SMTP depuis .env
data/
	catalogue.csv           Catalogue produit
	client_secret.json      Identifiants OAuth Gmail (local, non versionnés)
	gmail_oauth_token.json  Jeton Gmail (généré localement, non versionné)
	processed_ids.txt       Identifiants Gmail déjà traités
	pending_sends.txt       PDF dont l'envoi est différé
tests/                    Tests unitaires
```

## Limites et précautions

- QuoteFlow est une application en ligne de commande; elle n'a pas d'interface Web ni de base de données.
- Le filtre Gmail s'appuie sur une requête de recherche et des mots-clés issus du catalogue; il peut manquer une demande ou retenir un courriel non pertinent.
- Un LLM peut mal interpréter une quantité ou associer un produit incorrect. Vérifiez les soumissions et utilisez d'abord des courriels de test.
- L'envoi différé traite automatiquement toute la file au lancement de `src.send_pending`.
- Les quotas, le niveau gratuit et les modèles disponibles dans l'API Gemini sont déterminés par Google et peuvent évoluer.
- Ne transmettez pas de contenu client sensible à l'API sans avoir validé les conditions de confidentialité et de conservation applicables.


