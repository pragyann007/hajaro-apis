

def refresh_token_redis_key(token:str):

    return f"refresh_token:{token}"