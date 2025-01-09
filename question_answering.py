import openai
import weaviate
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain import __version__ as langchain_version
from pdf2image import convert_from_path
import pytesseract

# OpenAI API-Schlüssel
openai.api_key = "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"

# Функция для логирования ошибок
def fehler_protokollieren(nachricht):
    with open("errors.log", "a", encoding="utf-8") as log_datei:
        log_datei.write(nachricht + "\n")

# Подключение к Weaviate
def weaviate_client_erstellen():
    try:
        client = weaviate.Client(url="http://localhost:8080")
        if client.is_ready():
            print("Weaviate ist bereit und verbunden.")
        else:
            print("Weaviate ist nicht bereit. Überprüfen Sie die Verbindung.")
        return client
    except Exception as e:
        fehler_protokollieren(f"Fehler bei der Verbindung mit Weaviate: {e}")
        return None

# Проверка версий библиотек
def bibliotheken_versionen_pruefen():
    try:
        print(f"LangChain Version: {langchain_version}")
    except Exception as e:
        fehler_protokollieren(f"Fehler bei der Überprüfung von LangChain: {e}")

# Разделение текста на фрагменты
def text_in_abschnitte_aufteilen(text, abschnitt_groesse=200, abschnitt_ueberlappung=50):
    try:
        text_splitter = CharacterTextSplitter(chunk_size=abschnitt_groesse, chunk_overlap=abschnitt_ueberlappung)
        abschnitte = text_splitter.split_text(text)
        print(f"Текст разделён на {len(abschnitte)} фрагментов.")
        return abschnitte
    except Exception as e:
        fehler_protokollieren(f"Ошибка при разделении текста: {e}")
        return []

# Обработка PDF с извлечением текста и OCR для пустых страниц
def pdf_verarbeiten(datei_pfad):
    try:
        reader = PdfReader(datei_pfad)
        gesamter_text = ""

        # Преобразование страниц в изображения заранее для OCR
        bilder = convert_from_path(datei_pfad)

        # Обработка каждой страницы
        for i, seite in enumerate(reader.pages):
            try:
                seiten_text = seite.extract_text()
                if seiten_text and seiten_text.strip():
                    gesamter_text += seiten_text
                else:
                    print(f"Seite {i + 1}: Kein Text gefunden, OCR wird verwendet.")
                    ocr_text = pytesseract.image_to_string(bilder[i], lang="deu")
                    gesamter_text += ocr_text
            except Exception as inner_e:
                fehler_protokollieren(f"Fehler beim Verarbeiten der Seite {i + 1}: {inner_e}")
                continue

        if not gesamter_text.strip():
            print("Kein Text im Dokument. OCR hat ebenfalls nichts gefunden.")
            return []

        print(f"Extrahierter Text (первые 500 Zeichen): {gesamter_text[:500]}")
        return text_in_abschnitte_aufteilen(gesamter_text)
    except Exception as e:
        fehler_protokollieren(f"Fehler bei der Verarbeitung der PDF-Datei: {e}")
        return []

# Загрузка данных в Weaviate
def weaviate_daten_laden(client, abschnitte):
    try:
        if client.schema.contains("DocumentChunk"):
            client.schema.delete_class("DocumentChunk")
        schema = {
            "class": "DocumentChunk",
            "vectorizer": "none",
            "properties": [{"name": "content", "dataType": ["text"]}]
        }
        client.schema.create_class(schema)

        for abschnitt in abschnitte:
            embedding = openai.Embedding.create(
                input=abschnitt,
                model="text-embedding-ada-002"
            )["data"][0]["embedding"]
            client.data_object.create(
                data_object={"content": abschnitt},
                class_name="DocumentChunk",
                vector=embedding
            )
        print("Daten erfolgreich in Weaviate geladen!")
    except Exception as e:
        fehler_protokollieren(f"Fehler beim Laden der Daten in Weaviate: {e}")

# Поиск ответа с использованием Weaviate и OpenAI
def antwort_finden(client, frage):
    try:
        frage_embedding = openai.Embedding.create(
            input=frage,
            model="text-embedding-ada-002"
        )["data"][0]["embedding"]

        result = client.query.get(
            class_name="DocumentChunk",
            properties=["content"]
        ).with_near_vector({"vector": frage_embedding}).with_limit(1).do()

        if result.get("data", {}).get("Get", {}).get("DocumentChunk"):
            context = result["data"]["Get"]["DocumentChunk"][0]["content"]
            print("Gefundener Kontext:", context)

            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"Beantworte die folgende Frage basierend auf dem Kontext:\n\nKontext: {context}\n\nFrage: {frage}\nAntwort:",
                max_tokens=200
            )
            print("Antwort:", response["choices"][0]["text"].strip())
        else:
            print("Kein passender Kontext gefunden.")
    except Exception as e:
        fehler_protokollieren(f"Fehler bei der Antwortsuche: {e}")

# Основная программа
if __name__ == "__main__":
    bibliotheken_versionen_pruefen()

    # Шаг 1: Обработка PDF
    datei_pfad = "C:/Users/naume/Downloads/bedienungsanleitung-hyundai-kona.pdf"
    abschnitte = pdf_verarbeiten(datei_pfad)

    # Шаг 2: Подключение и загрузка данных в Weaviate
    client = weaviate_client_erstellen()
    if client and abschnitte:
        weaviate_daten_laden(client, abschnitte)

        # Шаг 3: Запрос и получение ответа
        frage = "Wie starte ich den Hyundai Kona?"
        antwort_finden(client, frage)
