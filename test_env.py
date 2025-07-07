# test_env.py
import os
from decouple import Config, RepositoryEnv

# Garante que o BASE_DIR é a pasta 'pat'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Força a leitura do arquivo .env no BASE_DIR (C:\Users\SEAOps\Documents\pat\.env)
env_path = os.path.join(BASE_DIR, '.env')
config = Config(RepositoryEnv(env_path))

try:
    db_url = config('DATABASE_URL')
    print(f"DATABASE_URL lida do .env: {db_url}")
except Exception as e:
    print(f"Erro ao ler DATABASE_URL do .env: {e}")

try:
    secret_key = config('SECRET_KEY')
    print(f"SECRET_KEY lida do .env (apenas os primeiros 10 caracteres): {secret_key[:10]}...")
except Exception as e:
    print(f"Erro ao ler SECRET_KEY do .env: {e}")