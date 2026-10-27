import os
from dotenv import load_dotenv

from src.constants.file import PROJECT_ROOT

REQUIRED_KEYS = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]

def load_env() -> dict[str, str]:         
    dotenv_path = os.path.join(PROJECT_ROOT, '.env')
    
    if os.path.exists(dotenv_path):
        try:
            load_dotenv(str(dotenv_path))
            env = dict()
            for key in REQUIRED_KEYS:
                if not os.environ.get(key):
                    raise ValueError(f"La variable d'environnement {key} n'est pas définie dans le fichier .env")
                else:
                    env.update({key : os.environ.get(key)})
            
            return env
        except Exception as e:
            raise e
    else:
        raise FileNotFoundError(f"Le fichier .env n'a pas été trouvé dans {str(dotenv_path)}")
    