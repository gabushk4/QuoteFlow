from src.utils.gmail_check import make_gmail_client, get_recent_messages, get_message_details, find_text_body, sort_by_keywords
from src.utils.csv_reader import read_catalogue
def main() -> None:
    service = make_gmail_client()
    messages = get_recent_messages(service, days=10)

    for message in messages.get("messages", []):
        message_id = message["id"]
        payload = get_message_details(service, message_id)["payload"]
        text_body = find_text_body(payload)
        catalogue = read_catalogue()
        keywords = [keyword for product in catalogue.values() for keyword in [product["name"]]]
        
        score, found = sort_by_keywords(text_body, keywords)
        if(score > 0):
            print(f"Score: {score}, Found: {found}")

main()
