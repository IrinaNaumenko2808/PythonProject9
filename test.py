import openai
from langchain import __version__ as langchain_version
import weaviate
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter

# OpenAI API-Schlüssel
openai.api_key = "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"

# Fehlerprotokollierung
def fehler_protokollieren(nachricht):
    with open("errors.log", "a", encoding="utf-8") as log_datei:
        log_datei.write(nachricht + "\n")

# Überprüfung der installierten Bibliotheken
def bibliotheken_versionen_pruefen():
    try:
        print(f"LangChain Version: {langchain_version}")
    except Exception as e:
        fehler_protokollieren(f"Fehler bei der Überprüfung von LangChain: {e}")

    try:
        print("Weaviate-Client funktioniert:", weaviate.__version__)
    except Exception as e:
        fehler_protokollieren(f"Fehler bei der Überprüfung von Weaviate: {e}")

# Funktion zum Aufteilen des Textes in Abschnitte
def text_in_abschnitte_aufteilen(text, abschnitt_groesse=500, abschnitt_ueberlappung=50):
    try:
        text_splitter = CharacterTextSplitter(chunk_size=abschnitt_groesse, chunk_overlap=abschnitt_ueberlappung)
        return text_splitter.split_text(text)
    except Exception as e:
        fehler_protokollieren(f"Fehler beim Aufteilen des Textes: {e}")
        return []

# Verarbeitung der PDF-Datei
def pdf_verarbeiten(datei_pfad):
    try:
        reader = PdfReader(datei_pfad)
        gesamter_text = ""

        # Extraktion des Textes von allen Seiten
        for seite in reader.pages:
            gesamter_text += seite.extract_text()

        # Aufteilen des Textes in Abschnitte
        abschnitte = text_in_abschnitte_aufteilen(gesamter_text)
        print(f"Der Text wurde in {len(abschnitte)} Abschnitte aufgeteilt.")

        # Anzeige der ersten Abschnitte zur Überprüfung
        for i, abschnitt in enumerate(abschnitte[:5]):
            print(f"Abschnitt {i + 1}: {abschnitt}\n")

    except FileNotFoundError:
        fehler_protokollieren(f"Die Datei {datei_pfad} wurde nicht gefunden.")
    except Exception as e:
        fehler_protokollieren(f"Fehler bei der Verarbeitung der PDF-Datei {datei_pfad}: {e}")

# Ausführung des Programms
if __name__ == "__main__":
    bibliotheken_versionen_pruefen()
    pdf_verarbeiten("C:/Users/naume/Downloads/bedienungsanleitung-hyundai-kona.pdf")




