import os
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from secrets import HTTPS_PROXY, OPENAI_API_KEY


async def get_openai_response(question: str):
    os.environ["HTTP_PROXY"] = HTTPS_PROXY
    os.environ["HTTPS_PROXY"] = HTTPS_PROXY

    # Установите ваш ключ OpenAI API
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    # Загрузите документы
    documents = SimpleDirectoryReader("data").load_data()

    # Создайте индекс
    index = VectorStoreIndex.from_documents(documents)

    # Создайте движок запросов
    query_engine = index.as_query_engine()

    print(f"Начинаю думать над вопросом {question}")
    # Сделайте запрос
    response = query_engine.query(question)
    print(f"Закончил думать над вопросом {question}")
    print(response)
    return response.response
