import json
import os

CHAT_FILE = "chat_history.json"

def load_chats():

    if not os.path.exists(CHAT_FILE):
        return []
    
    with open(
        CHAT_FILE,
        'r',
        encoding='utf-8'
    ) as f:
        return json.load(f)
    
def save_chats(conversations):

    with open(
        CHAT_FILE,
        'w',
        encoding='utf-8'
    )as f:
        json.dump(
            conversations,
            f,
            ensure_ascii = False,
            indent = 4
        )




