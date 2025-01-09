import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
import weaviate

def extract_and_split_pdf(file_path):
    pdf_document = fitz.open(file_path)
    full_text = ""
    for page in pdf_document:
        full_text += page.get_text()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = splitter.split_text(full_text)
    return text_chunks

def store_in_weaviate(text_chunks, weaviate_url):
    client = weaviate.Client(weaviate_url)
    for i, chunk in enumerate(text_chunks):
        client.data_object.create(
            {
                "content": chunk,
                "metadata": {"section": f"Раздел {i + 1}"}
            },
            "DocumentChunk"
        )
    print("Данные успешно сохранены в Weaviate.")
