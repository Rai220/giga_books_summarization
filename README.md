# GigaChat Book Summarizer

Простое консольное приложение на Python для суммаризации книг с использованием модели GigaChat. Поддерживает разные конфигурации суммаризации и позволяет сравнивать результаты с помощью GPT-4.

## Настройка

Перед началом работы убедитесь, что у вас установлен Python версии 3.6 или выше.

1. Клонируйте репозиторий на ваш локальный компьютер
2. Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```
3. Настройте переменные окружения для указания параметров доступа к GigaChat и OpenAI, или создайте файл `config.json` в корневой директории проекта со следующей структурой:
```json
{
    "user": "your_gigachat_user",
    "password": "your_gigachat_password",
    "base_url": "gigachat_base_url",
    "openai_api_key": "your_openai_api_key"
}
```
Если переменные окружения не заданы, приложение автоматически загрузит настройки из config.json.


markdown
Copy code
# GigaChat Book Summarizer

Простое консольное приложение на Python для суммаризации книг с использованием модели GigaChat. Поддерживает разные конфигурации суммаризации и позволяет сравнивать результаты с помощью GPT-4.

## Настройка

Перед началом работы убедитесь, что у вас установлен Python версии 3.6 или выше.

1. Клонируйте репозиторий на ваш локальный компьютер:
git clone https://your-repository-link.git

markdown
Copy code

2. Установите необходимые зависимости:
pip install -r requirements.txt

arduino
Copy code

3. Настройте переменные окружения для указания параметров доступа к GigaChat и OpenAI, или создайте файл `config.json` в корневой директории проекта со следующей структурой:
```json
{
    "user": "your_gigachat_user",
    "password": "your_gigachat_password",
    "base_url": "gigachat_base_url",
    "openai_api_key": "your_openai_api_key"
}
Если переменные окружения не заданы, приложение автоматически загрузит настройки из config.json.

## Запуск приложения
Для суммаризации книги используйте следующую команду, заменив path_to_your_book на путь к файлу книги в формате .epub и configuration_key на ключ одной из предустановленных конфигураций (plus_basic, plus_detailed, plus_quick), или all для выполнения всех конфигураций:

```python
python gigachat_book_summarizer.py path_to_your_book configuration_key
```

Пример запуска для одной конфигурации:
```python
python gigachat_book_summarizer.py mybook.epub plus_basic
```

Пример запуска для всех конфигураций:
```python
python gigachat_book_summarizer.py mybook.epub all
```

После выполнения суммаризации результаты будут сохранены в файлы в текущей директории.

## Сравнение результатов суммаризации
Для сравнения результатов суммаризации запустите функцию сравнения, указав пути к файлам с результатами:

```python
python compare_summaries.py summary_file1.txt summary_file2.txt summary_file3.txt
```

Это вызовет GPT-4 для оценки и выбора лучшего варианта суммаризации.