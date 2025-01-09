from data_preparation import extract_and_split_pdf, store_in_weaviate
from question_analysis import analyze_question
from data_search import search_in_weaviate
from answer_generation import generate_answer
import config

def main():
    pdf_path = "example.pdf"
    weaviate_url = config.WEAVIATE_URL

    # Подготовка данных
    text_chunks = extract_and_split_pdf(pdf_path)
    store_in_weaviate(text_chunks, weaviate_url)

    # Вопросы пользователя
    while True:
        question = input("Введите ваш вопрос (или 'exit', чтобы выйти): ")
        if question.lower() == "exit":
            print("Программа завершена.")
            break

        # Анализ вопроса
        keywords = analyze_question(question)

        # Поиск данных
        results = search_in_weaviate(keywords, weaviate_url)

        # Генерация ответа
        relevant_texts = "\n".join([res["content"] for res in results])
        answer = generate_answer(relevant_texts, question)

        # Вывод ответа
        print(f"Ответ: {answer}")

if __name__ == "__main__":
    main()
