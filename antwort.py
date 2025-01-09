from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import Weaviate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
import weaviate

YOUR_OPENAI_KEY = "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"
YOUR_WEAVIATE_KEY = "F9IhpZlUe3N6k34M0PMB8KhkK69pSHe3BxWj"
YOUR_WEAVIATE_CLUSTER = "https://pjhpx3t1semfwqokvkvada.c0.europe-west3.gcp.weaviate.cloud"


# 1. Data Reading
loader = PyPDFLoader("C:/Users/naume/Downloads/bedienungsanleitung-hyundai-kona.pdf")
data = loader.load()

print(f"Sie haben {len(data)} Dokument(e) in Ihren Daten.")
print(f"Das erste Dokument enthält {len(data[0].page_content)} Zeichen.")


# 2. Text Splitting

text_splitter = RecursiveCharacterTextSplitter(
    chunk_overlap=0,
    chunk_size=1000
)
docs = text_splitter.split_documents(data)

# 3. Embedding Conversion
embeddings = OpenAIEmbeddings(openai_api_key=YOUR_OPENAI_KEY)

# Authentifizierung mit Weaviate (API-Key)
auth_config = weaviate.AuthApiKey(api_key=YOUR_WEAVIATE_KEY)

# Client mit Weaviate-Instanz verbinden
client = weaviate.Client(
    url=YOUR_WEAVIATE_CLUSTER,
    auth_client_secret=auth_config,
    additional_headers={"X-OpenAI-Api-Key": YOUR_OPENAI_KEY}
)

client.schema.delete_all()
# Existierendes Schema löschen (внимание: удалит все данные!)
client.schema.delete_all()

# Neues Schema erstellen
schema = {
    "classes": [
        {
            "class": "Chatbot",
            "description": "Dokumente für den Chatbot",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "type": "text"
                }
            },
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Der Inhalt des Abschnitts",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    },
                },
            ],
        },
    ]
}
client.schema.create(schema)


# Wir verwenden den Weaviate-VectorStore aus langchain_community
# und speichern dort unsere Texte (Chunks).
vectorstore = Weaviate(
    client,                # Weaviate-Client
    "Chatbot",            # Name der Klasse im Schema
    "content",            # Feldname, aus dem Vektor generiert wird
    attributes=["source"] # Metadaten, die wir speichern wollen
)

# Die Daten (Inhalt + Metadaten) in Weaviate hochladen
text_meta_pair = [(doc.page_content, doc.metadata) for doc in docs]
texts, meta = list(zip(*text_meta_pair))
vectorstore.add_texts(texts, meta)


# 5. Similarity Search
query = "who founded openai?"
similar_docs = vectorstore.similarity_search(query, k=4)

chain = load_qa_chain(
    OpenAI(openai_api_key=YOUR_OPENAI_KEY, temperature=0),
    chain_type="stuff"
)

# Wir übergeben die Dokumente (similar_docs) und die Frage (query),
# um eine zusammenfassende Antwort zu erhalten.
antwort = chain.run(input_documents=similar_docs, question=query)

print("Ergebnis: ", antwort)