from pathlib import Path
from smtplib import SMTP, SMTP_SSL
from email.message import EmailMessage
from src.constants.env_keys import keys

from src.utils.load_env import load_env 

def send_pdf(pdf_path: Path, to) -> None:
    """Send a pdf file to a given email address.
        Embeds a generic object and body in the email.
    """
    env = load_env()
    recipient = to if to is not None else env[keys.SMTP_USERNAME]
    msg = EmailMessage()
    msg["From"] = env[keys.SMTP_USERNAME]
    msg["To"] = recipient
    msg["Subject"] = "Soumission QuoteFlow"
    msg.set_content("Bonjour,\n\nVoici votre soumission de quote.\n\nCordialement,\nQuoteFlow")
    msg.add_attachment(
        pdf_path.read_bytes(), 
        maintype="application", 
        subtype="pdf", 
        filename=pdf_path.name
    )
    with SMTP_SSL(env[keys.SMTP_HOST], int(env[keys.SMTP_PORT])) as smtp:
        try:            
            smtp.login(env[keys.SMTP_USERNAME], env[keys.SMTP_PASSWORD])                  
            smtp.send_message(msg)
            print("Email sent successfully")            
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
        finally:
            smtp.quit()
    
    