from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate

# variables d'environnement
OLLAMA_URL      = "http://localhost:11434" # URL de l'API Ollama
EMBED_MODEL     = "nomic-embed-text" # le modèle d'embedding à utiliser
LLM_MODEL       = "llama3.2:3b" # le modèle LLM à utiliser
PG_CONNECTION   = "postgresql+psycopg2://raguser:ragpassword@localhost:5432/ragdb" # connexion à la base de données PostgreSQL
COLLECTION_NAME = "rag_dataset" # le nom de la collection pgvector à utiliser
TOP_K           = 3   # le nmbre de documents récupérés

# Initialisation des objets d'embedding et LLM via Ollama
embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL)
llm        = OllamaLLM(model=LLM_MODEL, base_url=OLLAMA_URL)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=PG_CONNECTION,
)

# Template de prompt RAG
# Basée sur la documentation officielle du dataset
template = PromptTemplate.from_template("""
You are a precise assistant. Answer the question based ONLY 
on the context provided below. If the answer is not in the context, 
say so clearly.

Context :
{context}

Question : {question}

Réponse :
""")

# Fonction de requête RAG
def ask_with_rag(question: str) -> dict:
    # 1/3 recherche de similarité dans pgvector
    docs = vector_store.similarity_search(question, k=TOP_K)
    
    # Affichage des documents sources récupérés
    print(f"\n[Documents récupérés depuis pgvector ({len(docs)})]")
    for i, doc in enumerate(docs):
        print(f"\n  ── Source #{i+1} ──")
        print(f"  Question source : {doc.metadata.get('question', 'N/A')}")
        print(f"  Réponse source  : {doc.metadata.get('answer', 'N/A')[:150]}...")

    context = "\n\n---\n\n".join([d.page_content for d in docs])

    # 2/3 construction du prompt enrichi
    prompt = template.format(context=context, question=question)

    # 3/3 appel au LLM
    answer = llm.invoke(prompt)
    return {"question": question, "context": context, "answer": answer}

def ask_without_rag(question: str) -> str:
    """LLM seul, sans contexte RAG — pour comparaison."""
    return llm.invoke(question)

# ── Interface interactive ──────────────────────────────────────
if __name__ == "__main__":
    print("=== Mode RAG interactif (Ctrl+C pour quitter) ===\n")
    while True:
        question = input("Votre question : ").strip()
        if not question:
            continue

        print("\n[Sans RAG]")
        print(ask_without_rag(question))

        print("\n[Avec RAG]")
        result = ask_with_rag(question)
        print(result["answer"])
        print("-" * 60)