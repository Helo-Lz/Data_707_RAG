import os
from datasets import load_dataset
from tqdm import tqdm
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
import psycopg2

# Vérification de l'existence de la collection - pour ne pas le
# traiter à chaque exécution

conn = psycopg2.connect("postgresql://raguser:ragpassword@localhost:5432/ragdb")
cur = conn.cursor()
try:
    cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"Base déjà peuplée ({count} documents). Ingestion ignorée.")
        conn.close()
        exit(0)
except psycopg2.errors.UndefinedTable:
    pass
finally:
    conn.close()

# Configuration de l'ingestion
OLLAMA_URL      = "http://localhost:11434"
EMBED_MODEL     = "nomic-embed-text"
PG_CONNECTION   = "postgresql+psycopg2://raguser:ragpassword@localhost:5432/ragdb"
COLLECTION_NAME = "rag_dataset"
MAX_DOCS        = 500   # Limite du nombre des documents pour les tests

# Chargement du dataset
print("Chargement du dataset...")
ds = load_dataset("neural-bridge/rag-dataset-12000", split="train")
ds = ds.select(range(min(MAX_DOCS, len(ds))))

# Transformation en document langchain
print("Préparation des documents...")
documents = []
for row in tqdm(ds):
    content = f"Context: {row['context']}\nQuestion: {row['question']}\nAnswer: {row['answer']}"
    doc = Document(
        page_content=content,
        metadata={"question": row["question"], "answer": row["answer"]}
    )
    documents.append(doc)

# Initilisation du modèle d'embedding via Ollama
print("Initialisation du modèle d'embedding...")
embeddings = OllamaEmbeddings(
    model=EMBED_MODEL, # le modèle d'embedding à utiliser
    base_url=OLLAMA_URL # l'URL de l'API Ollama
)

# Stockage dans pgvector la base de données PostgreSQL
print("Stockage des vecteurs dans PostgreSQL...")
vector_store = PGVector.from_documents(
    documents=documents, # le document à stocker
    embedding=embeddings, # le modèle d'embedding à utiliser
    collection_name=COLLECTION_NAME,
    connection=PG_CONNECTION,
    pre_delete_collection=True   # Repart de zéro à chaque exécution
)

print(f"\nIngestion terminée : {len(documents)} documents stockés.")