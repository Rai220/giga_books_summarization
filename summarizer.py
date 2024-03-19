"""GigaChat books summarizer"""

import argparse
import os
from langchain.prompts import load_prompt
from langchain.chains.summarize import load_summarize_chain
from langchain_community.chat_models.gigachat import GigaChat
from langchain_community.document_loaders import UnstructuredEPubLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
import json

# Чтение конфигурации из файла, если файл существует
if os.path.exists("config.json"):
    with open("config.json", 'r') as file:
        config = json.load(file)
else:
    config = {}

# Замена значений конфигурации значениями из переменных окружения, если они установлены
GIGACHAT_USER = os.getenv('GIGACHAT_USER', config.get('GIGACHAT_USER', ''))
GIGACHAT_PASSWORD = os.getenv('GIGACHAT_PASSWORD', config.get('GIGACHAT_PASSWORD', ''))
GIGACHAT_BASE_URL = os.getenv('GIGACHAT_BASE_URL', config.get('GIGACHAT_BASE_URL', "https://beta.saluteai.sberdevices.ru/v1"))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', config.get('OPENAI_API_KEY', ''))


# Предустановленные конфигурации
CONFIGURATIONS = {
    "plus_basic": {
        "model_name": "GigaChat-Plus",
        "max_tokens": 10000,
        "chunk_size": 100000,
        "chunk_overlap": 5000,
        "map_size": "пять предложений",
        "reduce_size": "одна страница",
    },
    "plus_detailed": {
        "model_name": "GigaChat-Plus",
        "max_tokens": 10000,
        "chunk_size": 100000,
        "chunk_overlap": 5000,
        "map_size": "три страницы",
        "reduce_size": "три страницы",
    },
    "plus_quick": {
        "model_name": "GigaChat-Plus",
        "max_tokens": 10000,
        "chunk_size": 100000,
        "chunk_overlap": 5000,
        "map_size": "три предложения",
        "reduce_size": "пять предложений",
    },
    "pro_basic": {
        "model_name": "GigaChat-Pro",
        "max_tokens": 2000,
        "chunk_size": 20000,
        "chunk_overlap": 1000,
        "map_size": "три предложения",
        "reduce_size": "одна страница",
    },
    "pro_detailed": {
        "model_name": "GigaChat-Pro",
        "max_tokens": 2000,
        "chunk_size": 20000,
        "chunk_overlap": 1000,
        "map_size": "три предложения",
        "reduce_size": "три абзаца",
    },
    "pro_quick": {
        "model_name": "GigaChat-Pro",
        "max_tokens": 2000,
        "chunk_size": 20000,
        "chunk_overlap": 1000,
        "map_size": "одно предложение",
        "reduce_size": "три предложения",
    },
}


def load_epub(book_path):
    loader = UnstructuredEPubLoader(book_path)
    return loader.load()


def summarize_text(data, model, map_size, reduce_size, chunk_size, chunk_overlap):
    book_map_prompt = load_prompt(
        "lc://prompts/summarize/map_reduce/summarize_book_map.yaml"
    )
    book_combine_prompt = load_prompt(
        "lc://prompts/summarize/map_reduce/summarize_book_combine.yaml"
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    documents = text_splitter.split_documents(data)
    print(f"Количество частей книги: {len(documents)}")

    chain = load_summarize_chain(
        model,
        chain_type="map_reduce",
        map_prompt=book_map_prompt,
        combine_prompt=book_combine_prompt,
        verbose=False,
    )

    res = chain.invoke(
        {"input_documents": documents, "map_size": map_size, "reduce_size": reduce_size}
    )
    return res["output_text"].replace(". ", ".\n")

def compare_summaries(summary_files):
    """Сравнивает суммаризации и возвращает имя лучшего файла."""
    prompt = """Ты профессиональный редактор текстов и литератор. Я дам тебе несколько разных кратких содержаний книги.
Твоя задача - выбрать самый лучший и удачный вариант и написать мне название файла из которого он был взят.
"""
    for file in summary_files:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            prompt += f"\n\nФайл: {file}:\n{text}\n\n"
    prompt += "Теперь верни только название файла, который кажется тебе самым лучшим. Объясни почему"
    model = ChatOpenAI(model="gpt-4", api_key=OPENAI_API_KEY)
    output_parser = StrOutputParser()

    chain = ChatPromptTemplate.from_template(prompt) | model | output_parser
    res = chain.invoke({"topic": "ice cream"})
    print("Ответ GPT-4: ", res)
    return res


def run_all_configurations(book_path):
    """Выполняет суммаризацию для всех конфигураций и сравнивает результаты."""
    summary_files = []
    for config_key in CONFIGURATIONS:
        print(f"Выполняется суммаризация для конфигурации: {config_key}")
        summary_file = main(book_path, config_key)
        summary_files.append(summary_file)
    
    print("Сравнение результатов суммаризации...")
    best_summary_file = compare_summaries(summary_files)
    print(f"Лучший результат суммаризации: {best_summary_file}")

def main(book_path, config_key):
    # Изменения для поддержки пакетного режима
    if config_key == "all":
        run_all_configurations(book_path)
        return
    
    config = CONFIGURATIONS[config_key]

    book_content = load_epub(book_path)
    book_name = os.path.splitext(os.path.basename(book_path))[0]
    summary_file_name = f"{book_name}_summary_{config_key}.txt"
    # Проверка существования файла с результатом
    if os.path.exists(summary_file_name):
        print(f"Файл {summary_file_name} уже существует, пропускаем суммаризацию.")
        return summary_file_name

    model = GigaChat(
        profanity_check=False,
        verbose=False,
        verify_ssl_certs=False,
        user=GIGACHAT_USER,
        password=GIGACHAT_PASSWORD,
        model=config["model_name"],
        base_url=GIGACHAT_BASE_URL,
        timeout=6000,
        max_tokens=config["max_tokens"],
        streaming=True,
    )

    summarized_content = summarize_text(
        book_content, model, config["map_size"], config["reduce_size"], config["chunk_size"], config["chunk_overlap"]
    )

    with open(summary_file_name, "w", encoding="utf-8") as f:
        f.write(summarized_content)

    print(f"Суммаризированный текст книги сохранен в файл: {summary_file_name}")
    return summary_file_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Консольное приложение для суммаризации книг с использованием предустановленных конфигураций"
    )
    parser.add_argument("book_path", type=str, help="Путь к файлу книги")
    parser.add_argument(
        "config_key",
        choices=list(CONFIGURATIONS.keys()) + ["all"],
        help="Ключ конфигурации для суммаризации (например, basic, detailed, quick) или 'all' для выполнения всех.",
    )

    args = parser.parse_args()

    main(args.book_path, args.config_key)
