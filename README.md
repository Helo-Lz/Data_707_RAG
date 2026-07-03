# Projet RAG

Environnement RAG local avec Ollama (LLM + Embedding) et PostgreSQL/pgvector.

## Prérequis

- Docker + Docker Compose
- Python 3.13+
- uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Premier lancement

```bash
# 1. Se placer dans le projet
cd ~/Nom_Du_Repertoire

# 2. Créer l'environnement Python et installer les dépendances
uv sync

# 3. Lancer l'environnement complet
chmod +x start.sh
./start.sh
```

> `start.sh` permet de démarrer les conteneurs. Il attend que les modèles soient prêts, puis
> ingère les données et lance l'interface RAG interactive.
> À noter que le téléchargement des modèles (~2GB) peut prendre environ 30 minutes lors de la première exécution.

## Lancements (post installation et premier lancement)

```bash
cd ~/Nom_Du_Repertoire
./start.sh
```

## Arrêt

```bash
docker compose down
```

> Les données (modèles Ollama + base vectorielle) sont conservées entre les arrêts grâce aux volumes Docker.


## Structure du projet

```
Nom_Du_Repertoire/
├── docker-compose.yml   # Ollama + pgvector
├── start.sh             # Point d'entrée unique
├── pyproject.toml       # Dépendances Python (uv)
├── scripts/
│   ├── ingest.py        # Ingestion du dataset dans pgvector
│   └── query.py         # Interface RAG interactive
└── .venv/               # Environnement Python (généré par uv sync)
```

## Services existants dans l'environnement

| Service  | URL / Port             | Rôle                                             |
|----------|------------------------|--------------------------------------------------|
| Ollama   | http://localhost:11434 | LLM (llama3.2:3b) + Embedding (nomic-embed-text) |
| pgvector | localhost:5432         | Base de connaissances vectorielle                |