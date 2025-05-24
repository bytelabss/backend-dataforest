import redis

# Cria a conexão uma única vez
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
