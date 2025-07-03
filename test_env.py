from decouple import Config, RepositoryEnv

# Força carregar o .env desse caminho específico
config = Config(RepositoryEnv(r"C:\Users\SEAOps\Documents\pat\.env"))

print("DATABASE_URL =", config('DATABASE_URL'))

