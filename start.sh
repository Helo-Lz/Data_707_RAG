#!/bin/bash
set -e

echo "1/5 Démarrage des conteneurs"
docker compose up -d

echo "2/5 Attente que pgvector soit prêt"
until docker exec pgvector pg_isready -U raguser -d ragdb > /dev/null 2>&1; do
  echo "  pgvector en cours de démarrage..."
  sleep 2
done

echo "3/5 Attente des modèles Ollama"
until docker exec ollama ollama list | grep -q "nomic-embed-text" && \
      docker exec ollama ollama list | grep -q "llama3.2"; do
  echo "  Téléchargement des modèles en cours..."
  sleep 5
done
echo "  Modèles prêts."

echo "4/5 Ingestion des données"
source .venv/bin/activate
python scripts/ingest.py

echo "5/5 Lancement du mode RAG"
python scripts/query.py