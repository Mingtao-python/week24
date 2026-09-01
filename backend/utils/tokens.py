import secrets

tokens = {}  # token → user_id

def generate_token(user_id: int):
    token = secrets.token_hex(16)
    tokens[token] = user_id
    return token

def get_user_from_token(token: str):
    return tokens.get(token)
