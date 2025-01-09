import requests

def create_schema():
    # URL des Weaviate-Servers
    url = "http://localhost:8080/v1/schema"

    # Schema
    schema = {
        "class": "PDFChunks",  # Имя класса должно совпадать с add_data
        "description": "Textabschnitte aus einem PDF-Dokument",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "chunk_id", "dataType": ["string"]}
        ]
    }

    # Anfrage zum Erstellen des Schemas senden
    response = requests.post(url, json={"classes": [schema]})  # "classes" muss ein Array sein
    if response.status_code == 200:
        print("Schema erfolgreich erstellt!")
    else:
        print(f"Fehler beim Erstellen des Schemas: {response.text}")


def add_data():
    # URL zum Hinzufügen von Daten
    url = "http://localhost:8080/v1/objects"

    # Daten zum Hinzufügen
    data_objects = [
        {"class": "PDFChunks", "properties": {"text": "Dies ist der erste Abschnitt.", "chunk_id": "1"}},
        {"class": "PDFChunks", "properties": {"text": "Dies ist der zweite Abschnitt.", "chunk_id": "2"}}
    ]

    # Objekte einzeln hinzufügen
    for obj in data_objects:
        response = requests.post(url, json=obj)
        if response.status_code == 200:
            print(f"Objekt {obj['properties']['chunk_id']} erfolgreich hinzugefügt!")
        else:
            print(f"Fehler beim Hinzufügen des Objekts {obj['properties']['chunk_id']}: {response.text}")


if __name__ == "__main__":
    create_schema()
    add_data()
